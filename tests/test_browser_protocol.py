from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from ai_game_bench import cli
from ai_game_bench import submissions as s
from ai_game_bench.submission_models import Attempt

ROOT = Path(__file__).resolve().parents[1]
POLICY = "tetris-browser-pilot-v1"
EXAMPLE = ROOT / "examples/submissions/synthetic-counter"


def test_manual_protocol_is_frozen_but_not_a_harbor_task():
    policy, sha, prompt = s.load_policy(ROOT, POLICY)
    assert prompt == "一个经典俄罗斯方块"
    assert policy.task.kind == "browser_protocol"
    assert len(sha) == 64
    assert policy.attempt_limit == 1
    assert policy.timeout_seconds == 3600
    assert policy.allow_followups and not policy.allow_repairs
    assert sum(c.weight for c in policy.criteria) == 100
    assert all(c.max_score == 10 for c in policy.criteria)
    with pytest.raises(ValueError, match="existing directory"):
        cli.task_directory(ROOT, POLICY)


@pytest.mark.parametrize("filename", ["instruction.md", "rubric.json", "evaluation.md"])
def test_manual_method_edits_break_the_frozen_identity(tmp_path, filename):
    shutil.copytree(ROOT / "policies", tmp_path / "policies")
    shutil.copytree(ROOT / "protocols", tmp_path / "protocols")
    (tmp_path / "protocols" / POLICY / filename).write_text("changed")
    with pytest.raises(s.InvalidSubmission, match="Frozen task bytes"):
        s.load_policy(tmp_path, POLICY)


def fictional_attempt(duration, *, ready=True, claimed_time=None):
    # Deliberately invented records for arithmetic tests, never publishable results.
    policy, _, prompt = s.load_policy(ROOT, POLICY)
    creation = [json.loads(line) for line in (EXAMPLE / "creation.jsonl").read_text().splitlines()]
    evaluation = [
        json.loads(line) for line in (EXAMPLE / "evaluation.jsonl").read_text().splitlines()
    ]
    from datetime import UTC, datetime, timedelta

    start = datetime(2026, 1, 1, tzinfo=UTC)
    creation[1]["at"] = start.isoformat()
    creation[1]["prompt"] = prompt
    creation[-1]["at"] = (start + timedelta(seconds=duration)).isoformat()
    for i, event in enumerate(evaluation):
        event["at"] = (start + timedelta(seconds=duration + i)).isoformat()
    score = round(10 * max(0, min(1, (3600 - duration) / 3300)), 6) if ready else 0
    score = score if claimed_time is None else claimed_time
    verdicts = []
    for criterion in policy.criteria:
        points = score if criterion.id == "delivery-time" else 10
        if criterion.id == "ready" and not ready:
            points = 0
        verdicts.append(
            {
                "criterion_id": criterion.id,
                "status": "passed" if points == 10 else "partial" if points else "failed",
                "score": points,
                "reason": "Fictional arithmetic test, not observed gameplay.",
                "evidence_events": ["e-observe"],
            }
        )
    record = copy.deepcopy(json.loads((EXAMPLE / "manifest.json").read_text())["attempts"][0])
    record["artifact"].update(
        kind="public_url", url="https://example.com/test-game", bundle_sha256=None
    )
    record["result"]["criteria"] = verdicts
    record["result"]["total"] = round(
        sum(c.weight * v["score"] / 10 for c, v in zip(policy.criteria, verdicts, strict=True)),
        6,
    )
    blobs = {
        "creation.jsonl": "\n".join(json.dumps(e) for e in creation).encode(),
        "evaluation.jsonl": "\n".join(json.dumps(e) for e in evaluation).encode(),
        "observations.txt": b"Entirely invented arithmetic fixture.",
    }
    return Attempt.model_validate(record), policy, prompt, blobs


@pytest.mark.parametrize("seconds,expected", [(30, 100), (300, 100), (1950, 85), (3600, 70)])
def test_time_score_is_recomputed_from_the_observed_timeline(seconds, expected):
    attempt, policy, prompt, blobs = fictional_attempt(seconds)
    result = s.check_attempt(attempt, policy, prompt, blobs, set(blobs), set())
    assert result["recomputed_total"] == expected


def test_fast_but_unplayable_game_gets_no_time_credit():
    attempt, policy, prompt, blobs = fictional_attempt(30, ready=False)
    result = s.check_attempt(attempt, policy, prompt, blobs, set(blobs), set())
    assert result["recomputed_total"] == 64


@pytest.mark.parametrize("ready,claimed", [(True, 10), (False, 1)])
def test_favorable_time_score_cannot_be_claimed(ready, claimed):
    attempt, policy, prompt, blobs = fictional_attempt(1950, ready=ready, claimed_time=claimed)
    with pytest.raises(s.InvalidSubmission, match="Delivery-time credit"):
        s.check_attempt(attempt, policy, prompt, blobs, set(blobs), set())


def test_browser_draft_does_not_claim_native_or_deterministic_verification(tmp_path):
    target = tmp_path / "draft"
    s.initialize(ROOT, target, POLICY, "manual-test")
    record = json.loads((target / "manifest.json").read_text())
    assert record["source_kind"] == "browser_observation"
    assert record["attempts"][0]["result"]["mode"] == "human"


@pytest.mark.parametrize("key", ["line-score", "readability", "guidance", "feedback", "layout"])
def test_discrete_anchors_reject_arbitrary_partial_credit(key):
    attempt, policy, prompt, blobs = fictional_attempt(1950)
    verdict = next(v for v in attempt.result.criteria if v.criterion_id == key)
    verdict.status, verdict.score = "partial", 9.0
    with pytest.raises(s.InvalidSubmission, match="anchors"):
        s.check_attempt(attempt, policy, prompt, blobs, set(blobs), set())
