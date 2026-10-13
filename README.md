# AI Game Bench

An open benchmark for evaluating AI systems that create games. Tasks, evidence
and evaluation methods should be inspectable and useful to any creator agent.
Initially maintained by Mopan AI; not an independent governance body yet.

**Public foundation preview.** Today this checkout runs a free click-counter
calibration end to end through Harbor, Docker and Chromium. It does **not** yet
automate the six creator platforms or establish a general game-quality ranking.

## Try it locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and start
Docker (Docker Desktop on macOS). Python 3.12 is managed by uv. From this checkout:

```bash
uv sync --locked
uv run agb doctor
./scripts/run-smoke.sh
```

The smoke runs a known-working game (Oracle, expected **1**) and an empty
submission (Nop, expected **0**). It makes no model calls and uses no account.
First run downloads a large browser image; package/image downloads need internet,
but the game and verifier containers run without external network access.

```bash
uv run agb tasks
uv run agb platforms
uv run agb platforms mopan
uv run agb run --agent oracle --job-name my-first-run
uv run agb inspect jobs/my-first-run --expect 1
uv run agb view
```

View results at `http://127.0.0.1:8080`. Harbor's Viewer may build its frontend
on first use (requires Node/npm). Raw jobs remain local and ignored by Git.
See [running locally](docs/running.md) for checks and troubleshooting.

## Contribute

- **Tasks:** an instruction, runnable environment, rubric, reference solution
  and positive/negative verifier tests—not just a prompt.
- **Platform integrations:** a Harbor agent/configuration, login/setup recipe,
  free contract tests and explicitly approved end-to-end evidence.
- **Results:** reproducible metadata and rights-reviewed evidence; a score alone
  is insufficient. Existing reports are listed in [reports/](reports/README.md).
- **Evaluation fixes:** minimal examples of false passes, missed defects or
  instability. Changes to released criteria need a new version.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Read the
[contribution → CI → review flow](docs/contribution-workflow.md) and
[current platform boundaries](docs/platforms.md).
The six [platform directories](platforms/README.md) explain the historical
Codex, Claude Code, Mopan, TapTap Maker, Manus and Astrocade connection methods,
artifact handoff and usage evidence. Each has machine-readable metadata and a
runbook; reference availability is separate from executable adapter readiness.

## Project boundaries

This repository contains the public framework, task definitions and contribution
policy. [aigamebench.com](https://aigamebench.com/) is a separate presentation
site. A framework PR never deploys the website or spends platform credits.
Private run history is not included. Public report references do not make the
underlying private runs reproducible.

Code and authored calibration fixtures: [Apache-2.0](LICENSE). Third-party
contributions must document their own provenance and redistribution rights.
