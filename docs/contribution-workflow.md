# Contribution → checks → review

One public repository, one evidence package, one result PR. No private workspace,
invitation process or private-to-public export service is part of this version.
See [submission instructions](submissions.md) and [public-data terms](../README.md#public-data-and-privacy-terms).

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
| Maintainer manual dispatch with a PR number | Trusted evidence review | Pin PR head; validate its data using the dispatch revision's trusted code, dependencies and policies |
| Issue / Discussion | None | Conversation only; no model, upload, merge or deployment |

The trusted review workflow must be dispatched from a reviewed main revision,
after it is merged. It reads incoming submissions as data, never installs their
dependencies or executes their scripts. External media is not downloaded.
A new policy must be merged before formal submissions can pass this independent
structural check. The initial bootstrap PR cannot be checked by a main-branch
validator that does not exist yet; use the reviewed local revision first.

All Actions run on GitHub-hosted runners with read-only permissions. Outside
contributors' workflow runs require maintainer approval. PR CI itself is not a
tamper-proof judge: inspect changes to checks/workflows before approving.
No auto-merge, paid runs, raw-job upload or landing deployment.

Checks passed → evidence reviewed → artifact replayed (if performed) →
generation independently reproduced (only if actually rerun) are separate claims.
Record the exact reviewed head SHA in the PR. A changed head needs a new review.
[Maintainer checklist](reviewing-submissions.md) · [Live settings](github-setup.md)
