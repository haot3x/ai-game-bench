"""Method/export tests only. These fixtures do not generate or play games."""

from __future__ import annotations

import json
import shutil
import socket
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from ai_game_bench import cli
from ai_game_bench import submissions as s

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/submissions/synthetic-counter"
METHODS = ("platformer-browser-pilot-v1", "racing-3d-browser-pilot-v1")
UX = {"readability", "guidance", "feedback", "presentation"}


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Method/export tests must not connect to a platform or model")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def recalculate(record, policy):
    result = record["attempts"][0]["result"]
    scores = {v["criterion_id"]: v["score"] for v in result["criteria"]}
    result["total"] = round(sum(c.weight * scores[c.id] / 10 for c in policy.criteria), 6)


def synthetic_package(tmp_path, method, seconds=1950):
    """Invented test-only records; never report them as real gameplay evidence."""
    policy, sha, prompt = s.load_policy(ROOT, method)
    record = json.loads((EXAMPLE / "manifest.json").read_text())
    record.update(
        id="synthetic-" + method,
        policy_id=method,
        policy_sha256=sha,
        source_kind="browser_observation",
        source_ref="synthetic-no-actual-game",
    )
    record["creator"]["platform"] = "synthetic-fixture"
    attempt = record["attempts"][0]
    attempt["artifact"].update(
        kind="public_url", url="https://example.com/synthetic-game", bundle_sha256=None
    )
    attempt["result"].update(mode="agent_visual", creation_context_hidden=False)
    time_score = round(10 * max(0, min(1, (3600 - seconds) / 3300)), 6)
    attempt["result"]["criteria"] = [
        {
            "criterion_id": c.id,
            "status": "passed" if score == 10 else "partial" if score else "failed",
            "score": score,
            "reason": "Invented arithmetic fixture, not a gameplay observation.",
            "evidence_events": ["e-observe"],
        }
        for c in policy.criteria
        for score in [time_score if c.id == "delivery-time" else 10]
    ]
    recalculate(record, policy)
    creation = [json.loads(line) for line in (EXAMPLE / "creation.jsonl").read_text().splitlines()]
    evaluation = [
        json.loads(line) for line in (EXAMPLE / "evaluation.jsonl").read_text().splitlines()
    ]
    start = datetime(2026, 1, 1, tzinfo=UTC)
    creation[0]["at"] = start.isoformat()
    creation[1].update(at=(start + timedelta(seconds=1)).isoformat(), prompt=prompt)
    creation[-1]["at"] = (start + timedelta(seconds=seconds + 1)).isoformat()
    for i, event in enumerate(evaluation):
        event["at"] = (start + timedelta(seconds=seconds + i + 2)).isoformat()
    package = tmp_path / method
    package.mkdir()
    blobs = {
        "creation.jsonl": b"\n".join(json.dumps(e).encode() for e in creation) + b"\n",
        "evaluation.jsonl": b"\n".join(json.dumps(e).encode() for e in evaluation) + b"\n",
        "observations.txt": b"Hypothetical format/arithmetic fixture. No game or browser was run.",
    }
    for name, data in blobs.items():
        (package / name).write_bytes(data)
    record["files"] = [
        {"path": name, "sha256": s.digest(data), "bytes": len(data)} for name, data in blobs.items()
    ]
    save(package, record)
    return package, record, policy


def save(package, record):
    (package / "manifest.json").write_bytes(s.encode(record))


def rewrite_events(package, record, filename, edit):
    events = [json.loads(line) for line in (package / filename).read_text().splitlines()]
    edit(events)
    data = b"\n".join(json.dumps(e).encode() for e in events) + b"\n"
    (package / filename).write_bytes(data)
    entry = next(f for f in record["files"] if f["path"] == filename)
    entry.update(sha256=s.digest(data), bytes=len(data))
    save(package, record)


def reject(package, code):
    result = s.validate(package, ROOT)
    assert not result["structure_valid"], result
    assert result["errors"][0]["code"] == code, result


