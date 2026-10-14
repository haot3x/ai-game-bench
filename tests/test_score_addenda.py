"""Synthetic arithmetic and rejection tests, not real-game evidence."""

import copy
import json

import pytest
from test_browser_protocol import EXAMPLE, ROOT, fictional_attempt

from ai_game_bench import submissions as s
from ai_game_bench.score_addenda import STANDARD, ScoreAddendum, recompute, validate_addenda
from ai_game_bench.submission_models import Submission


@pytest.fixture
def context():
    attempt, policy, prompt, blobs = fictional_attempt(1800)
    manifest = json.loads((EXAMPLE / "manifest.json").read_text())
    manifest.update(policy_id=policy.id, source_kind="browser_observation")
    manifest["policy_sha256"] = s.load_policy(ROOT, policy.id)[1]
    attempt.result.mode = "human"
    manifest["attempts"] = [attempt.model_dump()]
    manifest["files"] = [
        {"path": path, "sha256": s.digest(data), "bytes": len(data)} for path, data in blobs.items()
    ]
    source_bytes = s.encode(manifest)
    blobs["source-manifest.json"] = source_bytes
    manifest["revision"] = 2
    submission = Submission.model_validate(manifest)
    standard = json.loads((ROOT / STANDARD).read_text())
    data = {
        "schema_version": "tetris-absolute-assessment/1",
        "policy_sha256": s.digest((ROOT / STANDARD).read_bytes()),
        "source_revision": 1,
        "source_manifest": "source-manifest.json",
        "source_manifest_sha256": s.digest(source_bytes),
        "attempt_id": attempt.id,
        "assessed_at": "2026-01-02T00:00:00Z",
        "provenance": "retrospective_operator_evidence_review",
        "note": "Synthetic arithmetic only, not real observations.",
        "mechanics": {
            key: {"status": "passed", "reason": "Synthetic", "evidence_events": ["e-observe"]}
            for key in standard["mechanics"]
        },
        "experience": {
            key: {"rating": 8, "reason": "Synthetic", "evidence_events": ["e-observe"]}
            for key in standard["experience"]
        },
        "user_cost": {
            "cost_index": None,
            "cny_per_unit": None,
            "fx_evidence": [],
            "reason": "Unknown",
        },
        "computed": {},
    }
    return data, submission, policy, blobs, set(blobs), standard


def calculate(ctx):
    data, *rest = ctx
    return recompute(ScoreAddendum.model_validate(data), *rest)


def test_fixed_standard_and_partial_coverage(context):
    assert context[-1]["weights"] == {
        "mechanics": 40,
        "experience": 20,
        "time": 20,
        "user_cost": 20,
    }
    result = calculate(context)
    assert result == {
        "status": "provisional",
        "total": 82.5,
        "points": 66.0,
        "scored_weight": 80,
        "evidence_weight": 80,
        "interval": [66.0, 86.0],
        "core_passed": 9,
        "elapsed_seconds": 1800.0,
        "groups": {"mechanics": 40.0, "experience": 16.0, "time": 10.0, "user_cost": None},
    }


def test_unobserved_core_is_zero_not_unallocated(context):
    context[0]["mechanics"]["opens"].update(status="not_tested", evidence_events=[])
    result = calculate(context)
    assert result["scored_weight"] == 80
    assert result["evidence_weight"] == 76
    assert result["total"] == 77.5


def test_unknown_experience_remains_unallocated(context):
    for item in context[0]["experience"].values():
        item.update(rating=None, evidence_events=[])
    result = calculate(context)
    assert result["scored_weight"] == 60
    assert result["groups"]["experience"] is None


@pytest.mark.parametrize("amount,points", [(0, 20), (5, 18), (20, 14), (50, 8), (100, 0), (200, 0)])
def test_user_cost_anchors(context, amount, points):
    context[0]["user_cost"].update(cost_index=0, cny_per_unit=1.0)
    context[1].costs[0] = (
        context[1]
        .costs[0]
        .model_copy(
            update={
                "kind": "actual_charge",
                "component": "creator",
                "currency": "CNY",
                "amount": float(amount),
                "evidence": ["observations.txt"],
            }
        )
    )
    result = calculate(context)
    assert result["groups"]["user_cost"] == points
    assert result["scored_weight"] == 100


