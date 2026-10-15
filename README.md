# AI Game Bench

An open, evidence-first benchmark for AI game creation.

Initiated by [Mopan](https://github.com/mopan-ai).
Results are published at [aigamebench.com](https://www.aigamebench.com/).

**Current scope:** one free Harbor/Docker/Chromium click-counter calibration,
six platform connection guides, and offline public-submission tools. A separate
[Tetris browser pilot](protocols/tetris-browser-pilot-v1/evaluation.md) provides
manual observation rules, not an automatic creator or calibrated game judge.
Historical reports are references, not reproduced results or comparable scores.

**Accepted pilot:** [Mopan Gemini 4 Tetris](submissions/mopan-gemini4-tetris-20261014/)
contains one real creation, public evidence/trajectories, an owner-reported cost
supplement and a historical-policy score addendum. [Maintainer review](https://github.com/mopan-ai/ai-game-bench/pull/4#issuecomment-6162702189)
accepted it with limitations after trusted checks and a limited artifact replay.
This is non-blind pilot evidence, not independently reproduced generation or a
calibrated leaderboard. Its three revisions are not three attempts.

## Participate

| I want to… | Start here |
| --- | --- |
| Submit a test result | [Record evidence and open one PR](docs/submissions.md) |
| Propose a task, policy or platform | [Open an Ideas discussion](https://github.com/mopan-ai/ai-game-bench/discussions/new?category=ideas) |
| Report a wrong verdict | [Open an issue](https://github.com/mopan-ai/ai-game-bench/issues/new?template=bug.yml) with the result and reproduction evidence |
| Ask for help | [Q&A](https://github.com/mopan-ai/ai-game-bench/discussions/categories/q-a) |

No invitation is required. Discussions do not start models or spend credits.
Results go directly to a PR; a separate Discussion is optional.

## Platform support

These platforms have been tested through **agent-operated workflows**.
`Tested` means a recorded test was performed, not that every game passed or that
the platform is certified. Each guide links to the corresponding report.

| Platform | Status | Execution |
| --- | --- | --- |
| [Mopan](platforms/mopan/README.md) | Tested | Browser tool use |
| [TapTap Maker](platforms/taptap-maker/README.md) | Tested | Browser tool use |
| [Astrocade](platforms/astrocade/README.md) | Tested | Browser tool use |
| [Manus](platforms/manus/README.md) | Tested | Browser tool use |
| [Codex](platforms/codex/README.md) | Tested | CLI |
| [Claude Code](platforms/claude-code/README.md) | Tested | CLI |

Reusable CLI integrations are planned. `agb run` currently executes only free
Harbor Oracle/Nop counter calibration, not these six creators.
[Support levels and setup](platforms/README.md) · [Add a platform](docs/platforms.md)

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

| Stage | What happens |
| --- | --- |
| [Discussion](https://github.com/mopan-ai/ai-game-bench/discussions) | People discuss proposals and questions; no automatic execution |
| [Public checks](https://github.com/mopan-ai/ai-game-bench/actions/workflows/checks.yml) | PR/main checks validate code, packages and free calibration; external runs require maintainer approval |
| [Trusted evidence review](https://github.com/mopan-ai/ai-game-bench/actions/workflows/review-submission.yml) | Maintainer manually checks a result PR using trusted main code, not its submitted checker |
| Evidence review → merge | Maintainer inspects claims and records the decision for the exact PR revision |

Green checks prove neither authentic evidence nor a correct game. Only designated
Mopan maintainers merge. Website publication is a separate curated update;
there is no automatic paid run, private repository creation or deployment.

[Contribution guide](CONTRIBUTING.md) · [Actions and triggers](docs/contribution-workflow.md)
· [Governance](GOVERNANCE.md) · [Reports](reports/README.md)

## Roadmap

- **Planned:** reusable platform integrations through the unified CLI.
- **Planned:** simpler evidence recording and packaging.
- **Contributions welcome:** new game tasks, platform guides and independent reviews.

## Contributors

- [Mopan](https://github.com/mopan-ai)

New contributors are welcome through the [contribution guide](CONTRIBUTING.md).
