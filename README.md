# AI Game Bench

An open, evidence-first benchmark for AI game creation.

Initiated by [Mopan](https://github.com/mopan-ai).
Results are published at [aigamebench.com](https://www.aigamebench.com/).

**Public preview:** free local calibration, six tested platform workflows and
offline submission tools. The six creator integrations are not yet runnable
through `agb run`. [Current capabilities and limits](docs/project-state.md).

[Quick start](#quick-start) · [Platforms](#platform-support) ·
[Contribute](#contributing) · [Documentation](docs/README.md)

## Quick start

Fork this repository, clone your fork, then install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync --locked
uv run agb platforms
uv run agb submission policies
uv run agb submission validate examples/submissions/synthetic-counter
```

The example is invented format-test data, **not** a game score. These commands
need no Docker or platform account, call no models and upload nothing.

### Run the free calibration

Start Docker, then:

```bash
uv run agb doctor
./scripts/run-smoke.sh
uv run agb view
```

Oracle should score 1, Nop 0, with no model calls. First use downloads dependencies
and browser images. Harbor owns runs and local `jobs/`. [Runbook](docs/running.md).

## Tasks and evaluation

| Task | What is available |
| --- | --- |
| [Click counter](datasets/smoke-create-v0.2/create-click-counter-zh-001/) | Free Harbor/Docker/Chromium calibration; automated interaction checks, not a game-quality score |
| [Classic Tetris](protocols/tetris-browser-pilot-v1/evaluation.md) | Browser observation and evidence protocol; no automatic creator or calibrated game judge |

Choose a task and freeze its policy before recording. Keep creation evidence
separate from evaluation, and preserve failures, gaps and unknown values.
[Evaluation boundaries](docs/architecture.md) · [Add a task or policy](docs/adding-tasks.md).

**Example submission:** [Mopan Gemini 4 Tetris](submissions/mopan-gemini4-tetris-20261014/)
was [accepted with limitations](https://github.com/mopan-ai/ai-game-bench/pull/4#issuecomment-6162702189).
It contains public trajectories, evidence, cost and scoring addenda: three
revisions of one creation, not three attempts. This affiliated, non-blind pilot
is not independently reproduced generation or a calibrated leaderboard.
[Historical reports](reports/README.md) are references, not reproduced results.

## Platform support

These platforms have been tested through **agent-operated workflows**.
`Tested` means a recorded test was performed, not that every game passed or that
the platform is certified. Each guide links to the corresponding report.

| Platform | Status | Execution |
| --- | --- | --- |
| <img src="platforms/mopan/logo.png" width="24" height="24" alt=""> &nbsp; [Mopan](platforms/mopan/README.md) | Tested | Browser tool use |
| <img src="platforms/taptap-maker/logo.svg" width="24" height="24" alt=""> &nbsp; [TapTap Maker](platforms/taptap-maker/README.md) | Tested | Browser tool use |
| <img src="platforms/astrocade/logo.svg" width="24" height="24" alt=""> &nbsp; [Astrocade](platforms/astrocade/README.md) | Tested | Browser tool use |
| <img src="platforms/manus/logo.svg" width="24" height="24" alt=""> &nbsp; [Manus](platforms/manus/README.md) | Tested | Browser tool use |
| <img src="platforms/codex/logo.png" width="24" height="24" alt=""> &nbsp; [Codex](platforms/codex/README.md) | Tested | CLI |
| <img src="platforms/claude-code/logo.png" width="24" height="24" alt=""> &nbsp; [Claude Code](platforms/claude-code/README.md) | Tested | CLI |

Reusable CLI integrations are planned. `agb run` currently executes only free
Harbor Oracle/Nop counter calibration, not these six creators.
[Support levels and setup](platforms/README.md) · [Add a platform](docs/platforms.md)

## Contributing

No invitation is required. Humans and agents follow the same guides.

| I want to… | Start here |
| --- | --- |
| Submit a test result | [Record evidence → prepare a public package → open one PR](docs/submissions.md) |
| Add a task or evaluation policy | [Task contribution guide](docs/adding-tasks.md) |
| Add a platform | [Integration contract](docs/platforms.md) |
| Report a wrong verdict | [Open an issue](https://github.com/mopan-ai/ai-game-bench/issues/new?template=bug.yml) with reproduction evidence |
| Discuss an idea or ask for help | [Ideas](https://github.com/mopan-ai/ai-game-bench/discussions/categories/ideas) · [Q&A](https://github.com/mopan-ai/ai-game-bench/discussions/categories/q-a) |

Read the public-data terms below **before uploading**. Existing-task results go
directly to a PR; no prior Discussion or private workspace is required.

PR checks validate code, packages and free calibration. Maintainers separately
run trusted evidence checks and review the claims before merging. Green checks
are not evidence approval; website publication is a separate curated decision.
Discussions and submissions do not trigger paid runs or automatic deployment.

[Contribution guide](CONTRIBUTING.md) · [Actions and triggers](docs/contribution-workflow.md)
· [Maintainer review](docs/reviewing-submissions.md) · [Governance](GOVERNANCE.md)

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

## Roadmap

- **Planned:** reusable platform integrations through the unified CLI.
- **Planned:** simpler evidence recording and packaging.
- **Contributions welcome:** new game tasks, platform guides and independent reviews.

## Contributors

| Contributor | Contribution |
| --- | --- |
| <img src="platforms/mopan/logo.png" width="24" height="24" alt=""> &nbsp; [Mopan](https://github.com/mopan-ai) | Project initiation and maintenance |

Task authors, platform integrators and reviewers are welcome through the
[contribution guide](CONTRIBUTING.md). Tested platforms are not automatically
contributors or endorsers. [Logo sources and attribution](platforms/LOGOS.md).