@pytest.mark.parametrize("rating", [True, 1.5, -1, 11])
def test_experience_scale_is_integer_zero_to_ten(context, rating):
    context[0]["experience"]["board_legibility"]["rating"] = rating
    with pytest.raises(ValueError):
        calculate(context)


@pytest.mark.parametrize("change", ["reference", "missing", "time", "provenance", "cost"])
def test_unsupported_claims_rejected(context, change):
    data = context[0]
    if change == "reference":
        data["mechanics"]["opens"]["evidence_events"] = ["invented"]
    elif change == "missing":
        del data["experience"]["board_legibility"]
    elif change == "time":
        data["assessed_at"] = "2025-01-01T00:00:00Z"
    elif change == "provenance":
        data["provenance"] = "independent"
    else:
        data["user_cost"].update(cost_index=0, cny_per_unit=1.0)
        context[1].costs[0] = (
            context[1]
            .costs[0]
            .model_copy(
                update={
                    "kind": "model_estimate",
                    "amount": 1.8,
                    "currency": "USD",
                    "evidence": ["observations.txt"],
                }
            )
        )
    with pytest.raises(ValueError):
        calculate(context)


@pytest.mark.parametrize(
    "tamper", [None, "hash", "total", "unlisted", "duplicate", "source-hash", "original-bytes"]
)
def test_addendum_is_allowlisted_hashed_recomputed(context, tamper):
    data, submission, policy, blobs, references, _ = context
    data["computed"] = calculate(context)
    path = "assessment.json"
    submission.score_addenda = [path]
    if tamper == "hash":
        data["policy_sha256"] = "0" * 64
    if tamper == "total":
        data["computed"]["total"] = 99
    blobs[path] = s.encode(data)
    if tamper == "unlisted":
        del blobs[path]
    if tamper == "duplicate":
        submission.score_addenda.append(path)
    if tamper == "source-hash":
        data["source_manifest_sha256"] = "0" * 64
        blobs[path] = s.encode(data)
    if tamper == "original-bytes":
        blobs["observations.txt"] = b"Changed original evidence"
    if tamper:
        with pytest.raises(ValueError):
            validate_addenda(submission, policy, blobs, references, ROOT)
    else:
        result = validate_addenda(submission, policy, blobs, references, ROOT)
        assert result[0]["computed"]["total"] == 82.5


def test_original_pilot_result_is_unchanged(context):
    original = copy.deepcopy(context[1].attempts[0].result.model_dump())
    calculate(context)
    assert context[1].attempts[0].result.model_dump() == original


def test_infrastructure_failure_has_no_numeric_total(context):
    context[1].attempts[0].outcome = "infrastructure_error"
    assert calculate(context) == {"status": "infrastructure_error", "total": None}


@pytest.mark.parametrize("tamper", [None, "source", "mode", "sum"])
def test_full_validation_calls_addendum_checker(context, tmp_path, tamper):
    data, submission, policy, blobs, refs, _ = context
    data["computed"] = calculate(context)
    if tamper == "sum":
        data["computed"]["total"] = 99
    submission.attempts[0].result.mode = "human"
    submission.policy_sha256 = s.load_policy(ROOT, policy.id)[1]
    submission.score_addenda = ["assessment.json"]
    blobs["assessment.json"] = s.encode(data)
    if tamper == "source":
        submission.source_kind = "harbor"
    if tamper == "mode":
        submission.attempts[0].result.mode = "deterministic"
    record = submission.model_dump()
    record["files"] = []
    for path, content in blobs.items():
        (tmp_path / path).write_bytes(content)
        record["files"].append({"path": path, "sha256": s.digest(content), "bytes": len(content)})
    (tmp_path / "manifest.json").write_bytes(s.encode(record))
    result = s.validate(tmp_path, ROOT)
    assert result["structure_valid"] is (tamper is None), result
    if not tamper:
        assert result["score_addenda"][0]["computed"]["total"] == 82.5
