# Upstream contribution and Actions research

Reviewed 2026-10-13. These are patterns to adapt, not dependencies to copy in full.

## SWE-bench experiments: entries separate from evidence

Its current contribution model puts metadata/result summaries in the experiments
repository and artifacts in a submitter-owned public repository. The validation
workflow checks changed entries, warns about historical entries and checks that
leaderboard data compiles. Independent verification is a separate process.

Apply here: small public result entries and explicit evidence provenance; do not
equate a successful report build with rerunning a creator. We do not adopt its
institutional eligibility restrictions or require inaccessible model reasoning.

Sources: [submission guide](https://github.com/SWE-bench/experiments/blob/40f164d5b8f1d249bf95a6df8b74b577fd8e519d/README.md),
[validation workflow](https://github.com/SWE-bench/experiments/blob/40f164d5b8f1d249bf95a6df8b74b577fd8e519d/.github/workflows/validate.yml).

## Harbor: runnable task packages and adapter evidence

Harbor separates Python tests from adapter review. The adapter review workflow
contains structural checks and an explicit comment-triggered review route; its
requirements include Oracle success and parity evidence. Contribution guidance
requires contributors to understand submitted code and discuss core changes.

Apply here: task package + reference + negative tests, one Harbor runtime, small
CLI wrapper. Do not copy paid AI review, permission choices or upstream latest
interfaces blindly; this preview pins Harbor 0.22.0.

Sources: [contribution guide](https://github.com/harbor-framework/harbor/blob/4778ceba98314a3b0fe119249f7ac84fc0af08b7/CONTRIBUTING.md),
[adapter review](https://github.com/harbor-framework/harbor/blob/4778ceba98314a3b0fe119249f7ac84fc0af08b7/.github/workflows/adapter-review.yml).

## BrowserGym: browser CI without paid inference

BrowserGym's test workflow installs Chromium, runs local browser fixtures and
excludes tests marked `pricy`. Some external-environment jobs are disabled/gated;
their presence is not evidence that every external site runs on every PR.
Its package workflow separates building distributions from tag-gated publishing.

Apply here: real browser calibration in free CI; live authenticated SaaS checks
belong to a separately approved lane. Package build is not package publication.

Sources: [test workflow](https://github.com/ServiceNow/BrowserGym/blob/e71419aef5759a11cb7896a26c36e5f7e92d82b2/.github/workflows/unit_tests.yml),
[package workflow](https://github.com/ServiceNow/BrowserGym/blob/e71419aef5759a11cb7896a26c36e5f7e92d82b2/.github/workflows/pypi.yml).

## OpenRSI: public intake, private workspace, reviewed publication

The public guide describes proposal review followed by a private task workspace
with validation/run instructions. Approval does not guarantee final inclusion.
Public workflows use GitHub App tokens to dispatch to a private worker. Their
publication check reads proposed data using base-revision policy, separately from
testing the proposed checker. The private provisioning implementation is not
established by the public workflow alone.

Apply here: optional private evidence workspace after Mopan maintainer approval;
separate artifact review from public release. Do not automatically upload personal
agent histories, adopt an RSI training goal, or enable paid task generation.
An authorized private workspace was inspected for structure only; no private
contents or identifiers are included in this public research note.

Sources: [contribution flow](https://github.com/OpenRSI-Foundation/OpenRSI-Index/blob/6ff5f4ac77be56a915aa052833a8ef67e4f61639/CONTRIBUTING.md),
[private dispatch](https://github.com/OpenRSI-Foundation/OpenRSI-Index/blob/6ff5f4ac77be56a915aa052833a8ef67e4f61639/.github/workflows/discussion-task-dispatch.yml),
[publication guard](https://github.com/OpenRSI-Foundation/OpenRSI-Index/blob/6ff5f4ac77be56a915aa052833a8ef67e4f61639/.github/workflows/task-log-publication-checks.yml).

## Security and scope

The workflow `GITHUB_TOKEN` is scoped to its repository; cross-repo provisioning
needs separately authorized credentials. Prefer narrowly scoped GitHub App
tokens. Privileged jobs must never run untrusted PR scripts with those tokens.
Checks from a PR's own revision are development tests, not tamper-proof gates.

Sources: [GitHub token scope](https://docs.github.com/en/actions/concepts/security/github_token),
[secure Actions use](https://docs.github.com/en/actions/reference/security/secure-use).

Our initial workflow deliberately implements only free checks/builds. Trusted-base
publication validation, evidence packaging, auto-provisioning, official reruns and
cross-repo publication remain separate milestones. See the
[implementation/proposal matrix](../contribution-workflow.md).
