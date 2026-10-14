from __future__ import annotations

import copy
import json
import os
import shutil
import socket
import subprocess
from pathlib import Path

import pytest

from ai_game_bench import cli
from ai_game_bench import submissions as s

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/submissions/synthetic-counter"


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Public validation must not make network connections")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def package(tmp_path):
    target = tmp_path / "package"
    shutil.copytree(EXAMPLE, target)
    return target


@pytest.fixture
def trusted_root(tmp_path):
    """A unit test's accepted-data baseline must not depend on real submissions."""
    target = tmp_path / "trusted"
    for directory in ("datasets", "policies", "protocols"):
        shutil.copytree(ROOT / directory, target / directory)
    shutil.copyfile(ROOT / "pyproject.toml", target / "pyproject.toml")
    (target / "submissions").mkdir()
    return target


def manifest(package):
    return json.loads((package / "manifest.json").read_text())


def save(package, record):
    (package / "manifest.json").write_bytes(s.encode(record))


def rewrite_events(package, filename, edit):
    events = [json.loads(line) for line in (package / filename).read_text().splitlines()]
    edit(events)
    data = ("\n".join(json.dumps(e) for e in events) + "\n").encode()
    (package / filename).write_bytes(data)
    record = manifest(package)
    for entry in record["files"]:
        if entry["path"] == filename:
            entry.update(sha256=s.digest(data), bytes=len(data))
    save(package, record)


def rejected(package, code):
    result = s.validate(package, ROOT)
    assert result["structure_valid"] is False, result
    assert result["review_status"] == "needs_changes"
    assert result["errors"][0]["code"] == code, result


def test_example_is_valid_not_verified():
    result = s.validate(EXAMPLE, ROOT)
    assert result["structure_valid"] is True, result
    assert result["review_status"] == "unverified"
    assert result["kind"] == "synthetic_example"
    assert result["attempts"][0]["recomputed_total"] == 1


def test_collection_accepts_two_maximum_file_count_packages(tmp_path, trusted_root):
    tree = tmp_path / "incoming"
    for name in ("large-a", "large-b"):
        package = tree / name / "r001"
        shutil.copytree(EXAMPLE, package)
        record = manifest(package)
        record.update(id=name, kind="result")
        for index in range(300 - len(record["files"])):
            filename = f"extra-{index}.txt"
            data = b"Synthetic inventory boundary fixture."
            (package / filename).write_bytes(data)
            record["files"].append({"path": filename, "bytes": len(data), "sha256": s.digest(data)})
        save(package, record)
    result = s.validate_tree(tree, trusted_root)
    assert result["structure_valid"], result
    assert result["count"] == 2


def test_draft_never_authorizes_publication(tmp_path):
    destination = tmp_path / "draft"
    s.initialize(ROOT, destination, "counter-calibration-v1", "my-run")
    assert manifest(destination)["publication"]["public_release_confirmed"] is False
    assert not s.validate(destination, ROOT)["structure_valid"]
    with pytest.raises(FileExistsError):
        s.initialize(ROOT, destination, "counter-calibration-v1", "my-run")


@pytest.mark.parametrize(
    "field",
    [
        "public_release_confirmed",
        "rights_confirmed",
        "sensitive_data_checked",
        "all_attempts_disclosed",
    ],
)
def test_explicit_attestations(package, field):
    record = manifest(package)
    record["publication"][field] = False
    save(package, record)
    rejected(package, "publication")


def test_cannot_claim_self_verified(package):
    record = manifest(package)
    record["review_status"] = "independently_reproduced"
    save(package, record)
    rejected(package, "schema")


def test_policy_cannot_be_changed_by_submitter(package):
    record = manifest(package)
    record["policy_sha256"] = "0" * 64
    save(package, record)
    rejected(package, "policy")


@pytest.mark.parametrize("content", [b"changed", b"", b"malicious replacement"])
def test_altered_evidence_hash(package, content):
    (package / "observations.txt").write_bytes(content)
    rejected(package, "file_hash")


