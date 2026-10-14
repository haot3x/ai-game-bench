"""Recompute explicitly retrospective reports; never replace a frozen run score."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .submission_models import ID, Hash, Record, Text, timestamp

STANDARD = "scoring/tetris-absolute-v1.json"


class Core(Record):
    status: Literal["passed", "failed", "not_tested"]
    reason: Text
    evidence_events: list[ID]


class Experience(Record):
    rating: Annotated[int, Field(ge=0, le=10)] | None
    reason: Text
    evidence_events: list[ID]


class UserCost(Record):
    cost_index: Annotated[int, Field(ge=0)] | None
    cny_per_unit: Annotated[float, Field(gt=0, allow_inf_nan=False)] | None
    fx_evidence: list[Text]
    reason: Text


class ScoreAddendum(Record):
    schema_version: Literal["tetris-absolute-assessment/1"]
    policy_sha256: Hash
    source_revision: Annotated[int, Field(ge=1, le=999)]
    source_manifest: Text
    source_manifest_sha256: Hash
    attempt_id: ID
    assessed_at: Text
    provenance: Literal["retrospective_operator_evidence_review"]
    note: Text
    mechanics: dict[Text, Core]
    experience: dict[Text, Experience]
    user_cost: UserCost
    computed: dict


def recompute(record, submission, policy, blobs, references, standard):
    """Evidence references and timing come from the validated original attempt."""
    from .submissions import load_events, require

    require(policy.id == "tetris-browser-pilot-v1", "score_addendum", "Wrong source protocol.")
    attempt = next((a for a in submission.attempts if a.id == record.attempt_id), None)
    require(attempt is not None, "score_addendum", "Unknown source attempt.")
    creation = load_events(blobs[attempt.creation], "creation", references)
    evaluation = load_events(blobs[attempt.evaluation], "evaluation", references)
    require(
        timestamp(record.assessed_at) >= timestamp(evaluation[-1].at),
        "score_addendum",
        "Retrospective assessment cannot precede its evidence.",
    )
    observations = {e.id for e in evaluation if e.kind == "observation" and e.evidence}
    points = 0.0
    scored_weight = 0
    evidence_weight = 0
    groups = {}
    for group in ("mechanics", "experience"):
        values = getattr(record, group)
        require(set(values) == set(standard[group]), "score_addendum", "Missing/extra criterion.")
        group_points = 0.0
        group_known = False
        for key, weight in standard[group].items():
            item = values[key]
            known = item.status != "not_tested" if group == "mechanics" else item.rating is not None
            require(
                set(item.evidence_events) <= observations and (not known or item.evidence_events),
                "score_addendum",
                "Ratings need evidence-backed original evaluation observation IDs.",
            )
            rating = (10 if item.status == "passed" else 0) if group == "mechanics" else item.rating
            if rating is not None:
                group_known = True
                group_points += weight * rating / 10
                scored_weight += weight
            if known:
                evidence_weight += weight
        groups[group] = round(group_points, 6) if group_known else None
        points += group_points

    accepted = [e for e in creation if e.kind == "prompt_accepted"]
    elapsed = (
        (timestamp(creation[-1].at) - timestamp(accepted[0].at)).total_seconds()
        if accepted
        else None
    )
    time_points = (
        None
        if elapsed is None
        else standard["weights"]["time"] * max(0, 1 - elapsed / standard["time_limit_seconds"])
    )
    if time_points is not None:
        points += time_points
        scored_weight += standard["weights"]["time"]
        evidence_weight += standard["weights"]["time"]
    groups["time"] = None if time_points is None else round(time_points, 6)

    cost = record.user_cost
    cost_points = None
    if cost.cost_index is None:
        require(
            cost.cny_per_unit is None and not cost.fx_evidence,
            "score_addendum",
            "Unknown user charge must not invent an exchange rate.",
        )
    else:
        require(cost.cost_index < len(submission.costs), "score_addendum", "Unknown cost index.")
        entry = submission.costs[cost.cost_index]
        require(
            entry.component == "creator"
            and entry.kind in {"actual_charge", "credit_value"}
            and entry.amount is not None
            and entry.evidence,
            "score_addendum",
            "Model estimates cannot substitute for user cost.",
        )
        require(
            cost.cny_per_unit is not None
            and set(cost.fx_evidence) <= references
            and (entry.currency == "CNY" or cost.fx_evidence),
            "score_addendum",
            "Non-CNY user cost needs documented conversion evidence.",
        )
        require(
            entry.currency != "CNY" or cost.cny_per_unit == 1,
            "score_addendum",
            "CNY conversion must be one.",
        )
        amount = entry.amount * cost.cny_per_unit
        curve = standard["cost_curve_linear_points"]
        percent = 0
        for (left, high), (right, low) in zip(curve, curve[1:], strict=False):
            if amount <= right:
                percent = high + (low - high) * (amount - left) / (right - left)
                break
        cost_points = percent * standard["weights"]["user_cost"] / 100
        points += cost_points
        scored_weight += standard["weights"]["user_cost"]
        evidence_weight += standard["weights"]["user_cost"]
    groups["user_cost"] = None if cost_points is None else round(cost_points, 6)
    if attempt.outcome in {"timeout", "auth_failure", "infrastructure_error"} or any(
        c.status == "infra_error" for c in attempt.result.criteria
    ):
        return {"status": "infrastructure_error", "total": None}
    require(
        attempt.outcome == "delivered",
        "score_addendum",
        "Only delivered artifacts can be reassessed.",
    )
    return {
        "status": "complete" if scored_weight == 100 else "provisional",
        "total": round(100 * points / scored_weight, 6),
        "points": round(points, 6),
        "scored_weight": scored_weight,
        "evidence_weight": evidence_weight,
        "interval": [round(points, 6), round(points + 100 - scored_weight, 6)],
        "core_passed": sum(v.status == "passed" for v in record.mechanics.values()),
        "elapsed_seconds": elapsed,
        "groups": groups,
    }


def validate_addenda(submission, policy, blobs, references, root):
    from .submissions import digest, model, parse_json, read_file, require

    paths = submission.score_addenda
    require(len(set(paths)) == len(paths), "score_addendum", "Duplicate score addendum.")
    results = []
    for path in paths:
        require(path in blobs and path.endswith(".json"), "score_addendum", "Unlisted addendum.")
        record = model(ScoreAddendum, parse_json(blobs[path]))
        require(
            record.source_revision < submission.revision
            and record.source_manifest in references
            and record.source_manifest in blobs,
            "score_addendum",
            "Addendum needs an allowlisted earlier source manifest.",
        )
        source_bytes = blobs[record.source_manifest]
        require(
            digest(source_bytes) == record.source_manifest_sha256,
            "score_addendum",
            "Source manifest hash mismatch.",
        )
        from .submission_models import Submission

        source = model(Submission, parse_json(source_bytes))
        require(
            source.revision == record.source_revision and source.id == submission.id,
            "score_addendum",
            "Source must be an earlier revision of the same submission.",
        )
        for field in (
            "kind",
            "policy_id",
            "policy_sha256",
            "author",
            "affiliation",
            "creator",
            "environment",
            "source_kind",
            "source_ref",
            "attempts",
            "external_evidence",
        ):
            require(
                getattr(source, field) == getattr(submission, field),
                "score_addendum",
                "Original run identity and results must remain unchanged.",
            )
        for entry in source.files:
            if entry.path not in {"README.md", "recording-notes.md"}:
                require(
                    entry.path in blobs
                    and digest(blobs[entry.path]) == entry.sha256
                    and len(blobs[entry.path]) == entry.bytes,
                    "score_addendum",
                    "Original evidence bytes must remain unchanged.",
                )
        raw = read_file(root, STANDARD)
        require(
            record.policy_sha256 == digest(raw), "score_addendum", "Scoring policy hash mismatch."
        )
        computed = recompute(record, submission, policy, blobs, references, parse_json(raw))
        require(record.computed == computed, "score_addendum", "Reassessment arithmetic mismatch.")
        results.append(
            {
                "file": path,
                "provenance": record.provenance,
                "computed": computed,
                "source_revision": record.source_revision,
                "source_manifest_sha256": record.source_manifest_sha256,
            }
        )
    return results
