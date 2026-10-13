#!/usr/bin/env python3
"""Portable offline DOM verifier: submission + static files -> JSON + evidence.

No Harbor imports. Exit 0 means a scored agent outcome (including failure).
Exit 2 means verifier infrastructure failed; deliberately emit no reward.json.
Run against generated code inside an isolated, credential-free container.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
from pathlib import Path
from urllib.parse import quote, urlsplit

VERSION = "0.2.0"
MAX_FILES = 200
MAX_BUNDLE_BYTES = 20 * 1024 * 1024
REWARD_NAMES = ("artifact_contract", "runtime_smoke", "gameplay_interaction", "overall")
OUTPUT_NAMES = (
    "reward.json",
    "reward.txt",
    "details.json",
    "actions.json",
    "ctrf.json",
    "trace.zip",
    "bundle",
)


class SubmissionFailure(Exception):
    """The agent did not supply the artifact required by the task."""


class GameFailure(Exception):
    """An observed game behavior failed an assertion."""


class InfrastructureFailure(Exception):
    """The verifier cannot produce a valid measurement."""


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_submission(path: Path, game_root: Path) -> tuple[dict, Path | None]:
    try:
        if path.stat().st_size > 64 * 1024:
            raise SubmissionFailure("submission.json exceeds 64 KiB")
        submission = json.loads(path.read_text())
    except (OSError, UnicodeError, ValueError) as error:
        raise SubmissionFailure(f"Cannot read submission.json: {error}") from error
    if not isinstance(submission, dict) or submission.get("schema_version") != "0.1":
        raise SubmissionFailure("Expected an object with schema_version='0.1'")

    kind = submission.get("kind")
    if kind == "build_failure":
        failure, producer = submission.get("failure"), submission.get("producer")
        if not isinstance(failure, dict) or not isinstance(failure.get("message"), str):
            raise SubmissionFailure("build_failure requires a string failure.message")
        if not failure["message"].strip():
            raise SubmissionFailure("build_failure requires a non-empty failure.message")
        if not isinstance(producer, dict) or producer.get("status") != "failed":
            raise SubmissionFailure("build_failure requires producer.status='failed'")
        return submission, None

    if kind != "local_directory":
        raise SubmissionFailure(
            "v0.2 requires local_directory; remote URLs are not offline artifacts"
        )
    entrypoint = submission.get("entrypoint")
    if not isinstance(entrypoint, str) or not Path(entrypoint).is_absolute():
        raise SubmissionFailure("entrypoint must be an absolute file path")
    dist = game_root.resolve() / "dist"
    # Reject symbolic links instead of copying files outside the submitted tree.
    if dist.is_symlink() or not dist.is_dir():
        raise SubmissionFailure("Expected a regular dist directory below game_root")
    try:
        entry = Path(entrypoint).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise SubmissionFailure(f"Cannot resolve entrypoint: {error}") from error
    if not entry.is_relative_to(dist) or not entry.is_file():
        raise SubmissionFailure("entrypoint must be a file inside game_root/dist")
    if entry.suffix.lower() not in {".html", ".htm"}:
        raise SubmissionFailure("entrypoint must be HTML")
    return submission, entry


def freeze_bundle(dist: Path, destination: Path) -> list[dict]:
    """Snapshot regular files once, retaining hashes for replay/provenance."""
    manifest: list[dict] = []
    total = 0
    destination.mkdir()
    for source in sorted(dist.rglob("*")):
        if source.is_symlink():
            raise SubmissionFailure("Static bundles must not contain symbolic links")
        if source.is_dir():
            continue
        if not source.is_file():
            raise SubmissionFailure("Static bundles must contain regular files only")
        size = source.stat().st_size
        total += size
        if len(manifest) >= MAX_FILES or total > MAX_BUNDLE_BYTES:
            raise SubmissionFailure("Static bundle exceeds 200 files or 20 MiB")
        relative = source.relative_to(dist)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest.append({"path": relative.as_posix(), "bytes": size, "sha256": digest(target)})
    return manifest


def load_rubric(path: Path) -> dict:
    rubric = json.loads(path.read_text())
    if rubric["mode"] != "dom-click-counter" or rubric["verifier_version"] != VERSION:
        raise ValueError("Unsupported rubric mode/version")
    for key in ("score_selector", "target_selector"):
        if not isinstance(rubric[key], str) or not rubric[key]:
            raise ValueError(f"Invalid {key}")
    for key in ("idle_ms", "action_timeout_ms", "navigation_timeout_ms"):
        if type(rubric[key]) is not int or rubric[key] <= 0:
            raise ValueError(f"Invalid {key}")
    if rubric["initial_score"] != 0 or not rubric["click_delays_ms"]:
        raise ValueError("Expected initial_score=0 and at least one click")
    if any(type(delay) is not int or delay <= 0 for delay in rubric["click_delays_ms"]):
        raise ValueError("Invalid click delays")
    if any(
        type(rubric["viewport"][key]) is not int or rubric["viewport"][key] <= 0
        for key in ("width", "height")
    ):
        raise ValueError("Invalid viewport")
    return rubric


@contextmanager
def serve_bundle(root: Path):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, _format, *_args):
            return

        def list_directory(self, _path):
            self.send_error(403, "Directory listing disabled")
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def browser_check(bundle: Path, entry: str, output: Path, rubric: dict, details: dict) -> None:
    try:
        from playwright.sync_api import Error as BrowserError
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise InfrastructureFailure(
            "Playwright is not installed; use the pinned task image"
        ) from error

    actions = details["actions"]
    errors: list[str] = []
    blocked: list[str] = []
    details["browser_errors"] = errors
    details["blocked_requests"] = blocked
    browser = None
    context = None
    page = None
    tracing = False
    stage = "browser_setup"
    try:
        with serve_bundle(bundle) as origin, sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True, timeout=15000)
                details["browser"] = {
                    "name": "chromium",
                    "version": browser.version,
                    "playwright": version("playwright"),
                    "viewport": rubric["viewport"],
                }
                context = browser.new_context(
                    viewport=rubric["viewport"],
                    locale="zh-CN",
                    timezone_id="UTC",
                    service_workers="block",
                    accept_downloads=False,
                )
                context.set_default_timeout(rubric["action_timeout_ms"])

                def restrict_network(route):
                    url = urlsplit(route.request.url)
                    if f"{url.scheme}://{url.netloc}" == origin:
                        route.continue_()
                    else:
                        # Do not retain query strings, which may contain credentials.
                        if len(blocked) < 50:
                            blocked.append(f"{url.scheme}://{url.hostname}{url.path}"[:500])
                        route.abort("blockedbyclient")

                context.route("**/*", restrict_network)
                context.tracing.start(screenshots=True, snapshots=True, sources=False)
                tracing = True
                page = context.new_page()
                page.on(
                    "pageerror",
                    lambda error: errors.append(str(error)[:2000]) if len(errors) < 50 else None,
                )
                fixed_time = datetime(2026, 1, 1, tzinfo=UTC)
                page.clock.install(time=fixed_time)
                page.clock.pause_at(fixed_time)
                # Chromium and the local server are ready. A submitted page's
                # redirect/load failure is a runtime failure, not missing infra.
                stage = "runtime_smoke"
                response = page.goto(
                    f"{origin}/{quote(entry, safe='/')}",
                    wait_until="load",
                    timeout=rubric["navigation_timeout_ms"],
                )
                if response is None or response.status != 200:
                    raise GameFailure("Submitted page did not finish loading with HTTP 200")
                page.clock.run_for(100)
                if errors:
                    raise GameFailure("Uncaught JavaScript error during page startup")
                details["checks"].append({"name": "runtime_smoke", "status": "passed"})
                details["partial_rewards"]["runtime_smoke"] = 1
                stage = "gameplay_interaction"

                def observe(name: str, expected: int, action: dict, operation=None):
                    record = {
                        "step": len(actions),
                        "name": name,
                        "action": action,
                        "expected_score": expected,
                        "status": "failed",
                    }
                    actions.append(record)
                    if operation is not None:
                        operation()
                    score = page.locator(rubric["score_selector"])
                    score.wait_for(state="visible")
                    text = score.inner_text().strip()
                    record["observed_text"] = text
                    screenshot = f"{record['step']:02d}-{name}.png"
                    page.screenshot(path=str(output / screenshot), timeout=3000)
                    record["screenshot"] = screenshot
                    if not re.fullmatch(r"0|[1-9][0-9]{0,8}", text):
                        raise GameFailure(f"{name}: score must be a visible non-negative integer")
                    record["observed_score"] = int(text)
                    if int(text) != expected:
                        raise GameFailure(f"{name}: expected {expected}, observed {text}")
                    record["status"] = "passed"

                observe("initial", 0, {"type": "observe"})
                observe(
                    "idle-before",
                    0,
                    {"type": "wait", "duration_ms": rubric["idle_ms"]},
                    lambda: page.clock.run_for(rubric["idle_ms"]),
                )
                for index, delay in enumerate(rubric["click_delays_ms"], 1):

                    def click_and_settle(settle_ms=delay):
                        # Browser input, not JS dispatchEvent or game-state mutation.
                        page.locator(rubric["target_selector"]).click()
                        page.clock.run_for(settle_ms)

                    observe(
                        f"click-{index}",
                        index,
                        {
                            "type": "click",
                            "selector": rubric["target_selector"],
                            "settle_ms": delay,
                        },
                        click_and_settle,
                    )
                observe(
                    "idle-after",
                    len(rubric["click_delays_ms"]),
                    {
                        "type": "wait",
                        "duration_ms": rubric["idle_ms"],
                    },
                    lambda: page.clock.run_for(rubric["idle_ms"]),
                )
                if errors:
                    raise GameFailure("Uncaught JavaScript error during interaction")
                if blocked:
                    raise GameFailure("Game requested resources outside its offline static bundle")
                details["checks"].append({"name": "gameplay_interaction", "status": "passed"})
                details["partial_rewards"]["gameplay_interaction"] = 1
            except (GameFailure, BrowserError) as error:
                if stage == "browser_setup":
                    raise InfrastructureFailure(f"{stage} failed: {error}") from error
                if browser and not browser.is_connected():
                    raise InfrastructureFailure(f"Browser disconnected: {error}") from error
                details["checks"].append({"name": stage, "status": "failed", "detail": str(error)})
                if page is not None:
                    try:
                        page.screenshot(path=str(output / "failure.png"), timeout=3000)
                    except BrowserError as screenshot_error:
                        details["evidence_warning"] = str(screenshot_error)
                raise GameFailure(str(error)) from error
            finally:
                # Finish artifacts while the Playwright transport is still alive.
                if context is not None:
                    try:
                        if tracing:
                            context.tracing.stop(path=str(output / "trace.zip"))
                    finally:
                        context.close()
                if browser is not None:
                    browser.close()
    except (GameFailure, InfrastructureFailure):
        raise
    except Exception as error:
        raise InfrastructureFailure(
            f"Verifier runtime failed: {type(error).__name__}: {error}"
        ) from error


def evaluate(submission_path: Path, game_root: Path, output: Path, rubric_path: Path) -> int:
    # Harbor creates this directory (and test stdout) first. Refuse to overwrite
    # any existing evaluation; standalone replays must select a fresh directory.
    if output.resolve().is_relative_to(game_root.resolve() / "dist"):
        raise ValueError("Output must not be inside the submitted dist directory")
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in OUTPUT_NAMES):
        raise FileExistsError(
            "Output contains a previous evaluation; choose a fresh output directory"
        )
    details = {
        "schema_version": "0.2",
        "verifier": {"name": "dom-click-counter", "version": VERSION},
        "outcome": "infrastructure_error",
        "checks": [],
        "actions": [],
        "partial_rewards": dict.fromkeys(REWARD_NAMES, 0),
        "scope": "DOM interaction calibration, not gameplay quality",
    }
    code = 0
    try:
        rubric = load_rubric(rubric_path)
        details["rubric_sha256"] = digest(rubric_path)
        details["verifier_sha256"] = digest(Path(__file__))
        submission, entry = load_submission(submission_path, game_root)
        details["submission_sha256"] = digest(submission_path)
        details["submission_kind"] = submission["kind"]
        if entry is not None:
            dist = game_root.resolve() / "dist"
            details["bundle"] = {
                "entrypoint": entry.relative_to(dist).as_posix(),
                "files": freeze_bundle(dist, output / "bundle"),
            }
        details["partial_rewards"]["artifact_contract"] = 1
        details["checks"].append({"name": "artifact_contract", "status": "passed"})
        if entry is None:
            details["outcome"] = "build_failure"
            details["failure"] = submission["failure"]
        else:
            browser_check(
                output / "bundle", details["bundle"]["entrypoint"], output, rubric, details
            )
            details["outcome"] = "passed"
            details["partial_rewards"]["overall"] = 1
    except SubmissionFailure as error:
        details["outcome"] = "invalid_submission"
        details["error"] = str(error)
        details["checks"].append(
            {"name": "artifact_contract", "status": "failed", "detail": str(error)}
        )
    except GameFailure as error:
        details["outcome"] = "gameplay_failure"
        details["error"] = str(error)
    except Exception as error:
        details["outcome"] = "infrastructure_error"
        details["error"] = f"{type(error).__name__}: {error}"
        code = 2

    checked = {check["name"] for check in details["checks"]}
    for name in REWARD_NAMES[:-1]:
        if name not in checked:
            details["checks"].append({"name": name, "status": "not_evaluated"})
    details["rewards"] = None if code else details["partial_rewards"]
    write_json(output / "actions.json", {"schema_version": "0.2", "actions": details["actions"]})
    write_json(output / "details.json", details)
    status = "skipped" if code else "passed" if details["rewards"]["overall"] else "failed"
    write_json(
        output / "ctrf.json",
        {
            "results": {
                "tool": {"name": "ai-game-bench-dom-verifier", "version": VERSION},
                "summary": {
                    "tests": 1,
                    "passed": int(status == "passed"),
                    "failed": int(status == "failed"),
                    "skipped": int(status == "skipped"),
                },
                "tests": [
                    {
                        "name": "click-counter-interaction",
                        "status": status,
                        "message": details.get("error", details["outcome"]),
                    }
                ],
            }
        },
    )
    if not code:
        write_json(output / "reward.json", details["rewards"])
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--submission", type=Path, default=Path("/workspace/gamebench/submission.json")
    )
    parser.add_argument("--game-root", type=Path, default=Path("/workspace/game"))
    parser.add_argument("--output-dir", type=Path, default=Path("/logs/verifier"))
    parser.add_argument("--rubric", type=Path, default=Path(__file__).with_name("rubric.json"))
    args = parser.parse_args(argv)
    try:
        return evaluate(args.submission, args.game_root, args.output_dir, args.rubric)
    except Exception as error:
        print(f"Verifier could not write results: {type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
