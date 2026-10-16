# 3D racing acceptance card

Supplemental examples for the [proposed evaluation](evaluation.md), not a change
to its frozen prompt/rubric, weights or budget. Apply the same checks to any
platform. The [local reference pack](../../fixtures/calibration/gameplay-v1/README.md)
is a simple software-projected scene for behavior checks, not an engine benchmark
or a full-score visual reference.

## Setup and capture

Open the final game only at 1280×800 / 100% zoom. Record game URL/build, browser,
viewport, time, initial car position, timer and checkpoint state. Learn controls
from the game, not creation chat/source. Record ordinary inputs, the world scene
and HUD continuously; a speedometer/minimap or screenshot alone cannot establish
vehicle dynamics. Each criterion cites action/observation IDs and clip/frame files.

Budget at most 30 minutes / six sessions. Suggested sequence: (1) controls, camera
and both boundaries; (2) straight-line coast baseline; (3) matched brake comparison
and invalid route probes; (4) uninterrupted valid lap; (5) post-finish restart;
(6) reserve for an unresolved accessible probe. Restarts/reloads count as documented
sessions per policy; never splice separate attempts into a purported legal lap.
Inspect 390×844 separately for layout only, not mobile driving.

## Steps, passing examples and failure examples

| Criterion | Acceptance steps | Passing behavior example | Failing behavior example |
| --- | --- | --- | --- |
| ready | Start and focus; inspect perspective, car, timer/progress; operate the vehicle. | A controllable car in an actual visibly 3D track scene. | A flat mock-up, loading screen or noninteractive animation only. |
| acceleration | Hold throttle on a clear straight; compare car motion against fixed scenery over time. | Vehicle displacement increases from rest. | `hud-only-speed`: speed reading rises but the vehicle stays still. |
| braking | Use the same clear straight and similar initial speed for coast and brake attempts; record comparable time windows. | Brake reduces motion/speed more than coasting, before any obstacle. | `no-brakes` decelerates only through ordinary drag. A wall collision does **not** prove braking. |
| steering | Drive forward and test left and right separately. | Both directions change vehicle heading and path. | `no-steering`: keys animate UI but the car keeps going straight. |
| follow-camera | Drive straight and through a sustained turn; review the scene, not only HUD. | Third-person camera follows with car and upcoming track visible. | `fixed-camera`: the car drives away from a stationary view. Manual visual comparison required. |
| track-bounds | At moderate speed contact outer and inner limits deliberately, then try crossing the infield. | Blocked/constrained/returned with no retained shortcut progress. | `no-boundaries` lets the car cross decorative walls and the infield. |
| ordered-checkpoints | Inspect ≥3 visible ordered gates. First attempt early/wrong-direction finish and out-of-order/reverse gate; then traverse legally and record each increment. | Invalid attempts do not advance/finish; only the ordered forward route counts. | `unordered-checkpoints` accepts a reverse finish immediately from the start. |
| lap-finish | Start at zero; continuously capture every gate and the correct-direction finish; wait ≥3s. | Positive final time and explicit result; final time remains frozen. | `running-finish-clock` displays a result but the final time keeps increasing. |
| restart | After a valid finish use Restart; compare position/timer/gates/result; accelerate again. | Fresh initial state, no result/progress carried over, timer/controls work. | `stale-reset` resets the car but retains previous gate progress. |

For the local reference, clockwise order is 1 → 2 → 3 → FINISH. Reverse from the
start for the invalid-finish example. Hold throttle + right for a legal lap. This
known route is for testing the example, not proof a general evaluator can discover
routes or recognize arbitrary 3D games. A geometry-blocked invalid-order probe is
not an automatic pass: explicitly record what could not be demonstrated.

## Other ratings and missing evidence

- **Readability:** inspect car, upcoming route, boundaries, gate order/progress and timer/result.
- **Guidance:** match displayed accelerate/brake/steer controls to input; inspect route/restart cues.
- **Feedback:** distinguish accepted gates, rejected attempts, boundary contacts and valid finish.
- **Presentation:** inspect low-poly 3D coherence and unobstructed essential UI at both viewports.

Use the existing 0/5/10 anchors, with reasons for partial ratings. No sound/FPS
inference from still images. Creation-time credit needs actual receipts and all
specified core gates; there is no creation-time or cost score for these fixtures.

Observed defect = `failed` (0). Missing route/recording/comparison = `not_tested`
(0), not a confirmed defect. Browser/authentication/transport problems remain
infrastructure errors. A braking test confounded by a wall is not a valid failure
or pass of the brake. Preserve the evidence and reason; never infer unseen success.
These examples do not change historical Tetris scores.
