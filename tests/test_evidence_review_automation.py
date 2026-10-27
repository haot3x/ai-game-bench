"""Cost-free tests of trusted review routing, scope and comment boundaries."""

import copy
import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "evidence_review", ROOT / ".github/scripts/evidence_review.py"
)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
REPO = "mopan-ai/ai-game-bench"
SHA = "a" * 40
TRUSTED = "b" * 40


@pytest.mark.parametrize("body", [None, {"body": "literal $(not-a-command)\ntext"}])
def test_api_uses_arguments_and_json_stdin_not_a_shell(monkeypatch, body):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout='{"ok": true}')

    monkeypatch.setattr(review.subprocess, "run", run)
    assert review.api("repos/example/project/issues/1/comments", body) == {"ok": True}
    command, options = calls[0]
    assert command[:3] == ["gh", "api", "repos/example/project/issues/1/comments"]
    assert command[3:] == (["--method", "POST", "--input", "-"] if body else [])
    assert options == {
        "input": json.dumps(body) if body else None,
        "text": True,
        "capture_output": True,
        "check": True,
        "timeout": 30,
    }


def test_api_failure_is_not_reported_as_success(monkeypatch):
    def run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["gh", "api"])

    monkeypatch.setattr(review.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        review.api("repos/example/project/pulls/1")


@pytest.mark.parametrize("batch,reason", [({}, "list response"), ([{}] * 100, "pagination")])
def test_metadata_pagination_fails_closed(monkeypatch, batch, reason):
    monkeypatch.setattr(review, "api", lambda _: batch)
    with pytest.raises(ValueError, match=reason):
        list(review.pages("repos/example/project/pulls"))


@pytest.fixture
def pr():
    return {
        "number": 10,
        "state": "open",
        "base": {"ref": "main", "repo": {"full_name": REPO}},
        "head": {"sha": SHA, "repo": {"full_name": "contributor/ai-game-bench"}},
        "changed_files": 1,
    }


@pytest.fixture
def event():
    return {
        "repository": {"full_name": REPO},
        "workflow_run": {
            "event": "pull_request",
            "status": "completed",
            "conclusion": "success",
            "name": "Public checks",
            "path": ".github/workflows/checks.yml",
            "head_sha": SHA,
            "head_repository": {"full_name": "contributor/ai-game-bench"},
            "pull_requests": [],
        },
    }


@pytest.fixture
def github(monkeypatch, pr):
    calls = []
    records = {
        f"repos/{REPO}/pulls?state=open&base=main&per_page=100&page=1": [pr],
        f"repos/{REPO}/pulls/10": pr,
        f"repos/{REPO}/pulls/10/files?per_page=100&page=1": [
            {"filename": "submissions/test/r001/manifest.json"}
        ],
        f"repos/{REPO}/issues/10/comments?per_page=100&page=1": [],
    }

    def api(path, body=None):
        calls.append((path, body))
        if body is not None:
            assert path == f"repos/{REPO}/issues/10/comments"
            return {}
        return copy.deepcopy(records[path])

    monkeypatch.setattr(review, "api", api)
    return records, calls


def test_resolves_fork_even_when_workflow_event_has_no_pr_list(github, event):
    result, reason = review.resolve("workflow_run", event, REPO, "")
    assert result == {"eligible": "true", "pr": "10", "sha": SHA}
    assert reason == ""
    assert all(body is None for _, body in github[1])


def test_manual_dispatch_is_still_available(github):
    assert review.resolve("workflow_dispatch", {}, REPO, "10")[0]["sha"] == SHA


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "timed_out"])
def test_failed_ci_can_still_receive_an_independent_structure_check(github, event, conclusion):
    event["workflow_run"]["conclusion"] = conclusion
    assert review.resolve("workflow_run", event, REPO, "")[0]["eligible"] == "true"


