# Governance and repository controls

Mopan AI maintains the initial release. External contributors can propose tasks,
platforms, verifier improvements and results. Only designated Mopan maintainers
approve official entries and merge. Benchmark criteria must be platform-neutral;
Mopan submissions disclose affiliation and follow the same evidence requirements.

This policy is not a claim of institutionally independent governance. Additional
maintainers/partners can be added through an explicit governance change.

## Required setup before accepting outside PRs

These are administrator actions, **not configured by the files in this branch**:

- Protect `main`: PR required, at least one eligible Mopan maintainer approval,
  dismiss stale approvals, resolve review conversations, require CI checks.
- Restrict writes to the maintainer group; block force pushes/deletion and
  restrict bypass permissions. Review membership periodically.
- Configure CODEOWNERS with a real Mopan team that has repository write access.
  The example file is intentionally not active until the team is confirmed.
- Require code-owner review for workflows, evaluation policy, dependency locks
  and public report entries. CODEOWNERS alone does not enforce approval.
- Use GitHub-hosted ephemeral runners for untrusted PRs; approve first-time
  contributors' workflows. No shared model keys, production tokens or Chrome
  profiles on these runners.
- Enable private vulnerability reporting and GitHub secret scanning/protection
  where available. Automated scanning does not replace a publication review.

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