def test_unlisted_file_is_not_silently_uploaded(package):
    (package / "private-notes.txt").write_text("Do not upload this")
    rejected(package, "unlisted_files")


@pytest.mark.parametrize(
    "path",
    [
        "../secret",
        "/tmp/secret",
        "a/../../secret",
        "./a",
        "a//b",
        "a\\b",
        ".env",
        "jobs/result.json",
        "a/.git/config",
    ],
)
def test_unsafe_paths(path):
    with pytest.raises(s.InvalidSubmission, match="relative"):
        s.relative_path(path)


def test_symlink_rejected_without_following(package, tmp_path):
    (package / "observations.txt").unlink()
    (package / "observations.txt").symlink_to(tmp_path / "outside")
    rejected(package, "symlink")


def test_symlink_directory_rejected(package, tmp_path):
    (package / "outside").symlink_to(tmp_path, target_is_directory=True)
    rejected(package, "symlink")


def test_fifo_cannot_block_reader(package):
    (package / "observations.txt").unlink()
    os.mkfifo(package / "observations.txt")
    rejected(package, "file_type")


def add_file(package, name, content):
    (package / name).write_bytes(content)
    record = manifest(package)
    record["files"].append({"path": name, "sha256": s.digest(content), "bytes": len(content)})
    save(package, record)


@pytest.mark.parametrize("filename", ["run.sh", "game.html", "archive.zip", "view.svg", "code.py"])
def test_executable_or_active_content_not_accepted(package, filename):
    add_file(package, filename, b"not executed")
    rejected(package, "file_type")


def test_fake_image_not_accepted(package):
    add_file(package, "shot.png", b"shell script disguised as an image")
    rejected(package, "file_type")


@pytest.mark.parametrize(
    "content",
    [
        b"sk-" + b"x" * 30,
        b"ghp_" + b"x" * 36,
        b"Authorization: Bearer illustrative-not-a-real-token",
        b"/Users/example/Library/Chrome/Profile 1",
    ],
)
def test_credential_and_personal_path_heuristics(package, content):
    add_file(package, "leak.txt", content)
    rejected(package, "sensitive_text")
    assert content.decode() not in json.dumps(s.validate(package, ROOT))


@pytest.mark.parametrize(
    "edit,code",
    [
        (lambda events: events[1].update(seq=9), "trajectory"),
        (lambda events: events[1].update(id=events[0]["id"]), "trajectory"),
        (lambda events: events[1].update(at="2025-12-31T00:00:00Z"), "trajectory"),
        (lambda events: events[1].update(at="2026-01-01T00:00:00"), "schema"),
        (lambda events: events[1].update(kind="progress", prompt=None), "missing_send"),
        (lambda events: events[1].update(evidence=[]), "missing_send"),
        (lambda events: events[1].update(prompt="A different task"), "prompt"),
        (lambda events: events[0].update(kind="progress"), "trajectory"),
        (lambda events: events[2].update(artifact_id="different-build"), "artifact_mismatch"),
        (lambda events: events[2].update(at="2026-01-01T01:00:00Z"), "time_limit"),
    ],
)
def test_creation_trajectory_negative_cases(package, edit, code):
    rewrite_events(package, "creation.jsonl", edit)
    rejected(package, code)


@pytest.mark.parametrize(
    "kind,code",
    [("prompt_accepted", "attempts"), ("followup", "followup_policy"), ("repair", "repair_policy")],
)
def test_undisclosed_send_followup_or_repair(package, kind, code):
    def insert(events):
        extra = {**events[1], "seq": 3, "id": "c-extra", "kind": kind}
        events.insert(2, extra)
        events[-1]["seq"] = 4

    rewrite_events(package, "creation.jsonl", insert)
    rejected(package, code)


def test_extra_attempt_rejected_not_best_of(package):
    record = manifest(package)
    record["attempts"].append({**record["attempts"][0], "id": "attempt-2"})
    save(package, record)
    rejected(package, "attempts")


