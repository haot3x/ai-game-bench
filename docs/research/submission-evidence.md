# Submission and evidence design — proposal

This is a proposed contribution contract, not a new runner, storage format or
implemented submission CLI. Native Harbor records remain canonical locally.

## What the public OpenRSI example establishes

[Discussion #209](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/209)
records a proposal moving through review, task preparation, validation and a
private-workspace invitation. Later Discussion edits did not regenerate the
already-created task. Experiment completion still required maintainer review;
formal-score saturation prompted a harder revision and short pilot. This is a
useful separation of packaging readiness, execution and scientific acceptance.

The [contribution guide](https://github.com/OpenRSI-Foundation/OpenRSI-Index/blob/6ff5f4ac77be56a915aa052833a8ef67e4f61639/CONTRIBUTING.md)
requests proposal-session evidence separately from the experiment trajectory.
For our project, task-scoped evidence should be the default; unrelated personal
or company conversations are not a submission requirement.

No private repository contents are reproduced in this design.

## Evidence to request for AI Game Bench

| Evidence group | Minimum content | Why it matters |
| --- | --- | --- |
| Contract | Exact prompt/task, rubric/policy versions, hashes, requirements, reference and failure semantics | Establish what was tested; prevent changing the exam afterward |
| Run conditions | Framework/agent/platform version, model/effort or unknown, account tier, browser/runtime, time limits, attempts, follow-up policy | Make limits and comparison differences visible |
| Creation process | Accepted prompt, relevant clarification turns, actual Send/start/end events, meaningful milestones, gaps, all attempts | Distinguish output quality from operator intervention and creation efficiency |
| Final artifact | Frozen playable bundle/hash or URL/build identity + observation time and access limits | Ensure evidence points at the same game version |
| Evaluation | Inputs/actions, timestamped observations, screenshots/video snippets, per-criterion verdict/reason/evidence, verifier hash | Connect a judgment to observed behavior, not a creator's claim |
| Usage and review | Tokens/credits with provenance, cost estimate vs actual charge, human annotations, rights/redaction record, review status | Audit cost, consent, exclusions and level of assurance |

Unknown metadata must be explicit, never invented. A hosted game without source
remains admissible if its supported evidence is clear; do not demand source export
as a universal submission condition. Loss of exact replay must be disclosed.

Cost of creator, browser operator and evaluator should be recorded separately.
Both model-price estimates and user credit valuations can be retained, but a
comparison must use the same declared basis and exchange-rate date. Missing
usage/cost does not become free usage.

## Different contributions need different proof

- New task: reference pass, empty/broken failures, replay stability, licensing,
  and a small weak/strong-policy pilot where relevant. A low weak baseline alone
  does not prove useful headroom. Do not change scores merely to make them lower.
- New platform adapter: fake-site lifecycle tests plus a bounded authorized real
  submission-to-game run. Test wrong profile, login expiry, clarification,
  missing Send, premature completion and timeout. Never require a shared login.
- New result: complete attempt accounting, final artifacts, evidence-linked
  scoring and comparable conditions. A screenshot of a total score is not enough.

Run a short diagnostic pilot before expensive multi-platform batches. Keep
development observations, first formal submission, best submission and final
submission distinct. More submissions on the same games are not more independent
games or repeated independent trials.

## Proposed submission experience

1. Contributor describes task/platform/result in one proposal. A helper can
   explain missing fields; maintainers retain acceptance authority.
2. Ordinary code uses a fork/PR. Sensitive evidence uses an approved private
   workspace with a pinned setup and one documented entry command.
3. Contributor runs locally with their own authorized account. A future packager
   prepares a file allowlist, hashes and a redaction/omission manifest for preview.
4. Upload only after confirming destination and scope. Verify remote commit/file
   hashes; local generation or commit alone is not a completed submission.
5. Free automated checks validate structure and completeness. Maintainers review
   substantive evidence; official paid reproduction needs separate approval.
6. Publish only a reviewed export through a public PR, then a separate landing
   update. Private evidence stays private.

The exact `agb` packaging/upload command and machine schema are not implemented
yet. Finalize them with one manually reviewed contribution rather than hiding
unimplemented automation behind a command name.

## Do not copy these requirements blindly

No expertise-based exclusion for ordinary community contributions; evaluate the
work and its evidence. No automatic full-session upload. No automatic acceptance
because an LLM reviewer says PASS. No mandatory long RSI run for a Create Bench
task. No automatic paid execution for every proposal edit. Preserve an explicit
appeal/revision path when an automated review is wrong.

Proposed statuses: `proposed → approved → packaged → execution_validated →
evidence_reviewed → independently_reproduced (optional) → published`.
Record the reviewed revision for every status; a changed rubric invalidates an
older acceptance. Publishing a self-reported result need not imply reproduction,
but its status must remain visible to readers.
