from __future__ import annotations

import json
from pathlib import Path

import pytest


def make_submission(tmp_path: Path, body: object) -> Path:
    path = tmp_path / "submission.json"
    path.write_text(json.dumps(body))
    return path


def local_submission(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "game"
    (root / "dist").mkdir(parents=True)
    entry = root / "dist/index.html"
    entry.write_text("<html><script>let n = 0;</script></html>")
    return make_submission(
        tmp_path,
        {
            "schema_version": "0.1",
            "kind": "local_directory",
            "entrypoint": str(entry),
        },
    ), root


@pytest.mark.parametrize(
    "body",
    [
        None,
        [],
        {},
        {"schema_version": "0.2"},
        {"schema_version": "0.1", "kind": "remote_url", "game_url": "https://example.com"},
        {"schema_version": "0.1", "kind": "build_failure", "failure": {"message": 3}},
        {
            "schema_version": "0.1",
            "kind": "build_failure",
            "failure": {"message": " "},
            "producer": {"status": "failed"},
        },
        {
            "schema_version": "0.1",
            "kind": "build_failure",
            "failure": {"message": "bad"},
            "producer": {"status": "ready"},
        },
    ],
)
def test_invalid_contract_is_not_awarded(dom_verifier, dom_task, tmp_path, body):
    submission = make_submission(tmp_path, body)
    output = tmp_path / "result"
    assert (
        dom_verifier.evaluate(submission, tmp_path / "game", output, dom_task / "tests/rubric.json")
        == 0
    )
    assert json.loads((output / "reward.json").read_text())["artifact_contract"] == 0
    details = json.loads((output / "details.json").read_text())
    assert details["outcome"] == "invalid_submission"
    assert any(c["status"] == "not_evaluated" for c in details["checks"])


def test_missing_submission_is_nop_failure(dom_verifier, dom_task, tmp_path):
    output = tmp_path / "result"
    assert (
        dom_verifier.evaluate(
            tmp_path / "missing.json", tmp_path / "game", output, dom_task / "tests/rubric.json"
        )
        == 0
    )
    assert set(json.loads((output / "reward.json").read_text()).values()) == {0}


def test_build_failure_does_not_launch_browser(dom_verifier, dom_task, tmp_path, monkeypatch):
    monkeypatch.setattr(dom_verifier, "browser_check", lambda *_: pytest.fail("Unexpected browser"))
    submission = make_submission(
        tmp_path,
        {
            "schema_version": "0.1",
            "kind": "build_failure",
            "failure": {"message": "Recorded build failed"},
            "producer": {"status": "failed"},
        },
    )
    output = tmp_path / "result"
    assert (
        dom_verifier.evaluate(submission, tmp_path / "game", output, dom_task / "tests/rubric.json")
        == 0
    )
    assert json.loads((output / "reward.json").read_text()) == {
        "artifact_contract": 1,
        "runtime_smoke": 0,
        "gameplay_interaction": 0,
        "overall": 0,
    }


@pytest.mark.parametrize("failure", ["infrastructure", "unexpected", "rubric"])
def test_infrastructure_has_details_but_no_reward(
    dom_verifier,
    dom_task,
    tmp_path,
    monkeypatch,
    failure,
):
    submission, root = local_submission(tmp_path)
    output = tmp_path / "result"

    def broken_browser(*_):
        if failure == "unexpected":
            raise RuntimeError("Verifier bug")
        raise dom_verifier.InfrastructureFailure("Chromium missing")

    monkeypatch.setattr(dom_verifier, "browser_check", broken_browser)
    rubric = dom_task / "tests/rubric.json" if failure != "rubric" else tmp_path / "missing.json"
    assert dom_verifier.evaluate(submission, root, output, rubric) == 2
    assert not (output / "reward.json").exists()
    details = json.loads((output / "details.json").read_text())
    assert details["outcome"] == "infrastructure_error"
    assert details["rewards"] is None
    assert json.loads((output / "ctrf.json").read_text())["results"]["summary"]["skipped"] == 1


def test_game_failure_is_scored_zero(dom_verifier, dom_task, tmp_path, monkeypatch):
    submission, root = local_submission(tmp_path)

    def static_game(*_):
        raise dom_verifier.GameFailure("Click did not increment score")

    monkeypatch.setattr(dom_verifier, "browser_check", static_game)
    output = tmp_path / "result"
    assert dom_verifier.evaluate(submission, root, output, dom_task / "tests/rubric.json") == 0
    assert json.loads((output / "details.json").read_text())["outcome"] == "gameplay_failure"
    assert json.loads((output / "reward.json").read_text())["overall"] == 0


def test_entrypoint_cannot_escape_dist(dom_verifier, tmp_path):
    other = tmp_path / "outside.html"
    other.write_text("private")
    _, root = local_submission(tmp_path)
    submission = make_submission(
        tmp_path,
        {
            "schema_version": "0.1",
            "kind": "local_directory",
            "entrypoint": str(other),
        },
    )
    with pytest.raises(dom_verifier.SubmissionFailure, match="inside"):
        dom_verifier.load_submission(submission, root)


def test_bundle_rejects_symlinks(dom_verifier, tmp_path):
    _, root = local_submission(tmp_path)
    (root / "dist/leak").symlink_to(tmp_path)
    with pytest.raises(dom_verifier.SubmissionFailure, match="symbolic"):
        dom_verifier.freeze_bundle(root / "dist", tmp_path / "bundle")


def test_bundle_size_is_bounded(dom_verifier, tmp_path, monkeypatch):
    _, root = local_submission(tmp_path)
    monkeypatch.setattr(dom_verifier, "MAX_BUNDLE_BYTES", 1)
    with pytest.raises(dom_verifier.SubmissionFailure, match="exceeds"):
        dom_verifier.freeze_bundle(root / "dist", tmp_path / "bundle")


def test_snapshot_is_independent_and_hashable(dom_verifier, tmp_path):
    _, root = local_submission(tmp_path)
    bundle = tmp_path / "bundle"
    manifest = dom_verifier.freeze_bundle(root / "dist", bundle)
    (root / "dist/index.html").write_text("changed")
    assert manifest[0]["sha256"] == dom_verifier.digest(bundle / "index.html")
    assert (bundle / "index.html").read_text() != "changed"


def test_replay_requires_fresh_output(dom_verifier, dom_task, tmp_path):
    output = tmp_path / "result"
    args = (tmp_path / "missing.json", tmp_path / "game", output, dom_task / "tests/rubric.json")
    dom_verifier.evaluate(*args)
    before = (output / "details.json").read_bytes()
    with pytest.raises(FileExistsError, match="previous"):
        dom_verifier.evaluate(*args)
    assert (output / "details.json").read_bytes() == before


def test_output_cannot_mutate_submitted_bundle(dom_verifier, dom_task, tmp_path):
    submission, root = local_submission(tmp_path)
    output = root / "dist/results"
    with pytest.raises(ValueError, match="inside"):
        dom_verifier.evaluate(submission, root, output, dom_task / "tests/rubric.json")
    assert not output.exists()