@pytest.mark.parametrize("method", METHODS)
def test_proposal_contract_is_platform_neutral_and_not_executable(method):
    policy, sha, prompt = s.load_policy(ROOT, method)
    directory = ROOT / "protocols" / method
    assert tomllib.loads((directory / "task.toml").read_text())["protocol"]["status"] == "proposed"
    assert policy.task.kind == "browser_protocol"
    assert policy.prompt_mode == "full_instruction"
    assert prompt == (directory / "instruction.md").read_text()
    assert all(name not in prompt.lower() for name in ("mopan", "gemini", "harbor", "rubric"))
    assert len(sha) == 64
    assert policy.attempt_limit == 1 and policy.timeout_seconds == 3600
    assert policy.allow_followups and not policy.allow_repairs
    assert policy.artifact_kinds == ["public_url"]
    assert all(c.max_score == 10 for c in policy.criteria)
    assert len([c for c in policy.criteria if not c.allow_partial]) == 9
    assert sum(c.weight for c in policy.criteria if not c.allow_partial) == 60
    assert sum(c.weight for c in policy.criteria if c.id in UX) == 10
    assert next(c.weight for c in policy.criteria if c.id == "delivery-time") == 30
    assert sum(c.weight for c in policy.criteria) == 100
    assert policy.time_score.full_credit_seconds == 300
    with pytest.raises(ValueError, match="existing directory"):
        cli.task_directory(ROOT, method)


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("filename", ["instruction.md", "rubric.json", "evaluation.md"])
def test_proposal_edits_invalidate_pinned_method(tmp_path, method, filename):
    for directory in ("policies", "protocols"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    (tmp_path / "protocols" / method / filename).write_text("Changed draft bytes")
    with pytest.raises(s.InvalidSubmission, match="Frozen task bytes"):
        s.load_policy(tmp_path, method)


@pytest.mark.parametrize("method", METHODS)
def test_authored_review_cases_are_explicitly_hypothetical(method):
    policy, _, _ = s.load_policy(ROOT, method)
    data = json.loads((ROOT / "protocols" / method / "review-cases.json").read_text())
    assert data["kind"] == "hypothetical_review_cases_not_run_evidence"
    assert len({c["id"] for c in data["cases"]}) == len(data["cases"])
    assert {c["criterion_id"] for c in data["cases"]} <= {c.id for c in policy.criteria}
    assert {c["expected"]["status"] for c in data["cases"]} == {
        "passed",
        "failed",
        "not_tested",
        "infra_error",
    }
    for case in data["cases"]:
        expected = case["expected"]
        assert case["observation"] and expected["reason"]
        assert (
            expected["score"]
            == {"passed": 10, "failed": 0, "not_tested": 0, "infra_error": None}[expected["status"]]
        )


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("seconds,total", [(30, 100), (300, 100), (1950, 85), (3600, 70)])
def test_synthetic_export_recomputes_time_without_claiming_verification(
    tmp_path, method, seconds, total
):
    package, _, _ = synthetic_package(tmp_path, method, seconds)
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert result["kind"] == "synthetic_example"
    assert result["review_status"] == "unverified"
    assert result["attempts"][0]["recomputed_total"] == total


@pytest.mark.parametrize("method", METHODS)
def test_every_time_gate_blocks_speed_credit_if_not_demonstrated(tmp_path, method):
    package, record, policy = synthetic_package(tmp_path, method, 30)
    original = json.loads(json.dumps(record))
    for gate in policy.time_score.required_passes:
        record = json.loads(json.dumps(original))
        by_id = {v["criterion_id"]: v for v in record["attempts"][0]["result"]["criteria"]}
        by_id[gate].update(status="not_tested", score=0, evidence_events=[])
        recalculate(record, policy)
        save(package, record)
        reject(package, "time_score")
        by_id["delivery-time"].update(status="failed", score=0)
        recalculate(record, policy)
        save(package, record)
        result = s.validate(package, ROOT)
        assert result["structure_valid"], result
        assert result["attempts"][0]["recomputed_total"] < 70


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("status", ["failed", "not_tested"])
def test_zeroes_keep_full_denominator_and_distinct_reasons(tmp_path, method, status):
    package, record, policy = synthetic_package(tmp_path, method)
    for verdict in record["attempts"][0]["result"]["criteria"]:
        verdict.update(status=status, score=0, reason=f"Synthetic {status} case")
    recalculate(record, policy)
    save(package, record)
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert result["attempts"][0]["recomputed_total"] == 0


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "mutation,code",
    [
        ("missing-criterion", "criteria"),
        ("missing-evidence", "missing_evidence"),
        ("partial-core", "score"),
        ("forged-total", "total"),
        ("forged-policy", "policy"),
        ("deterministic-claim", "source"),
        ("second-attempt", "attempts"),
    ],
)
def test_invalid_claims_are_rejected(tmp_path, method, mutation, code):
    package, record, _ = synthetic_package(tmp_path, method)
    attempt = record["attempts"][0]
    match mutation:
        case "missing-criterion":
            attempt["result"]["criteria"].pop()
        case "missing-evidence":
            attempt["result"]["criteria"][0]["evidence_events"] = []
        case "partial-core":
            attempt["result"]["criteria"][0].update(status="partial", score=5)
        case "forged-total":
            attempt["result"]["total"] = 99
        case "forged-policy":
            record["policy_sha256"] = "0" * 64
        case "deterministic-claim":
            attempt["result"]["mode"] = "deterministic"
        case "second-attempt":
            record["attempts"].append(json.loads(json.dumps(attempt)))
    save(package, record)
    reject(package, code)


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "outcome", ["build_failure", "timeout", "auth_failure", "infrastructure_error"]
)
def test_failed_generation_and_infrastructure_remain_distinct(tmp_path, method, outcome):
    package, record, _ = synthetic_package(tmp_path, method)
    attempt = record["attempts"][0]
    attempt.update(outcome=outcome, artifact=None)
    infra = outcome != "build_failure"
    for verdict in attempt["result"]["criteria"]:
        verdict.update(status="infra_error" if infra else "failed", score=None if infra else 0)
    attempt["result"]["total"] = None if infra else 0
    rewrite_events(
        package, record, "creation.jsonl", lambda es: es[-1].update(kind=outcome, artifact_id=None)
    )
    rewrite_events(
        package, record, "evaluation.jsonl", lambda es: [e.update(artifact_id=None) for e in es]
    )
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert result["attempts"][0]["recomputed_total"] == (None if infra else 0)


