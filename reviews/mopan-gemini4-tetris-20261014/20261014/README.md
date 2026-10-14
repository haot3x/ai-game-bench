# Maintainer evidence review and limited replay

Submission: [r003](../../../submissions/mopan-gemini4-tetris-20261014/r003/README.md).
Reviewer: haot3x / Mopan AI, assisted by the same Codex session as submitter.
Same-person affiliated review; no independent certification or generation rerun.

The submitted manifest hash is
`46f8f1fa92d8ab582591ce3db75254c4af523c76de5ec8f9dcd584b5fdd05e6d`.
Trusted main `bc13bdc88e2abe1114324b8e7520dbc24e5a44d9` validates the three revisions,
original source binding and score arithmetic. The exact final reviewed PR head,
GitHub checks and acceptance decision are recorded in
[PR #4](https://github.com/mopan-ai/ai-game-bench/pull/4).

## Evidence judgement

Original single clear: score102→234, with32 drop points and explicit+100 award.
Original double clear:568→898, with30 drop points and explicit+300, both Level1.
Before/after board images show row removal and remaining blocks. Core9/9 claims
are supported by their referenced original screenshots/action observations.
Six historical experience ratings have their own observations/reasons; they are
operator judgements, not calibrated AI-judge measurements.

Historical-scale total85.380340 is provisional:68.304272 points on80 allocated
weight; actual user cost remains unknown. Owner-reported model/media estimates
are disclosed with scope and arithmetic, not audited bills. Original pilot91.443355
and original evidence remain unchanged. Creation sampling gaps and unseen internal
model/tool activity prevent a completeness/authenticity attestation.

## Replay, 2026-10-14 06:40–06:49 UTC

Used the submitted public URL and build label in a fresh credential-free gstack
Chromium context,1280×800. No account cookies/profile were imported. Browser
reports HeadlessChrome151.0.7922.34. See [replay.json](replay.json) for exact times,
file hashes and scope; [operations.jsonl](operations.jsonl) retains every tool
operation with task-local paths replaced by `review-root`.

Canvas UI buttons were activated by dispatched pointer events at visually chosen
coordinates; keyboard input used browser key presses after a native canvas click
to focus the iframe. This is DOM-assisted input and visual observation. No hidden
game state, source reads, game-function calls, RNG/clock/storage changes were used.
Initial unfocused keyboard attempts are retained in the trace and earn no replay
claim. No screenshot-only claim of frame rate or input latency is made.

Observed: delayed Start opens a clean score0 board; idle gravity advances pieces
without spontaneous score increases; focused hard drops score and stack; explicit
top-out; left/down input cannot continue placement; visible post-loss restart
clears current score/board; left input works afterward; pause works. Historical
best persists correctly. Space on the loss screen is a quick restart, so it is
unsuitable as a test of blocked placement. Some initial drop batches crossed
that quick-restart path; the full trace preserves them.

| Replay evidence | Observation |
| --- | --- |
| [Entry](replay-entry.png), [start](replay-start.png) | Delayed entry / score0 clean start |
| [Idle](replay-idle.png) | Gravity/locks with score0 and no drop input |
| [Loss](replay-pointer-loss.png), [after left/down](replay-pointer-loss-blocked.png) | Top-out82 and unchanged loss/board after placement input |
| [Restart](replay-pointer-restart.png), [left input](replay-pointer-restart-left.png) | Empty score0 board and working input |
| [Paused](replay-final-paused.png) | Visible pause; score stays0 while ordinary gravity had progressed |

This limited replay did not reproduce the original owner-tab anomalies. Their
cause remains unresolved; no claim that they were product defects or harmless
infrastructure is made. Reviewer line clears were not rerun; their acceptance
uses the original public before/action/after evidence above. Mobile, sound,
level progression,3/4-line clears and exhaustive collisions were not replayed.
Same URL/build label is not proof of identical game bytes across observations.

Review recommendation: accept as an affiliated manual pilot with these stated
limitations and retrospective scoring. Required CI and the trusted review must
pass on the final PR head before merge. Website publication is a separate step.
