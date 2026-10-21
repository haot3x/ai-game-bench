"""Trusted-main metadata routing and fixed-scope receipts; never execute PR code."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def checked(value: str, pattern: str) -> str:
    if not re.fullmatch(pattern, value):
        raise ValueError("Invalid review identifier.")
    return value


def api(path: str, body: dict | None = None):
    command = ["gh", "api", path]
    if body is not None:
        command += ["--method", "POST", "--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(body) if body is not None else None,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    return json.loads(result.stdout)


def pages(path: str):
    # GitHub's PR files endpoint caps at 3,000 files; fail closed at that boundary.
    for page in range(1, 31):
        separator = "&" if "?" in path else "?"
        batch = api(f"{path}{separator}per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Expected a GitHub list response.")
        yield from batch
        if len(batch) < 100:
            return
    raise ValueError("Review metadata exceeds pagination limit; inspect manually.")


def repository() -> str:
    return checked(os.environ["REVIEW_REPO"], r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def current_pr(pr: dict, repo: str, sha: str | None = None) -> bool:
    return (
        pr.get("state") == "open"
        and pr.get("base", {}).get("ref") == "main"
        and pr.get("base", {}).get("repo", {}).get("full_name") == repo
        and (sha is None or pr.get("head", {}).get("sha") == sha)
    )


def resolve(event_name: str, event: dict, repo: str, requested: str) -> tuple[dict, str]:
    if event_name == "workflow_dispatch":
        number = checked(requested, r"[1-9][0-9]*")
        pr = api(f"repos/{repo}/pulls/{number}")
    elif event_name == "workflow_run":
        run = event["workflow_run"]
        if (
            run.get("event") != "pull_request"
            or run.get("status") != "completed"
            or run.get("path") != ".github/workflows/checks.yml"
            or run.get("name") != "Public checks"
            or event.get("repository", {}).get("full_name") != repo
        ):
            return {}, "Not a completed Public checks PR run."
        sha = checked(run["head_sha"], r"[0-9a-f]{40}")
        # Both workflow_run.pull_requests and commits/{sha}/pulls can be empty
        # for forks. Match open PRs by exact head SHA AND source repository.
        matches = [
            item
            for item in pages(f"repos/{repo}/pulls?state=open&base=main")
            if current_pr(item, repo, sha)
            and item.get("head", {}).get("repo", {}).get("full_name")
            == run.get("head_repository", {}).get("full_name")
        ]
        if not matches:
            return {}, "No current open PR for this head (superseded or closed)."
        if len(matches) != 1:
            raise ValueError("Ambiguous PR association; dispatch the intended PR manually.")
        number = checked(str(matches[0]["number"]), r"[1-9][0-9]*")
        pr = api(f"repos/{repo}/pulls/{number}")
        if not current_pr(pr, repo, sha):
            return {}, "PR changed while resolving; wait for its new CI run."
    else:
        raise ValueError("Unsupported review event.")

    if not current_pr(pr, repo):
        return {}, "Only open PRs targeting this repository's main are eligible."
    if pr.get("changed_files", 0) > 3000:
        raise ValueError("PR too large for automatic routing; inspect manually.")
    # Consume every page, including renamed/deleted evidence, before deciding.
    files = list(pages(f"repos/{repo}/pulls/{number}/files"))
    if not any(
        item.get(key, "").startswith("submissions/")
        for item in files
        for key in ("filename", "previous_filename")
    ):
        return {}, "No submission changes; ordinary Public checks are sufficient."
    sha = checked(pr["head"]["sha"], r"[0-9a-f]{40}")
    # The files API follows a moving PR; never approve a head from a mixed snapshot.
    if not current_pr(api(f"repos/{repo}/pulls/{number}"), repo, sha):
        return {}, "PR changed while listing files; wait for its new CI run."
    return {"eligible": "true", "pr": number, "sha": sha}, ""


def receipt(
    repo: str, number: str, sha: str, trusted: str, run: str, attempt: str, outcome: str
) -> str:
    result = {
        "success": "Passed",
        "failure": "Failed — inspect logs (validation or runtime error)",
    }.get(outcome, "Not completed — see setup/runner errors in the run")
    url = f"https://github.com/{repo}/actions/runs/{run}/attempts/{attempt}"
    return (
        f"<!-- agb-structure-review:{run}:{attempt} -->\n"
        "### Evidence check — structural validation only\n\n"
        f"PR #{number} · head `{sha}`\n\n"
        f"**Structure: {result}.** [Check run]({url})\n\n"
        "| Verification | Performed by this action |\n"
        "| --- | --- |\n"
        "| Structure and consistency | " + result + " |\n"
        "| Evidence content review | No |\n"
        "| Artifact gameplay replay | No |\n"
        "| Independent generation rerun | No |\n\n"
        "Checks cover schema, frozen policy, hashes, event references/timing and score "
        "arithmetic. They do **not** prove capture authenticity, model identity, costs "
        "or absence of hidden attempts.\n\n"
        f"Trusted checker: `{trusted}`. Applies only to the head above. "
        "Maintainer decisions remain separate; this is not approval or a merge.\n"
    )


def summary(text: str) -> None:
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as handle:
        handle.write(text + "\n")


def report(repo: str) -> None:
    number = checked(os.environ["REVIEW_PR"], r"[1-9][0-9]*")
    sha = checked(os.environ["REVIEW_SHA"], r"[0-9a-f]{40}")
    trusted = checked(os.environ["GITHUB_SHA"], r"[0-9a-f]{40}")
    run = checked(os.environ["GITHUB_RUN_ID"], r"[1-9][0-9]*")
    attempt = checked(os.environ["GITHUB_RUN_ATTEMPT"], r"[1-9][0-9]*")
    if not current_pr(api(f"repos/{repo}/pulls/{number}"), repo, sha):
        summary("Superseded or closed PR: no current-head receipt posted.")
        return
    body = receipt(repo, number, sha, trusted, run, attempt, os.getenv("REVIEW_OUTCOME", ""))
    summary(body)
    marker = f"<!-- agb-structure-review:{run}:{attempt} -->"
    comments = list(pages(f"repos/{repo}/issues/{number}/comments"))
    if any(
        comment.get("user", {}).get("login") == "github-actions[bot]"
        and comment.get("user", {}).get("type") == "Bot"
        and comment.get("body", "").startswith(marker)
        for comment in comments
    ):
        return
    # Recheck just before writing. A subsequent push still leaves an explicitly SHA-bound receipt.
    if current_pr(api(f"repos/{repo}/pulls/{number}"), repo, sha):
        api(f"repos/{repo}/issues/{number}/comments", {"body": body})


def main() -> None:
    repo = repository()
    if sys.argv[1:] == ["resolve"]:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        result, reason = resolve(
            os.environ["GITHUB_EVENT_NAME"], event, repo, os.getenv("REVIEW_PR", "")
        )
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as handle:
            for key, value in (result or {"eligible": "false"}).items():
                handle.write(f"{key}={value}\n")
        summary(
            f"Resolving PR #{result['pr']} at `{result['sha']}` for structural validation only."
            if result
            else reason
        )
    elif sys.argv[1:] == ["report"]:
        report(repo)
    else:
        raise ValueError("Use resolve or report.")


if __name__ == "__main__":
    main()
