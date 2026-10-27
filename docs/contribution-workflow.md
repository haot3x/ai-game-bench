# Contribution → checks → review

One public repository, one evidence package, one result PR. No private workspace,
invitation process or private-to-public export service is part of this version.
See [submission instructions](submissions.md) and [public-data terms](../README.md#public-data-and-privacy-terms).

## Choose an entry point

- **Ready to submit:** follow the submission guide and open a result PR. No
  prior invitation or Discussion is needed.
- **New method or platform:** use [Ideas](https://github.com/mopan-ai/ai-game-bench/discussions/new?category=ideas)
  to agree scope before a large change, or open a small scoped PR.
- **Need help:** ask in [Q&A](https://github.com/mopan-ai/ai-game-bench/discussions/categories/q-a).
- **Want to share an existing result:** [Show and tell](https://github.com/mopan-ai/ai-game-bench/discussions/new?category=show-and-tell)
  can link its PR; it does not replace evidence review.

[Platform support](../platforms/README.md) distinguishes tested agent-operated
workflows from public CLI integrations. None of these entry points starts a paid model run.

| Contribution | Entry | Checks | Decision |
| --- | --- | --- | --- |
| Existing-task result | PR under `submissions/<id>/rNNN/` | Schema, frozen policy, file hashes, event consistency, score recomputation, privacy heuristics | Maintainer evidence review and any isolated replay |
| New task / policy | Scoped PR; Ideas optional | Contract parsing, reference and negative tests; add task-specific free calibration | Approve method/version before a formal result |
| Platform adapter | PR; Ideas optional | Mocked lifecycle tests, package build | Separately authorized real smoke |

## GitHub Actions

| Trigger | Workflow | Effect |
| --- | --- | --- |
| PR opened/updated, push main | Public checks | Ruff/pytest, submission/policy validation, package build, free browser and Oracle/Nop calibration |
| Maintainer manual dispatch | Public checks | Repeat the same free checks |
| PR Public checks completes; submission files changed | Trusted evidence review | Validate current PR-head data with main's code/policies; post a structural-only receipt |
| Maintainer manual dispatch with a PR number | Trusted evidence review | Repeat for the current head, including existing PRs after rollout |
| Issue / Discussion | None | Conversation only; no model, upload, merge or deployment |

Open [Public checks](https://github.com/mopan-ai/ai-game-bench/actions/workflows/checks.yml)
or [Trusted evidence review](https://github.com/mopan-ai/ai-game-bench/actions/workflows/review-submission.yml)
to inspect actual runs. If an external PR is waiting for workflow approval, a
maintainer must inspect its workflow/code changes and approve the run first.
The contributor does not need to supply repository secrets or model keys.

The trusted review workflow uses a reviewed main revision, not PR code. It reads
incoming submissions as data, never installs their dependencies or executes their
scripts. External media is not downloaded. Old-head, closed and non-result PRs
are skipped. A policy/checker change on main does not automatically revisit all
open results; dispatch those explicitly when needed.
A new policy must be merged before formal submissions can pass this independent
structural check. The initial bootstrap PR cannot be checked by a main-branch
validator that does not exist yet; use the reviewed local revision first.

Checks run on GitHub-hosted runners with read-only permissions. Only the isolated
receipt job has `pull-requests: write`, to post a comment; it checks out main only,
reads no evidence/artifacts, and cannot write repository contents. Outside
contributors' Public checks require maintainer approval. PR CI itself is not a
tamper-proof judge: inspect changes to checks/workflows before approving.
No auto-merge, paid runs, raw-job upload or landing deployment.
Maintainer-funded reruns require separate approval of the task, revision,
platform, attempts, time and spending.

## Result PR: who does what?

1. **Contributor:** prepare/validate the public package, check privacy/rights and
   submit the PR. Fix structural errors without hiding failed game attempts.
2. **Maintainer:** approve external CI when safe. Trusted evidence review then
   follows automatically for result PRs; inspect its exact-head receipt (manual
   dispatch remains available). Both required Public checks must also pass.
3. **Maintainer:** inspect screenshots/trajectories, perform any stated replay,
   and record the decision, limitations and exact reviewed head/manifest hashes.
   Passing Actions alone is not approval; changed evidence needs a new review.
4. **Maintainer:** merge an accepted revision manually. Website publication, if
   selected, is a separate curated change in the landing repository.

Record **structural validation**, **evidence review**, **artifact replay** and
**generation rerun** separately; use **not performed** where applicable. There
is no requirement to rerun every creation and no generic "authentic" badge.
Record the exact reviewed head SHA in the PR. A changed head needs a new review.
[Maintainer checklist](reviewing-submissions.md) · [Live settings](github-setup.md)