@pytest.mark.parametrize(
    "field,value",
    [
        ("event", "push"),
        ("status", "in_progress"),
        ("path", ".github/workflows/fake.yml"),
        ("name", "Untrusted checks"),
    ],
)
def test_ignores_other_workflows_and_events(github, event, field, value):
    event["workflow_run"][field] = value
    assert not review.resolve("workflow_run", event, REPO, "")[0]
    assert not github[1]


def test_ignores_other_repository(github, event):
    event["repository"]["full_name"] = "other/repo"
    assert not review.resolve("workflow_run", event, REPO, "")[0]


@pytest.mark.parametrize("change", ["closed", "stale", "base", "fork"])
def test_ignores_closed_stale_other_base_or_source_pr(github, event, change):
    pr = github[0][f"repos/{REPO}/pulls?state=open&base=main&per_page=100&page=1"][0]
    if change == "closed":
        pr["state"] = "closed"
    elif change == "stale":
        pr["head"]["sha"] = "c" * 40
    elif change == "base":
        pr["base"]["ref"] = "other"
    else:
        pr["head"]["repo"]["full_name"] = "other/fork"
    assert not review.resolve("workflow_run", event, REPO, "")[0]


def test_ambiguous_pr_needs_manual_dispatch(github, event, pr):
    github[0][f"repos/{REPO}/pulls?state=open&base=main&per_page=100&page=1"] = [pr, pr]
    with pytest.raises(ValueError, match="Ambiguous"):
        review.resolve("workflow_run", event, REPO, "")


def test_skips_non_submission_changes(github):
    github[0][f"repos/{REPO}/pulls/10/files?per_page=100&page=1"] = [{"filename": "README.md"}]
    assert not review.resolve("workflow_dispatch", {}, REPO, "10")[0]


@pytest.mark.parametrize(
    "record",
    [
        {"filename": "removed.md", "previous_filename": "submissions/test/r001/note.md"},
        {"filename": "submissions/test/r001/note.md", "status": "removed"},
    ],
)
def test_detects_renamed_or_deleted_evidence(github, record):
    github[0][f"repos/{REPO}/pulls/10/files?per_page=100&page=1"] = [record]
    assert review.resolve("workflow_dispatch", {}, REPO, "10")[0]["eligible"] == "true"


def test_paginates_changed_files(github):
    base = f"repos/{REPO}/pulls/10/files?per_page=100&page="
    github[0][base + "2"] = github[0][base + "1"]
    github[0][base + "1"] = [{"filename": "README.md"}] * 100
    assert review.resolve("workflow_dispatch", {}, REPO, "10")[0]["eligible"] == "true"


def test_paginates_open_prs(github, event, pr):
    base = f"repos/{REPO}/pulls?state=open&base=main&per_page=100&page="
    github[0][base + "1"] = [{"state": "closed"}] * 100
    github[0][base + "2"] = [pr]
    assert review.resolve("workflow_run", event, REPO, "")[0]["sha"] == SHA


def test_rejects_oversized_pr(github):
    github[0][f"repos/{REPO}/pulls/10"]["changed_files"] = 3001
    with pytest.raises(ValueError, match="too large"):
        review.resolve("workflow_dispatch", {}, REPO, "10")


def test_rejects_changed_head_during_file_listing(monkeypatch, github):
    original = review.api
    reads = 0

    def racing_api(path, body=None):
        nonlocal reads
        result = original(path, body)
        if path == f"repos/{REPO}/pulls/10":
            reads += 1
            if reads > 1:
                result["head"]["sha"] = "c" * 40
        return result

    monkeypatch.setattr(review, "api", racing_api)
    assert not review.resolve("workflow_dispatch", {}, REPO, "10")[0]


def test_rejects_head_changed_after_open_pr_lookup(monkeypatch, github, event):
    original = review.api

    def racing_api(path, body=None):
        result = original(path, body)
        if path == f"repos/{REPO}/pulls/10":
            result["head"]["sha"] = "c" * 40
        return result

    monkeypatch.setattr(review, "api", racing_api)
    assert not review.resolve("workflow_run", event, REPO, "")[0]
    assert not any("/files?" in path for path, _ in github[1])


