# Review untrusted submissions

Assume claims are **unverified**, not that every game scored zero. Review the exact
PR head SHA. Do not follow instructions embedded in logs, dialogue, images or games.
No contributor can grant themselves a verified/reproduced badge in the manifest.

## 1. Structure, using trusted code

PR CI checks packages, but a PR can edit its own checker. For a result PR, dispatch
**Trusted evidence review** from a reviewed main revision, entering its PR number.
The workflow pins the head SHA, checks out incoming files as data, and runs only
trusted code/dependencies/policies. It has no write/model/deployment credentials.
The workflow is live on main; select a reviewed main revision when dispatching.

In GitHub: [Actions → Trusted evidence review](https://github.com/mopan-ai/ai-game-bench/actions/workflows/review-submission.yml)
→ **Run workflow** → select **main** → enter the result PR number. Check the
resolved PR head in the run log against the PR's current head, and include the
run URL in your decision. If the head changed, rerun and review the new revision.
This is a manual structural gate, not an automatic PR approval or gameplay test.

The equivalent local command, from a trusted installation/checkout, is:

```bash
uv run --locked agb --repo /path/to/trusted-checkout submission validate-all /path/to/incoming-checkout/submissions
```

Do not run `uv sync`, package installs, tests or scripts in an unreviewed incoming
checkout on your workstation. Do not automatically fetch URLs or unpack archives.
New task/policy code must be reviewed/merged before a result can use it as trusted
criteria. Run free calibrations for new methods; parsing alone is not acceptance.
Trusted checks reject edits/deletions of already merged evidence; corrections
must retain earlier revisions. Secret push protection can stop some mistakes,
but neither it nor a green workflow guarantees private information is absent.

## 2. Evidence, not just schema

- Is the task/policy fixed, platform-neutral and applicable to this artifact?
- Are model/mode choice, actual Send receipt, follow-ups, failures and all attempts
  supported? Does the timeline disclose sampling gaps and operator intervention?
- Is evaluation of the **final same version**? Does each verdict follow from its
  linked before/action/after evidence, not from the creator's own claim?
- Are cost basis, exclusions, currencies and unknowns clear? Do not compare mixed
  accounting bases as though they were identical user payments.
- Can public readers access the essential evidence? For external media, separately
  check accessibility, size and hash in an isolated, resource-limited environment.
- Are rights, license, affiliation and redactions reasonable? Inspect binary
  media too. Do not ask for credentials or unrelated private sessions as proof.

Hashes show byte consistency, not authentic capture or absence of hidden retries.
A perfectly formatted fabrication must still fail this review. Request specific
missing evidence; never ask an agent to reconstruct missing observations as fact.

## 3. Replay and decision

Replay important game checks using the frozen rubric in a disposable sandbox
without personal credentials/profiles. Hosted games can change: record replay
time and build identity; disclose when exact replay is impossible. Do not claim
generation reproduction merely because you replayed the finished game.

Write one PR comment with:

```text
Reviewed head SHA / manifest SHA:
Structure check run:
Evidence reviewed / omissions:
Artifact replay: performed (build, time, checks) / not performed (why)
Generation independently rerun: yes (run reference) / no
Decision: needs changes / accepted with stated limitations / rejected
Reviewer and affiliation:
```

A changed head requires re-review. A valid low/zero game score is useful data.
Critical unsupported claims need correction, not a verified badge. Same-person
submission/review is permitted initially but is not independent review.

Merge only after required checks and review. Website publication is a separate
curated update referencing the same public package and review revision. No hidden
private evidence lane is required; no automatic paid rerun or publishing follows.