@pytest.mark.parametrize(
    "edit,code",
    [
        (lambda r: r.update(total=0.99), "total"),
        (lambda r: r["criteria"][0].update(score=10), "score"),
        (lambda r: r["criteria"][0].update(score=-1), "schema"),
        (lambda r: r["criteria"][0].update(evidence_events=[]), "missing_evidence"),
        (lambda r: r["criteria"][0].update(evidence_events=["c-delivered"]), "evidence_reference"),
        (lambda r: r["criteria"][0].update(criterion_id="easier-test"), "criteria"),
        (lambda r: r["criteria"][0].update(status="not_tested"), "score"),
    ],
)
def test_score_and_evidence_negative_cases(package, edit, code):
    record = manifest(package)
    edit(record["attempts"][0]["result"])
    save(package, record)
    rejected(package, code)


def test_circular_self_evidence_rejected(package):
    rewrite_events(
        package, "evaluation.jsonl", lambda events: events[2].update(evidence=["evaluation.jsonl"])
    )
    rejected(package, "evidence_reference")


def test_wrong_evaluation_artifact(package):
    rewrite_events(
        package, "evaluation.jsonl", lambda events: events[2].update(artifact_id="other-game")
    )
    rejected(package, "artifact_mismatch")


def test_valid_failed_game_is_valid_data(package):
    record = manifest(package)
    verdict = record["attempts"][0]["result"]["criteria"][0]
    verdict.update(status="failed", score=0, reason="Synthetic broken game observation")
    record["attempts"][0]["result"]["total"] = 0
    save(package, record)
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert result["attempts"][0]["recomputed_total"] == 0


def test_infrastructure_error_is_not_game_zero(package):
    rewrite_events(
        package,
        "creation.jsonl",
        lambda events: events[-1].update(kind="infrastructure_error", artifact_id=None),
    )
    rewrite_events(
        package, "evaluation.jsonl", lambda events: [e.update(artifact_id=None) for e in events]
    )
    record = manifest(package)
    attempt = record["attempts"][0]
    attempt.update(outcome="infrastructure_error", artifact=None)
    attempt["result"]["criteria"][0].update(status="infra_error", score=None)
    attempt["result"]["total"] = None
    save(package, record)
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert result["attempts"][0]["recomputed_total"] is None
    attempt["result"]["total"] = 0
    save(package, record)
    rejected(package, "total")


def test_unknown_cost_is_not_free(package):
    record = manifest(package)
    record["costs"][0].update(kind="unknown", amount=None, currency=None)
    save(package, record)
    assert s.validate(package, ROOT)["structure_valid"]
    record["costs"][0]["amount"] = 0
    save(package, record)
    rejected(package, "cost")


def test_counter_cannot_be_reinterpreted_as_partial_quality_score(package):
    record = manifest(package)
    record["attempts"][0]["result"]["criteria"][0].update(status="partial", score=0.5)
    record["attempts"][0]["result"]["total"] = 0.5
    save(package, record)
    rejected(package, "score")


def test_visible_model_requires_pre_send_evidence(package):
    record = manifest(package)
    record["creator"].update(model="Example UI label", model_source="visible_ui")
    save(package, record)
    rejected(package, "model")


def test_browser_observations_cannot_claim_native_harbor_artifact(package):
    record = manifest(package)
    record["source_kind"] = "browser_observation"
    save(package, record)
    rejected(package, "source")


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org/a",
        "https://localhost/a",
        "https://127.0.0.1/a",
        "https://10.0.0.1/a",
        "https://user:pass@example.org/a",
        "https://example.org/video?access=private",
        "file:///tmp/a",
        "https://example.org/a#secret",
    ],
)
def test_nonpublic_reference_rejected(url):
    with pytest.raises(s.InvalidSubmission):
        s.public_url(url)