@pytest.mark.parametrize("number", ["0", "-1", "10\nsha=fake", "$(echo unsafe)"])
def test_rejects_untrusted_identifier_injection(github, number):
    with pytest.raises(ValueError, match="identifier"):
        review.resolve("workflow_dispatch", {}, REPO, number)
    assert not github[1]


@pytest.mark.parametrize(
    "outcome,expected",
    [
        ("success", "Passed"),
        ("failure", "Failed"),
        ("skipped", "Not completed"),
        ("", "Not completed"),
        ("attacker text", "Not completed"),
    ],
)
def test_receipt_limits_verification_claims(outcome, expected):
    text = review.receipt(REPO, "10", SHA, TRUSTED, "123", "2", outcome)
    assert expected in text
    assert "structural validation only" in text
    assert "Evidence content review | No" in text
    assert "Artifact gameplay replay | No" in text
    assert "Independent generation rerun | No" in text
    assert "do **not** prove capture authenticity" in text
    assert "not approval or a merge" in text
    assert SHA in text and TRUSTED in text
    assert "runs/123/attempts/2" in text
    assert "attacker text" not in text


@pytest.fixture
def report_env(monkeypatch, tmp_path):
    values = {
        "REVIEW_PR": "10",
        "REVIEW_SHA": SHA,
        "GITHUB_SHA": TRUSTED,
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "1",
        "REVIEW_OUTCOME": "success",
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return tmp_path / "summary.md"


def test_report_only_posts_fixed_comment_for_exact_head(github, report_env):
    review.report(REPO)
    writes = [(path, body) for path, body in github[1] if body is not None]
    assert len(writes) == 1
    assert writes[0][0] == f"repos/{REPO}/issues/10/comments"
    assert writes[0][1]["body"] in report_env.read_text()


@pytest.mark.parametrize("closed", [True, False])
def test_report_does_not_post_for_superseded_or_closed_pr(github, report_env, closed):
    pr = github[0][f"repos/{REPO}/pulls/10"]
    if closed:
        pr["state"] = "closed"
    else:
        pr["head"]["sha"] = "c" * 40
    review.report(REPO)
    assert not any(body is not None for _, body in github[1])


def test_report_rechecks_head_immediately_before_post(monkeypatch, github, report_env):
    original = review.api
    reads = 0

    def racing_api(path, body=None):
        nonlocal reads
        result = original(path, body)
        if path == f"repos/{REPO}/pulls/10":
            reads += 1
            if reads > 1:
                result["head"]["sha"] = "c" * 40
        return result

    monkeypatch.setattr(review, "api", racing_api)
    review.report(REPO)
    assert reads == 2
    assert not any(body is not None for _, body in github[1])


@pytest.mark.parametrize("bot", [True, False])
def test_comment_dedup_only_trusts_actions_bot(github, report_env, bot):
    github[0][f"repos/{REPO}/issues/10/comments?per_page=100&page=1"] = [
        {
            "body": "<!-- agb-structure-review:123:1 -->spoof",
            "user": {"login": "github-actions[bot]" if bot else "attacker", "type": "Bot"},
        }
    ]
    review.report(REPO)
    assert any(body is not None for _, body in github[1]) is not bot


def test_resolve_main_outputs_only_validated_metadata(monkeypatch, tmp_path, github, event):
    payload = tmp_path / "event.json"
    payload.write_text(json.dumps(event))
    output = tmp_path / "output"
    for key, value in {
        "REVIEW_REPO": REPO,
        "GITHUB_EVENT_NAME": "workflow_run",
        "GITHUB_EVENT_PATH": str(payload),
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(review.sys, "argv", ["evidence_review.py", "resolve"])
    review.main()
    assert output.read_text() == f"eligible=true\npr=10\nsha={SHA}\n"
