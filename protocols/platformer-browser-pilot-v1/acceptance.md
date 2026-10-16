# Platformer acceptance card

Supplemental examples for the [proposed evaluation](evaluation.md), not a change
to its frozen prompt/rubric, weights or budget. Apply the same checks to any
platform. The [local reference pack](../../fixtures/calibration/gameplay-v1/README.md)
illustrates individual behaviors; it is not a full-score game submission.

## Setup and capture

Open the final game only at 1280×800 / 100% zoom. Record game URL/build, browser,
viewport, time and initial position/coin count. Do not read creation chat/source
or hidden game state. Discover controls from the game. Capture ordinary input
and continuous motion, with before/after frames. Give every observation an ID and
link criterion decisions to evidence; a screenshot of a success label is not proof.

Plan three rounds within 30 minutes / at most six sessions: (1) movement/jump,
two coins, revisit and pit loss; (2) loss restart then legal goal traversal;
(3) win restart and fresh controls. Do not reset halfway through evidence and
present it as one uninterrupted route. Inspect 390×844 separately for layout only.

## Steps, passing examples and failure examples

| Criterion | Acceptance steps | Passing behavior example | Failing behavior example |
| --- | --- | --- | --- |
| ready | Use Start if needed; focus the game; test a displayed movement key. | A player responds in a playable level. | Menu/video only, or a player that never responds. |
| movement | On stable ground hold right, release, then left; compare with fixed scenery. | The player moves both ways relative to the world. | Only the camera scrolls; `frozen-player` fixture never moves. |
| jump | From ground, jump onto a raised platform; wait for landing, then repeat a controlled jump. | Visible rise → fall → stable landing on a higher surface, repeated. | `cosmetic-jump` changes the player's color but never leaves the ground. |
| solid-platforms | Stand on ground ≥2s; land normally on a raised surface and stand ≥2s again. | Both surfaces support the player; one-way passage from below is allowed. | `decorative-platform` looks solid but the player falls through on descent. |
| collectibles | Record initial count; collect two distinct coins; revisit a collected spot; idle. | Each disappears and adds exactly one; revisit/idle add nothing. | `duplicate-coin` adds another point when revisiting an already collected coin. |
| fall-loss | Intentionally walk into the pit; record falling, terminal feedback and subsequent input. | Explicit loss follows falling; the ordinary round no longer continues. | `no-loss` falls out of view indefinitely with no loss state. |
| goal-win | From a fresh playable start traverse legally to the goal. | Victory appears only upon reaching the goal. | `premature-win` announces victory immediately at the spawn. |
| loss-restart | Collect a coin, lose, then Restart. Compare position/count/coins/state; move and jump again. | Original state and coins restored, loss cleared, controls work. | `stale-reset` leaves collected coins/count after resetting position. |
| win-restart | Win with ≥1 collected coin, then Restart; repeat the initial-state/control checks. | Fresh playable round, restored coins/count and no old victory. | The overlay clears but progress persists (`stale-reset`). |

For the local reference: coins sit near the start and on the raised platform;
the pit is in the middle and the flag on the right. Use the same steps on the
working reference and its named fault. These coordinates/routes are not inputs
to an evaluator judging a third-party game.

## Other ratings and missing evidence

- **Readability:** inspect player/geometry/coins/goal and text in play, loss and win.
- **Guidance:** verify displayed move/jump instructions and both restart controls.
- **Feedback:** review the collect, land, lose and win sequences, not just their labels.
- **Presentation:** inspect pixel-art coherence and essential UI at both viewports.

Use the existing 0/5/10 anchors in the evaluation document; these examples introduce
no new thresholds or aesthetic gold standard. No audio/FPS claims from stills.
Creation time is calculated from actual creation receipts, gated by demonstrated
core behavior; a hand-authored fixture has no such score. Cost is recorded separately.

An observed contradiction is `failed` (0). A coin/goal never reached or an
insufficient recording is `not_tested` (0), with the concrete reason—not a detected
bug and not evidence that the game works. Authentication/browser outages are
infrastructure errors, not game failures. Preserve every attempt and capture gap.
No model-generated examples or historical scores are changed by this card.