def test_external_evidence_not_downloaded_or_claimed_verified(package, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("No commands may execute"))
    record = manifest(package)
    record["external_evidence"] = [
        {
            "id": "video",
            "url": "https://example.org/video.mp4",
            "sha256": "1" * 64,
            "bytes": 8000000,
            "description": "Synthetic public reference, not fetched",
        }
    ]
    save(package, record)
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert any("NOT downloaded" in w for w in result["warnings"])


def test_prepare_requires_confirmation_and_preserves_existing(package, tmp_path):
    target = tmp_path / "ready"
    with pytest.raises(s.InvalidSubmission, match="confirm-public"):
        s.prepare(package, ROOT, target, confirmed=False)
    result = s.prepare(package, ROOT, target, confirmed=True)
    assert result["uploaded"] is False
    assert result["review_status"] == "unverified"
    assert s.validate(target, ROOT)["structure_valid"]
    with pytest.raises(s.InvalidSubmission, match="overwrite"):
        s.prepare(package, ROOT, target, confirmed=True)


def test_prepare_fills_missing_hashes_but_not_changed_ones(package, tmp_path):
    record = manifest(package)
    for entry in record["files"]:
        entry.update(sha256=None, bytes=None)
    save(package, record)
    assert s.prepare(package, ROOT, tmp_path / "ready", confirmed=True)["structure_valid"]
    # The source draft is not silently rewritten or approved by the packager.
    assert manifest(package)["files"][0]["sha256"] is None


def test_prepare_does_not_reseal_tampering(package, tmp_path):
    (package / "observations.txt").write_text("Changed after hashing")
    with pytest.raises(s.InvalidSubmission, match="hash/size mismatch"):
        s.prepare(package, ROOT, tmp_path / "ready", confirmed=True)
    assert not (tmp_path / "ready").exists()


def test_tree_layout_and_synthetic_block(package, tmp_path, trusted_root):
    tree = tmp_path / "submissions"
    shutil.copytree(package, tree / "synthetic-counter/r001")
    assert not s.validate_tree(tree, trusted_root)["structure_valid"]
    record = manifest(tree / "synthetic-counter/r001")
    record["kind"] = (
        "result"  # Mechanical gate only; the reviewer must still reject invented evidence.
    )
    save(tree / "synthetic-counter/r001", record)
    result = s.validate_tree(tree, trusted_root)
    assert result["structure_valid"], result
    assert result["review_status"] == "unverified"


def test_missing_or_malformed_manifest(tmp_path):
    assert not s.validate(tmp_path, ROOT)["structure_valid"]
    (tmp_path / "manifest.json").write_text('{"id":"a","id":"b"}')
    rejected(tmp_path, "duplicate_key")
    (tmp_path / "manifest.json").write_text('{"total":NaN}')
    rejected(tmp_path, "nonfinite")


@pytest.mark.parametrize("existing_result", [False, True])
def test_cli_is_offline_and_schema_machine_readable(
    monkeypatch, capsys, trusted_root, package, existing_result
):
    if existing_result:
        record = manifest(package)
        record["kind"] = "result"  # Test data only; never submitted as genuine evidence.
        save(package, record)
        shutil.copytree(package, trusted_root / "submissions/synthetic-counter/r001")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("No commands may execute"))
    base = ["--repo", str(trusted_root), "submission"]
    assert cli.main([*base, "validate", str(EXAMPLE)]) == 0
    assert json.loads(capsys.readouterr().out)["review_status"] == "unverified"
    assert cli.main([*base, "schema", "manifest"]) == 0
    assert json.loads(capsys.readouterr().out)["additionalProperties"] is False
    assert cli.main([*base, "validate-all", str(trusted_root / "submissions")]) == 0
    assert json.loads(capsys.readouterr().out)["count"] == int(existing_result)


