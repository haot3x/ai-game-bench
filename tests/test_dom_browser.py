from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("GAMEBENCH_BROWSER_TESTS") != "1",
        reason="Run ./scripts/test-browser.sh for real Chromium calibration",
    ),
]


def setup_game(tmp_path: Path, source: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "game"
    (root / "dist").mkdir(parents=True)
    entry = root / "dist/index.html"
    shutil.copyfile(source, entry)
    submission = tmp_path / "submission.json"
    submission.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "kind": "local_directory",
                "entrypoint": str(entry),
            }
        )
    )
    return submission, root, tmp_path / "result"


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("oracle", "passed"),
        ("working", "passed"),
        ("static", "gameplay_failure"),
        ("auto-increment", "gameplay_failure"),
        ("double-increment", "gameplay_failure"),
        ("one-click-only", "gameplay_failure"),
        ("hidden-score", "gameplay_failure"),
        ("blocked-button", "gameplay_failure"),
        ("runtime-error", "gameplay_failure"),
        ("external-resource", "gameplay_failure"),
        ("external-navigation", "gameplay_failure"),
    ],
)
def test_real_browser_calibration(dom_verifier, dom_task, tmp_path, fixture, expected):
    fixtures = Path(os.environ["GAMEBENCH_BROWSER_FIXTURES"])
    source = (
        dom_task / "solution/files/index.html"
        if fixture == "oracle"
        else fixtures / f"{fixture}.html"
    )
    submission, root, output = setup_game(tmp_path, source)
    assert dom_verifier.evaluate(submission, root, output, dom_task / "tests/rubric.json") == 0
    details = json.loads((output / "details.json").read_text())
    assert details["outcome"] == expected, details
    reward = json.loads((output / "reward.json").read_text())
    assert reward["artifact_contract"] == 1
    assert reward["overall"] == int(expected == "passed")
    assert (output / "trace.zip").stat().st_size > 0
    assert list(output.glob("*.png"))
    assert details["bundle"]["files"][0]["sha256"] == dom_verifier.digest(source)
    if expected == "passed":
        actions = json.loads((output / "actions.json").read_text())["actions"]
        assert [step["observed_score"] for step in actions] == [0, 0, 1, 2, 3, 3]
        assert all((output / step["screenshot"]).is_file() for step in actions)
    if fixture == "one-click-only":
        assert "click-2" in details["error"]
    if fixture == "auto-increment":
        assert "idle-before" in details["error"]
    if fixture in {"external-resource", "external-navigation"}:
        assert details["blocked_requests"]


def test_missing_browser_is_infrastructure_not_game_failure(
    dom_verifier,
    dom_task,
    tmp_path,
    monkeypatch,
):
    submission, root, output = setup_game(tmp_path, dom_task / "solution/files/index.html")
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", "/nonexistent-gamebench-browser")
    assert dom_verifier.evaluate(submission, root, output, dom_task / "tests/rubric.json") == 2
    details = json.loads((output / "details.json").read_text())
    assert details["outcome"] == "infrastructure_error"
    assert details["rewards"] is None
    assert "browser_setup" in details["error"]
    assert not (output / "reward.json").exists()


def test_frozen_bundle_can_be_reverified(dom_verifier, dom_task, tmp_path):
    submission, root, output = setup_game(tmp_path, dom_task / "solution/files/index.html")
    rubric = dom_task / "tests/rubric.json"
    assert dom_verifier.evaluate(submission, root, output, rubric) == 0
    replay_root = tmp_path / "replay-game"
    shutil.copytree(output / "bundle", replay_root / "dist")
    replay_submission = tmp_path / "replay-submission.json"
    replay_submission.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "kind": "local_directory",
                "entrypoint": str(replay_root / "dist/index.html"),
            }
        )
    )
    replay = tmp_path / "replay-result"
    assert dom_verifier.evaluate(replay_submission, replay_root, replay, rubric) == 0
    assert (replay / "reward.json").read_bytes() == (output / "reward.json").read_bytes()
    assert (replay / "actions.json").read_bytes() == (output / "actions.json").read_bytes()
