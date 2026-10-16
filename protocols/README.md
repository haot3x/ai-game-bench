# Manual browser protocols

These versioned, data-only protocols describe observable tests of hosted games.
They are **not executable Harbor tasks**, unattended adapters or calibrated AI
judges. `agb run` continues to accept only Harbor packages under `datasets/`.

Each protocol contains a prompt, identity, rubric and evaluation procedure.
A file in `policies/` pins those bytes. The public submission validator checks
records, references and arithmetic; a maintainer must still inspect the evidence.
No submitted game or script is executed by this lane.

- [Classic Tetris pilot v1](tetris-browser-pilot-v1/evaluation.md): one fresh
  browser creation, normal player input, nine core checks and four UX checks.
  This is a new pilot scale, not comparable to historical website scores.

## Contributor proposals — not approved or run

- [2D platformer v1](platformer-browser-pilot-v1/evaluation.md): pixel-art level,
  movement/jump, solid platforms, coins, loss/win and both restart paths.
  [Acceptance steps and examples](platformer-browser-pilot-v1/acceptance.md).
- [3D racing v1](racing-3d-browser-pilot-v1/evaluation.md): low-poly timed lap,
  driving/camera, boundaries, ordered checkpoints, finish and restart.
  [Acceptance steps and examples](racing-3d-browser-pilot-v1/acceptance.md).

See the [method proposal and Mopan validation plan](../docs/proposals/platformer-racing-pilot.md).
Their policies parse locally, but listing them is not maintainer approval.
Existing Tetris/counter versions and historical results are unchanged.
The [local reference fixtures](../fixtures/calibration/gameplay-v1/README.md)
exercise focused pass/fault probes, not a general or independently calibrated judge.
