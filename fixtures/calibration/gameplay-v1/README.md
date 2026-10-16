# Local gameplay references

Two original, dependency-free fixtures and deliberate faults for the proposed
[platformer](../../../protocols/platformer-browser-pilot-v1/acceptance.md) and
[racing](../../../protocols/racing-3d-browser-pilot-v1/acceptance.md) methods.
These are small **behavior examples**, not generated games, polished passing
submissions, hidden test sets or replacements for the public evaluation rules.
No model, account, paid service, downloaded art or game engine is required.
Code and drawn shapes are original and covered by the repository's
[Apache-2.0 license](../../../LICENSE).

## Play the examples

From the repository root:

```bash
python3 -m http.server 8091 --bind 127.0.0.1 --directory fixtures/calibration/gameplay-v1
```

- Platformer: `http://127.0.0.1:8091/?game=platformer`
- Racing: `http://127.0.0.1:8091/?game=racing`
- Fault example: `http://127.0.0.1:8091/?game=platformer&defect=cosmetic-jump`
- Fault example: `http://127.0.0.1:8091/?game=racing&defect=unordered-checkpoints`

Select Start, then use the displayed keys. Restart is ordinary game UI. Mutation
selection happens only when loading a fixture; it is not a gameplay debug API.
In the reference racing scene, hold accelerate + right to follow the circular
track. This is a known fixture route, **not a walkthrough for a submitted game**.
The entire level/map fits on screen to keep reference behavior inspectable;
passing these examples does not validate side-scrolling quality or 3D aesthetics.

## Replay and inspect

```bash
./scripts/test-gameplay-calibration.sh
```

The pinned Chromium container has no external network, accounts or repository
mount. Each run gets a fresh ignored `artifacts/gameplay-calibration/run.*`
directory. It contains task-scoped videos, before/after screenshots, normal
keyboard/button actions, visible observations, per-probe JSON and a summary.
Run twice into separate directories to check repeatability. Failed checks retain
evidence too. Nothing is uploaded or included in a result PR automatically.

[cases.json](cases.json) lists 15 focused pass/fault pairs, plus two mobile layout
checks. `none` is the working reference; a listed mutation should fail its named
probe. A mutation may break other behavior as well. Reference geometry and HUD
are read through visible DOM/SVG; no game source, private state, injected events,
clock manipulation or teleporting is used **during replay**. Tests deliberately
know the fixture structure, so this is not blind evaluation.

The tests can catch broken probes and examples. They do **not** estimate an AI
judge's false-pass rate on real games. In particular, a moving minimap marker is
not sufficient evidence of a real game's 3D acceleration/camera; the recordings
must show the world scene. Ready, camera, visual/experience quality and complete
criterion semantics still require review. There is no generation-time/cost score
for hand-authored fixtures.

## Gate before Mopan

1. Review both acceptance cards and replay the controls; flag unclear or impossible
   checks. The reference is a behavioral illustration, not pixel-perfect ground truth.
2. Require both repetitions of the fixture checks to agree. Fix the checker or
   reference if they disagree; retain the failed local run and explanation.
3. Test the **actual intended independent evaluator** on balanced reference/fault
   cases. Give it only the game-only surface and the criterion; use opaque case
   IDs/URLs and do not expose mutation names, source, expected answers or this
   catalog. The operator must hold the answer key separately. No model calls are
   made by this package.
4. Report false passes (fault called pass), false failures (reference called fail),
   abstentions/not-tested, infrastructure errors and agreement across repeated
   evaluations, with denominators and evidence. Do not count abstentions as correct
   fault detection. Hold out additional faults/layout variants before claiming
   generalization; the public examples are teaching cases, not a benchmark score.
5. A maintainer approves the method revision, unresolved limitations and the live
   pilot. Only then run Mopan with explicit authorization. Retain existing weights,
   60-minute creation / 30-minute evaluation budgets and all historical results.

Full independent-evaluator calibration and live creation are separate gates;
green fixture tests alone do not satisfy them.