@pytest.mark.parametrize("method", METHODS)
def test_contributor_can_prepare_synthetic_export_but_draft_is_never_authorized(tmp_path, method):
    draft = tmp_path / "unapproved"
    s.initialize(ROOT, draft, method, "draft-not-a-result")
    record = json.loads((draft / "manifest.json").read_text())
    assert record["publication"]["public_release_confirmed"] is False
    assert record["source_kind"] == "browser_observation"
    assert (draft / "creation.jsonl").read_bytes() == b""
    assert not s.validate(draft, ROOT)["structure_valid"]
    package, _, _ = synthetic_package(tmp_path, method)
    output = tmp_path / "synthetic-export"
    with pytest.raises(s.InvalidSubmission, match="confirm-public"):
        s.prepare(package, ROOT, output, confirmed=False)
    s.prepare(package, ROOT, output, confirmed=True)
    result = s.validate(output, ROOT)
    assert result["structure_valid"] and result["kind"] == "synthetic_example"
    assert result["review_status"] == "unverified"


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "mutation,code",
    [
        ("changed-prompt", "prompt"),
        ("repair", "repair_policy"),
        ("unasked-followup", "followup_policy"),
        ("missing-acceptance", "missing_send"),
        ("different-build", "artifact_mismatch"),
    ],
)
def test_creation_and_handoff_rules_survive_export(tmp_path, method, mutation, code):
    package, record, _ = synthetic_package(tmp_path, method)

    def edit(events):
        if mutation == "changed-prompt":
            events[1]["prompt"] += " Extra help from the operator."
        elif mutation == "missing-acceptance":
            events.pop(1)
        elif mutation == "different-build":
            events[1]["artifact_id"] = "another-game"
        else:
            events.insert(
                2,
                {
                    "seq": 3,
                    "id": "c-extra",
                    "at": events[1]["at"],
                    "kind": "repair" if mutation == "repair" else "followup",
                    "detail": "Synthetic unauthorized extra input",
                    "evidence": ["observations.txt"],
                },
            )
        for seq, event in enumerate(events, 1):
            event["seq"] = seq

    stream = "evaluation.jsonl" if mutation == "different-build" else "creation.jsonl"
    rewrite_events(package, record, stream, edit)
    reject(package, code)


@pytest.mark.parametrize("method", METHODS)
def test_late_delivery_and_favorable_time_are_rejected(tmp_path, method):
    package, record, policy = synthetic_package(tmp_path, method, 3601)
    reject(package, "time_limit")
    rewrite_events(
        package, record, "creation.jsonl", lambda es: es[-1].update(at="2026-01-01T00:32:31+00:00")
    )
    time = next(
        v
        for v in record["attempts"][0]["result"]["criteria"]
        if v["criterion_id"] == "delivery-time"
    )
    time.update(status="passed", score=10)
    recalculate(record, policy)
    save(package, record)
    reject(package, "time_score")


@pytest.mark.parametrize("method", METHODS)
def test_unknown_cost_and_documented_partial_ux_do_not_change_denominator(tmp_path, method):
    package, record, policy = synthetic_package(tmp_path, method)
    record["costs"] = [
        {
            "kind": "unknown",
            "component": "creator",
            "amount": None,
            "currency": None,
            "basis": "Synthetic unavailable user-facing cost, not a real run.",
            "evidence": [],
        }
    ]
    guidance = next(
        v for v in record["attempts"][0]["result"]["criteria"] if v["criterion_id"] == "guidance"
    )
    guidance.update(status="partial", score=7.3, reason="Hypothetical intermediate UX rating.")
    recalculate(record, policy)
    save(package, record)
    result = s.validate(package, ROOT)
    assert result["structure_valid"], result
    assert result["attempts"][0]["recomputed_total"] == 84.325
