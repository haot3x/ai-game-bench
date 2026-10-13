# Working in the public AI Game Bench repository

Read [docs/README.md](docs/README.md), then [project state](docs/project-state.md)
and [architecture](docs/architecture.md). Run `git status --short` before edits.

- Harbor owns execution, sandboxes, jobs, retries, artifacts and viewing.
  `agb` is a thin entry point, not another runner or database.
- The public preview runs a free, deterministic counter calibration. Six
  creator platforms have references under `platforms/`, not working adapters.
- Keep game verification independently runnable: files in, plain JSON out.
- Do not change frozen task prompts, rubrics or verifier bytes in place. Add a
  version; retain old results and explain comparability changes.
- Infrastructure errors are not scored game failures. The counter's binary
  reward is not a game-quality score or a leaderboard result.
- Never copy private history, jobs, credentials, browser profiles, account data,
  production prompts or unreviewed assets into this repository.
- Do not call models, remote creation services, publish, commit or push without
  explicit authorization. Free Docker/Oracle/Nop checks are safe defaults.
- Do not modify product APIs, databases, private landing site or its deployment.
- Run `./verify.sh`. For runtime/verifier changes also run
  `./scripts/test-browser.sh` and `./scripts/run-smoke.sh`, inspect native results,
  and state what did and did not run. Do not claim GitHub enforcement is active
  merely because a workflow or governance document exists locally.
- Keep contributions narrow; see [CONTRIBUTING.md](CONTRIBUTING.md).
