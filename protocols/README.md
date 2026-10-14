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