def test_new_policy_must_match_frozen_task_and_have_negative_checks(tmp_path):
    # A contributor can add a policy without changing the immutable Harbor task.
    shutil.copytree(ROOT / "datasets", tmp_path / "datasets")
    (tmp_path / "policies").mkdir()
    policy = copy.deepcopy(json.loads((ROOT / "policies/counter-calibration-v1.json").read_text()))
    policy["id"] = "counter-calibration-v2"
    policy["allow_followups"] = True
    path = tmp_path / "policies/counter-calibration-v2.json"
    path.write_bytes(s.encode(policy))
    loaded, _, _ = s.load_policy(tmp_path, policy["id"])
    assert loaded.allow_followups is True
    policy["task"]["instruction_sha256"] = "0" * 64
    path.write_bytes(s.encode(policy))
    with pytest.raises(s.InvalidSubmission, match="Frozen task"):
        s.load_policy(tmp_path, policy["id"])


def test_trusted_review_blocks_rewriting_or_deleting_accepted_data(package, tmp_path):
    trusted = tmp_path / "trusted"
    incoming = tmp_path / "incoming"
    shutil.copytree(ROOT / "datasets", trusted / "datasets")
    shutil.copytree(ROOT / "policies", trusted / "policies")
    record = manifest(package)
    record["kind"] = "result"
    save(package, record)
    shutil.copytree(package, trusted / "submissions/synthetic-counter/r001")
    shutil.copytree(trusted / "submissions", incoming)
    assert s.validate_tree(incoming, trusted)["structure_valid"]
    previous = incoming / "synthetic-counter/r001"
    altered = manifest(previous)
    altered["author"] = "Changed after review"
    save(previous, altered)
    result = s.validate_tree(incoming, trusted)
    assert result["errors"][0]["code"] == "immutable_revision"
    save(previous, record)
    (previous / "observations.txt").unlink()
    assert s.validate_tree(incoming, trusted)["errors"][0]["code"] == "immutable_revision"


def test_correction_adds_revision_without_replacing_original(package, tmp_path, trusted_root):
    tree = tmp_path / "incoming"
    first = tree / "synthetic-counter/r001"
    second = tree / "synthetic-counter/r002"
    shutil.copytree(package, first)
    record = manifest(first)
    record["kind"] = "result"
    save(first, record)
    shutil.copytree(first, trusted_root / "submissions/synthetic-counter/r001")
    shutil.copytree(first, second)
    record["revision"] = 2
    record["publication"]["limitations"].append("Corrected disclosure; original retained.")
    save(second, record)
    result = s.validate_tree(tree, trusted_root)
    assert result["structure_valid"], result
    assert result["count"] == 2


def test_revision_gap_rejected(package, tmp_path, trusted_root):
    tree = tmp_path / "incoming"
    destination = tree / "synthetic-counter/r002"
    shutil.copytree(package, destination)
    record = manifest(destination)
    record.update(kind="result", revision=2)
    save(destination, record)
    assert s.validate_tree(tree, trusted_root)["errors"][0]["code"] == "revision"


def test_manifest_cannot_smuggle_escaped_secret(package):
    record = manifest(package)
    record["environment"] = "sk-" + "x" * 30
    encoded = json.dumps(record).replace("sk-", "\\u0073k-")
    (package / "manifest.json").write_text(encoded)
    rejected(package, "sensitive_text")


def test_large_file_fails_before_read(package):
    with (package / "observations.txt").open("wb") as stream:
        stream.truncate(s.MAX_FILE + 1)
    rejected(package, "file_size")


@pytest.mark.parametrize("name", ["auth.json", "credentials.json", "storage-state.json"])
def test_session_files_are_not_allowed(name):
    with pytest.raises(s.InvalidSubmission, match="session-state"):
        s.relative_path(name)


def test_prepared_export_never_spawns_upload(package, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("Unexpected upload"))
    assert (
        cli.main(
            [
                "--repo",
                str(ROOT),
                "submission",
                "prepare",
                str(package),
                "--output",
                str(tmp_path / "ready"),
                "--confirm-public",
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["uploaded"] is False
    assert set(result["files"]) == {
        "manifest.json",
        "creation.jsonl",
        "evaluation.jsonl",
        "observations.txt",
    }
