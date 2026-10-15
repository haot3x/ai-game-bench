# GitHub setup and audit

Target: `mopan-ai/ai-game-bench` only. This does not configure the landing site,
other repositories, organization membership or a cross-repository GitHub App.

## Initial policy

- One participating maintainer: `haot3x`; no new collaborators are invited.
- `main` requires PRs and the two free `Public checks` jobs, even for admins.
- Required approvals: **0**. The maintainer can manually merge their own PR
  after checks pass. GitHub self-approval is neither supported nor necessary.
- Required review conversations must be resolved; force push and deletion are
  blocked. Auto-merge remains off. Existing organization owners retain admin
  authority; repository rules cannot revoke that authority.
- Default Actions token: read-only; Actions cannot approve PRs. All outside
  collaborators need maintainer approval before a workflow run. Inspect their
  workflows/scripts/Dockerfiles before approving. No model keys or private profiles.
- Discussions uses Ideas (task/platform proposals), Show and tell (results) and
  Q&A. Forms live in `.github/DISCUSSION_TEMPLATE/` and take effect on `main`.
- Discussions and issues do not trigger an automated reviewer, paid run, private
  repository creation, merge or website publication.
- Result PRs go directly to public `submissions/`; Discussion is optional. The
  `Trusted evidence review` manual workflow checks pinned PR data with trusted
  code/policies; it is not another required PR approval or automatic score judge.
- Secret scanning and push protection should be enabled. Private vulnerability
  reporting is for security incidents, not a private result-submission workflow.

## Administrator application

Policy files: [main-protection.json](../.github/main-protection.json) controls
the intended write allowlist and branch rules; [CODEOWNERS](../.github/CODEOWNERS)
routes reviews. Require `checks-and-package` and `browser-calibration` on an
up-to-date branch, with no PR bypass. Keep both jobs reporting on docs-only PRs.
Before adding a maintainer, update these files and explicitly decide whether
independent approval, code-owner approval and last-pusher approval become required.

The committed policy is a desired configuration, not a self-applying workflow.
Apply only after reviewing the exact repository and confirming the expected
check names and GitHub Actions app ID (`15368`) from a real PR run:

```bash
gh api repos/mopan-ai/ai-game-bench --jq '{full_name,permissions}'
gh api --method PUT repos/mopan-ai/ai-game-bench/branches/main/protection \
  --input .github/main-protection.json
```

This PUT replaces branch protection fields: inspect existing live rules before
reapplying and preserve any newer intentional changes. Never use it as a routine
CI step. Keep independent-approval/code-owner requirements off until another
maintainer is explicitly added; otherwise the sole maintainer's PRs deadlock.

## Read-only verification

```bash
gh api repos/mopan-ai/ai-game-bench --jq '{has_discussions,allow_auto_merge}'
gh api repos/mopan-ai/ai-game-bench/branches/main/protection
gh api repos/mopan-ai/ai-game-bench/rulesets
gh api repos/mopan-ai/ai-game-bench/actions/permissions/workflow
gh api repos/mopan-ai/ai-game-bench/actions/permissions/fork-pr-contributor-approval
gh api repos/mopan-ai/ai-game-bench --jq '.security_and_analysis'
gh api repos/mopan-ai/ai-game-bench/private-vulnerability-reporting
gh run list --repo mopan-ai/ai-game-bench --limit 5
gh pr checks --repo mopan-ai/ai-game-bench PR_NUMBER
```

Verify the returned settings, not merely a successful API status. Tests in this
repo protect the configuration's intended shape but cannot prove remote settings
are enabled. PR checks must come from GitHub Actions, not an arbitrary status
publisher. Require a green result on the exact revision to be merged.

For a normal contribution: open a proposal when needed, create/update a PR,
wait for both checks, inspect the change and evidence, then merge manually. A
failed check blocks merge; fix it and rerun rather than disabling protection.
The public framework remains a source checkout, not a PyPI release.

Audit on 2026-10-14: public visibility, Issues/Discussions, main PR + both checks,
read-only Actions token, all-external-contributor approval and disabled auto-merge
were read back. Secret scanning, push protection and private vulnerability
reporting were enabled and read back. No collaborators or merge permissions were
broadened. PR #3 has since merged the submission workflow, and
[Trusted evidence review](https://github.com/mopan-ai/ai-game-bench/actions/runs/38524647241)
successfully checked the exact result PR #4 head using trusted main code. PR #4
is merged and [main checks passed](https://github.com/mopan-ai/ai-game-bench/actions/runs/38524926580).
The workflow is available for manual dispatch; CI does not grant merge rights
or replace evidence review. Local checks alone still do not establish remote state.

Live evidence: [PRs](https://github.com/mopan-ai/ai-game-bench/pulls),
[Actions](https://github.com/mopan-ai/ai-game-bench/actions),
[Discussions](https://github.com/mopan-ai/ai-game-bench/discussions).
