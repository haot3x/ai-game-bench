# Contribution, automation and publication

This document distinguishes the **local workflow definitions in this preview**
from proposed future automation. Nothing here implies GitHub settings or remote
services have been enabled.

## Three contribution paths

| Submit | Minimum contents | Automatic check / build | Human decision |
| --- | --- | --- | --- |
| Task PR | Versioned Harbor task, rubric, Oracle, broken fixtures, license | Parse contracts, test verifier, build environment, free calibration | Does this measure a useful game capability without shortcuts? |
| Platform PR | Harbor adapter/config, setup instructions, fake-site or mocked tests | Lint/unit tests, lifecycle contract, Python package build | Authorized real smoke, then mark integration supported |
| Result proposal | Task/policy versions, platform/model/effort, all attempts, timing/cost provenance, game/evidence references, limitations | Initially reference metadata checks; full evidence packaging and report build are planned | Review evidence/rights; independently reproduce only with separate approval |

Anyone can propose these through an issue or fork/PR. Initial merge authority is
Mopan maintainers only. A private evidence workspace is optional, not a barrier
for ordinary code fixes or public-safe task contributions.

## Actions included in this preview

File: [checks.yml](../.github/workflows/checks.yml).

| Event | Job | What runs / is built | What it does not do |
| --- | --- | --- | --- |
| PR opened/updated/reopened | `checks-and-package` | Locked dependencies, Ruff, pytest, task/report-reference checks, wheel + source distribution, CLI dry run | No package publish, no accounts |
| Same PR event | `browser-calibration` | Docker browser image; positive/broken browser fixtures; Harbor Oracle/Nop and reward assertions | No paid generation or website interaction |
| Push to main | Both jobs again | Verify merged revision | No automatic website deploy |
| Maintainer manual `workflow_dispatch` | Both jobs | Repeat free checks | No extra privilege or spending |

The fixed counter is exercised end to end. New tasks must explicitly add their
free tests; task discovery does not prove every new Dockerfile was built.
No `pull_request_target`, model keys, private profiles or self-hosted workstation
runner. No raw job upload. GitHub branch rules must be configured separately.

There are three different meanings of **build**: a Python package build verifies
installability; a task image build verifies the execution environment; a report
build renders data for readers. None means "ask a paid agent to create a game".
Only the first two exist here; report rendering stays in the landing repository.

## Proposed private evidence path — not implemented

Borrow the workspace idea from OpenRSI, but make maintainer approval the first
gate and keep running a model separate from creating a repository:

```text
public proposal → maintainer approves an exact revision
    → private evidence workspace → contributor runs locally and submits evidence
    → private checks + human review → sanitized public result PR
    → separate landing-site publication PR
```

Suggested future workflows (names are proposals, not available commands):

| Trigger | Proposed action | Required boundary |
| --- | --- | --- |
| Proposal issue opened/edited | Check fields, label task/platform/result; request missing data | Free deterministic checks first; no automatic LLM reviewer |
| Maintainer approves / manual dispatch | Provision one private evidence repository from a pinned template; invite contributor | Recheck actual permission and proposal hash; least-privilege GitHub App; no model calls |
| Contributor requests validation in private workspace | Validate manifest, scan secrets, check file hashes and evidence completeness | Private repo contents are still untrusted; no provisioning/model token on executor |
| Maintainer approves a bounded rerun | Run trusted revision with named task, platform, attempts, time/spend caps | Protected execution context and separately approved credentials; never arbitrary PR code |
| Maintainer approves publication | Create a public PR containing only reviewed export files | No visibility switch on the private repo; never copy full history |
| Public result PR merged | Prepare a landing-site update pinned to that revision | Separate deployment review; no public PR access to Vercel secrets |

Private workspaces would hold a manifest linking proposal revision, task/rubric
versions, CLI/Harbor version, evidence hashes and review state; `task/`, `evidence/`
and `review/` directories plus a short README. Pin the public framework dependency
instead of copying an entire runtime into every repository. Large recordings
should use a controlled artifact store, not grow every Git history indefinitely.

Operational requirements before enabling provisioning:

- One workspace per accepted proposal/version; duplicate events must reuse it.
  Proposal edits invalidate an older approval. Record who approved what.
- Default private visibility; contributor accesses only that workspace. Mopan
  organization base permissions must not inadvertently expose all workspaces.
- Cross-repo creation uses a dedicated GitHub App, not a personal all-repo token.
  Repository creation authority is separate from code execution and publication.
- Contributor data never chooses an arbitrary organization, collaborator list,
  shell command or privileged workflow revision. Validate all inputs.
- Record retention and consent; no automatic archive/delete/visibility changes.
- Private does not mean safe to store secrets. Upload task-scoped scrubbed
  evidence, not entire personal sessions, cookies or API credentials.
- Account-only games can support private review, but public reports must disclose
  that readers cannot independently replay the same artifact.

Keep the two core repositories. Optional evidence repositories are per-contribution
workspaces, not a third copy of the framework or another result database. If a
private orchestration repository becomes necessary, decide it explicitly; do not
put untrusted execution into the landing deployment pipeline.

## Acceptance is not verification

Use separate labels: proposal accepted, checks passed, evidence reviewed,
independently reproduced, published. A green format check proves neither gameplay
quality nor benchmark validity. Initial historical reports remain labeled as
historical observations, with their original limitations.

Recommended sequence: finish free contribution checks → one manually provisioned
private workspace dry run → automation with a GitHub App → optional approved
reruns → curated report publication. No auto-merge or automatic paid judging first.
