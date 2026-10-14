# Classic Tetris browser pilot v1

Freeze this protocol and its policy hash **before** sending the prompt. Until a
maintainer approves the method, results are pilot observations, not accepted
benchmark rankings. Do not compare this new scale with historical report totals.

## Creation policy

- One fresh project, one generation, no hidden retries or repair prompts.
- At most 60 minutes from accepted prompt to final accessible game. Record Send
  click, accepted-message receipt, last still-working observation and first final
  delivery observation. Sampling yields an interval, not exact model compute time.
- Owner-approved model; all other settings default. No template/asset selection.
- Answer only actual clarification questions. Use classic single-player 2D,
  keyboard controls, no login/multiplayer, simple original block visuals and
  platform-default stack when a choice is necessary. Record the exact question,
  answer and reason. A build confirmation is allowed and recorded as a follow-up;
  a request to fix/extend a delivered game is not.
- Capture task-scoped progress at least every 30 seconds where connection permits,
  plus model selection, acceptance, questions, errors and final delivery. Declare
  gaps. Keep raw captures local; publicly share reviewed evidence only.
- Completion requires no active generation/Stop state, a completion signal and
  an accessible final game. A creator saying "done" is not a gameplay pass.
- No purchase, account-setting changes, public-game publishing or backend access.
  Costs/effort/internal model identity remain unknown unless actually exposed.

## Evaluate only the final game

Use the delivered game-only surface, normal mouse/keyboard/touch controls and
visible pixels/labels. DOM is permitted for targeting UI controls, not for reading
hidden game state, inspecting source, invoking game functions or setting scores.
Do not change the game, clock, RNG, storage or JavaScript. Restarting a play session
is allowed; regenerating the artifact is not. Keep focus on the game and record
the viewport, browser, build identity and access requirements.

Use up to **30 minutes of gameplay evaluation**, at most six restarted sessions,
with before/action/after images and an ordered action trace. Stop testing a
criterion once its required evidence is captured. Do not omit failures. The
limited budget intentionally leaves difficult/unobserved checks at zero, with
`not_tested` distinguished from an observed defect. A reviewer can request a new
evidence revision but must not silently replace this run's original score.

An independent evaluator should not see creation chat/model/cost. If the same
operator/agent creates and evaluates, declare `creation_context_hidden: false`;
separate files/pages alone do not establish blindness or independent review.

## Scores (all subcriteria 0–10; total 0–100)

Core = 60 points, observable UX = 10, delivery time = 30. Cost is reported but
not scored. No missing dimension is dropped or renormalized. Core criteria are
binary 0/10 except `line-score` (0/5/10); UX criteria have 0/5/10 anchors below.
Screenshot aesthetics alone do not prove that the game works.

| Criterion | Weight | Required observation for 10/10 |
| --- | ---: | --- |
| ready | 6 | Open/start a visible board with a falling playable piece and legible score/state. A loading screen is insufficient. |
| movement | 6 | The same piece moves left and right on input and stops at both side boundaries without leaving the board. |
| rotation | 6 | An asymmetric piece visibly rotates in open space; repeat beside a wall without leaving the board or overlapping locked blocks. |
| gravity | 6 | With no input a piece descends; down/soft-drop visibly accelerates descent. |
| lock-spawn | 6 | A piece locks on floor/stack, remains fixed, and a new piece spawns. Observe at least three locks, including one on a stack. |
| line-clear | 10 | Fill a complete row by normal input, observe that row disappear and blocks above shift correctly. Before/after board evidence is required. |
| line-score | 8 | Capture a line clear with score before/after and then a same-placement multi-line clear. Show both increases and the multi-line reward is larger at the same level; movement/drop points must not explain the delta. Only a proven single-line scoring event earns 5. |
| game-over | 6 | Stack to the top through normal input; observe explicit loss and no continued normal placement. |
| restart | 6 | From game-over restart through visible controls; board and current score reset and new input works. |
| readability | 2.5 | Active/locked pieces and score/state remain visually readable both on an empty and populated board. One state only earns 5. |
| guidance | 2.5 | Visible control instructions exist and observed movement/rotation/drop mappings match. Instructions without checking mappings earn 5. |
| feedback | 2.5 | Visible event feedback distinguishes both line clear and game-over, apart from raw score changes. Only one event earns 5. |
| layout | 2.5 | At desktop 1280×800 and mobile 390×844 the board, state and provided controls fit without obstructing each other. One viewport only earns 5; this is layout, not proof of mobile playability. |
| delivery-time | 30 | Accepted-to-final-observed time at most 5 minutes, and ready + lock-spawn both pass. See formula below. |

For time: `score = round(10 × clamp((3600 − elapsed_seconds) / 3300, 0, 1), 6)`.
Use the first observed **final** delivery time, not a favorable midpoint or an
intermediate preview. Require ready + lock-spawn passes or time score is zero.
Preparation, operator evaluation and PR packaging durations are reported
separately and do not count as generation time.

`total = sum(weight × score / 10)` (weights sum to 100). Build failure earns zero.
Authentication/browser/evaluator infrastructure failures yield no total, not a
game defect. Public validation recomputes totals and time credit; it cannot prove
the truth of the supplied observations or the authenticity of screenshots.

## Evidence and review

Use public-submission/0.1 with separate creation/evaluation JSONL, timestamps,
stable event IDs, final artifact URL/build (or null when unavailable), criterion
evidence references, costs by basis, affiliation and privacy/rights declarations.
Every verdict needs actual observed evidence; no reconstructed missing frames.
Do not include accounts, private profile paths, unrelated tabs/chats or credentials.
Explicitly state whether captures are sampled or continuous. Internal model/tool
trajectories are unknown unless the platform exposes them; do not invent them.

This is a **manual pilot**, not a calibrated automatic Tetris verifier. Free
tests validate prompt/policy identity, evidence arithmetic and rejection cases;
they do not calibrate game judgement. A maintainer reviews screenshots and replays
critical actions in a clean, credential-free browser where the URL permits it.
Green CI is never evidence authenticity, game verification or merge approval.
