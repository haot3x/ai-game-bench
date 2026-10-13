# Governance and repository controls

Mopan AI maintains the initial release. External contributors can propose tasks,
platforms, verifier improvements and results. Only designated Mopan maintainers
approve official entries and merge. Benchmark criteria must be platform-neutral;
Mopan submissions disclose affiliation and follow the same evidence requirements.

This policy is not a claim of institutionally independent governance. Additional
maintainers/partners can be added through an explicit governance change.

## Initial single-maintainer workflow

The initial designated maintainer is [@haot3x](https://github.com/haot3x).
The maintainer may author and manually merge the same PR after checks pass.
GitHub does not allow authors to approve their own PR, so the required approval
count is **zero**, not a fictional self-approval or an administrator bypass.
External contributors can propose changes but cannot merge just because CI passes.

The intended `main` controls are recorded in
[main-protection.json](.github/main-protection.json). They require a PR, both CI
jobs on an up-to-date branch, and resolved review conversations. Force pushes,
branch deletion and explicit PR bypasses are disabled; rules apply to admins.
The write allowlist names the initial maintainer. Existing organization owners
retain their GitHub administrative authority; this does not remove their access.

[CODEOWNERS](.github/CODEOWNERS) names the initial maintainer for review routing.
Code-owner approval and last-pusher approval are **not** mandatory while there
is only one participating maintainer. No auto-merge is enabled. Manual merge is
the maintainer's acceptance decision, not evidence of an independent review or
an independently reproduced benchmark result.

These files do not apply GitHub settings themselves. An administrator must apply
the configuration and read it back; see
[the setup and audit runbook](docs/github-setup.md).

Before adding another maintainer, explicitly update the allowlist/CODEOWNERS and
decide whether to require one independent approval and code-owner review.

## Contributor execution safety

- Use GitHub-hosted ephemeral runners for untrusted PRs. Require maintainer
  approval for every outside collaborator's workflow run; inspect workflow and
  Dockerfile changes before approving execution.
- Keep the default workflow token read-only and disallow Actions from approving
  PRs. No shared model keys, production tokens or Chrome profiles on runners.
- CI checks the submitted code; it is not a tamper-proof evaluator. A maintainer
  must inspect changes to checks, task versions and result evidence before merge.
- Review secret scanning/protection and private vulnerability reporting
  separately. Automated scanning does not replace a publication review.

Required checks after their first successful GitHub run:
`checks-and-package` and `browser-calibration` in `Public checks`.
The workflow has no path-level trigger filter, so docs-only PRs still report
required checks rather than leaving them pending indefinitely.

## Publication authority

Public framework CI cannot write to the landing repository. Website publication
requires a separate curated update/PR in that repository. A result author cannot
grant themselves an independently-reproduced badge. Maintainers document review
evidence and conflicts of interest; they do not edit native historical runs.

Private evidence workspaces, if adopted, give the contributor access only to
their workspace—not main-repo write access or other contributors' data. Creation
authority belongs to a narrowly scoped provisioning service, never untrusted PR
code. See the [proposed workflow](docs/contribution-workflow.md).
