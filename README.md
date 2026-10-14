# AI Game Bench

An open, evidence-first benchmark for AI game creation. Initially maintained by
Mopan AI; not an independent governance body. The same rules apply to Mopan and
outside submissions.

**Current scope:** one free Harbor/Docker/Chromium click-counter calibration,
six platform connection guides, and offline public-submission tools. A separate
[Tetris browser pilot](protocols/tetris-browser-pilot-v1/evaluation.md) provides
manual observation rules, not an automatic creator or calibrated game judge.
Historical reports are references, not reproduced results or comparable scores.

## Submit a result

Fork this repository, clone your fork, then install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync --locked
uv run agb submission policies
uv run agb submission validate examples/submissions/synthetic-counter
```

The example is invented format-test data, **not** a game score. Submission tools
do not require Docker, connect accounts, call models or upload anything.

[Start a submission](docs/submissions.md) — humans and agents follow the same
guide: record locally → prepare an allowlisted public package → open one PR.
Existing-task results do not require a prior Discussion or a private workspace.

Missing a task or policy? [Contribute one](docs/adding-tasks.md).
Platform connection methods: [platforms/](platforms/README.md).
Maintainers: [review untrusted evidence](docs/reviewing-submissions.md).

## Public-data and privacy terms

- **Everything you push to a public fork, PR, issue or Discussion is public
  immediately, even before acceptance.** Do not upload first and redact later.
- Publish only task-scoped evidence you have reviewed and have rights to share:
  relevant dialogue/actions, screenshots, game references, verdicts and cost
  provenance. Declare the evidence's license and any affiliation.
- Never upload credentials, cookies, Chrome profiles, unrelated conversations,
  full account/billing pages, signed URLs, private assets or whole raw jobs.
  Original Harbor records stay local; the submission is a reviewed export.
- Declare redactions, capture gaps and unknown values. If a necessary claim
  cannot be supported publicly, leave it unverified; do not silently omit proof.
- Agents need the owner's explicit publication approval before pushing. Automated
  scans are a backstop, not a privacy guarantee. Forks/caches may retain copies
  after deletion. Report accidental disclosure [privately](SECURITY.md).

By submitting, you confirm permission for public distribution and benchmark
review/display under the declared license. You retain your ownership. Code and
authored fixtures use [Apache-2.0](LICENSE); third-party evidence must state its
actual license. No additional training-data agreement is inferred from submission;
reuse follows the applicable license.

## Run the free calibration

Start Docker, then:

```bash
uv run agb doctor
./scripts/run-smoke.sh
uv run agb view
```

Oracle should score 1, Nop 0, with no model calls. First use downloads dependencies
and browser images. Harbor owns runs and local `jobs/`; the binary score is not
game quality. [Runbook](docs/running.md) · [Current state](docs/project-state.md)

## Contribute and review

A PR receives free package, policy and calibration checks. CI passing does not
verify a game's claims or grant merge rights. Mopan maintainers review and merge;
website publication is a separate curated update. No automatic paid runs,
private repository provisioning or deployment.

[Contribution guide](CONTRIBUTING.md) · [Actions and triggers](docs/contribution-workflow.md)
· [Governance](GOVERNANCE.md) · [Reports](reports/README.md)
