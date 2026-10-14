# Mopan · Gemini 4 Argon · Classic Tetris

**Unverified manual pilot, 2026-10-14.** Submitted by `haot3x` / Mopan AI with an
AI browser operator. This is affiliated, same-operator evidence, not independent
review, an accepted ranking, or a new automatic game verifier.

[Play the tested build](https://mopan.ai/play/9e77c349-d405-4916-9773-00f00535479d?build=5816ae22-b9f0-49cb-b736-dd111797133d)
· [Machine-readable result](manifest.json)
· [Creation trajectory](creation.jsonl)
· [Evaluation trajectory](evaluation.jsonl)

## Run

- Prompt: **一个经典俄罗斯方块**. One fresh generation; no retry or repair prompt.
- Selected Main: **Gemini 4 Argon · Google**; Child: **Same as Main**.
  These are UI labels, not internal model attestation. Other options unchanged.
- Three requested clarifications answered: pure classic arcade rules, simple
  pastel/wooden blocks, portrait layout with keyboard/touch controls.
- Creation used the owner's explicitly selected existing Chrome profile.
  Scored play used the same build in a new anonymous browser context.
- Effort, internal routing/version, tokens, task cost and account tier: **unknown**.
  Unknown subscription allocation is not zero. No old run's price is reused.
- Policy: `tetris-browser-pilot-v1`, frozen before Send in method commit
  `362e3cc40eefb33e0987ffa6592076187c07cd63`; [method PR #3](https://github.com/mopan-ai/ai-game-bench/pull/3)
  remains a prerequisite for formal acceptance. No post-result weight changes.

## Result: 91.44 / 100 under this pilot rubric

Nine core checks observed: **60/60**. Observable UX checks: **10/10**.
Delivery time: **21.44/30**. This narrow score is not an aesthetic/fun rating and
must not be mixed with historical report totals or generalized to the model.

| Criterion | Subscore / 10 | Weighted points | Main screenshot evidence |
| --- | ---: | ---: | --- |
| Start / ready | 10 | 6 | [Empty playable board](evidence/eval-009-clean-begin.jpeg) |
| Left/right and boundaries | 10 | 6 | [Left clamp](evidence/eval-013-left-clamp.jpeg), [right clamp](evidence/eval-016-right-clamp.jpeg) |
| Rotation | 10 | 6 | [Open space](evidence/eval-011-rotate-open.jpeg), [at wall](evidence/eval-014-rotate-wall.jpeg) |
| Gravity and soft drop | 10 | 6 | [Before idle](evidence/eval-017-gravity-before.jpeg), [after idle](evidence/eval-018-gravity-after.jpeg), [soft drop](evidence/eval-019-soft-drop.jpeg) |
| Lock and new spawn | 10 | 6 | [First](evidence/eval-020-lock-one.jpeg), [second](evidence/eval-021-lock-two.jpeg), [third](evidence/eval-022-lock-three.jpeg) |
| Line removal / collapse | 10 | 10 | [Before](evidence/eval-031-single-before.jpeg), [after](evidence/eval-032-single-after.jpeg) |
| Single vs same-placement multi-line score | 10 | 8 | [Single +100](evidence/eval-032-single-after.jpeg), [double +300](evidence/eval-043-double-after.jpeg), both Level 1 |
| Game-over stops placement | 10 | 6 | [Top-out](evidence/eval-024-top-5.jpeg), [after input](evidence/eval-025-loss-input-blocked.jpeg) |
| Post-loss restart | 10 | 6 | [Reset to zero](evidence/eval-026-restart-zero.jpeg), [new input](evidence/eval-027-restart-input.jpeg) |
| Readability | 10 | 2.5 | [Empty](evidence/eval-009-clean-begin.jpeg), [populated](evidence/eval-042-double-before.jpeg) |
| Control guidance | 10 | 2.5 | [Game instructions](evidence/eval-008-anonymous-start.jpeg) and movement/rotation/drop observations above |
| Event feedback | 10 | 2.5 | Line-clear messages/particles and explicit loss modal above |
| Desktop/mobile layout | 10 | 2.5 | [1280×800](evidence/eval-042-double-before.jpeg), [390×844](evidence/eval-046-mobile-playing.jpeg) |
| Delivery time | 7.147785 | 21.443355 | Receipt and final-render timestamps below |

Single clear: score **102 → 234**, lines **0 → 1**, visible clear reward **+100**;
32 extra points from hard drop. Double clear: **568 → 898**, lines **1 → 3**,
visible clear reward **+300**; 30 extra drop points. Both at Level 1. Normal input
filled the rows; no hidden-state reads, board injection or source modifications.

## Timing (UTC, observer timestamps)

| Event | Time |
| --- | --- |
| Actual Send click | 04:08:50.536–04:08:50.768 |
| First accepted-prompt receipt | 04:09:03.432 |
| Last sampled active generation | 04:28:29.557 |
| First no-Stop/completion observation | 04:28:34.559 |
| First rendered final game | 04:29:44.663 |
| Evaluation window | 04:29:56.667–04:47:01.733 |

Scored elapsed time is **1,241.231 seconds (20m 41.231s)**, including clarification
response latency and observation delay. Send-to-render is about 20m 54s. The
platform's **18:52** build-card timer is preserved but not substituted for these
timestamps. Setup, evaluation (~17m 05s), and packaging are separate from creation.

Time subscore = `round(10 × (3600 − 1241.231) / 3300, 6) = 7.147785`.
Ready and lock/spawn gates passed. Total = `60 + 10 + 30 × 7.147785 / 10`.

## What the evidence contains

[Browser operations](evidence/browser-operations.jsonl) preserve ordered tool
receipts, timestamps, keys/click coordinates, surface identity and reviewed
read-only observation expressions as inert data. [Creation observations](evidence/creation-observations.jsonl)
contain 85 rendered conversation samples, not internal reasoning/tool traces.
Canonical JSONL events link verdicts to actual screenshots and those receipts.

Images are original task-scoped viewport/element captures, not retouched. Their
hashes and sizes are in `manifest.json`. No executable game bundle, profile,
credentials, unrelated tabs or raw transport output is included. Some redundant
screenshots and all local videos are omitted; capture names in the operation log
are provenance, not a promise that every local file was published.

## Limitations and review next steps

- Same assistant saw creation chat and performed evaluation; blindness and
  independent validation are **not** claimed. Selected UI model is not a signed
  provider receipt. Cost remains unknown.
- Two initial owner-tab play sessions showed state changes unexplained by this
  operator's inputs ([first](evidence/eval-003-start.jpeg), [restart](evidence/eval-005-reset.jpeg)).
  Cause is unresolved. Both remain disclosed, are not scored as defects/passes,
  and motivated clean anonymous evaluation. Five play sessions in total,
  including mobile-emulation reload; no generation retry.
- Public captures are sampled. [13 conversation-text gaps exceed 30 seconds](evidence/capture-gaps.json),
  maximum 186.086s. This deviates from the target cadence and is a review issue,
  not silently repaired with invented timestamps or a private video claim.
- Mobile means browser layout emulation, not physical-device gameplay. Audio,
  advanced progression, 3/4-line clears and exhaustive edge cases are untested.
  No points for these are hidden in this rubric's limited checks.
- A hosted build URL is not immutable bytes. Single prompt/single generation
  gives no stability estimate. The high core score means these basic checks
  passed, not that broader game quality has been calibrated.
- Maintainer: review method PR first, validate this exact head/manifest using
  trusted code, inspect evidence and replay critical checks in a clean browser.
  Input trace is auditable but not deterministic replay: RNG seed is unknown.
  Record review identity, affiliation, head SHA and any omissions in the PR.
  Green schema/CI is not authenticity, acceptance, reproduction or merge approval.

## Rights

Authored benchmark notes/JSON exports: Apache-2.0. The owner explicitly authorized
public PR evidence for this new run. Task-scoped screenshots/dialogue are shared
for public benchmark review/display; third-party UI/trademarks retain their
rights. This submission grants no additional game-source or training-data license.
