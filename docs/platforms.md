# Platform integration contract

The public preview has two operational agents: Harbor Oracle and Nop. The six
creator platforms below have individual [reference directories](../platforms/README.md),
**not** validated one-command adapters in this checkout. `agb run` deliberately
refuses them. `agb platforms <name>` reads a runbook; adding `--json` returns its
integration metadata without connecting accounts or executing a plugin.

| Target | Intended route | Required contribution |
| --- | --- | --- |
| Codex | Native Harbor agent | Pinned version/config, credentials guide, local artifact handoff, free mocked tests |
| Claude Code | Native Harbor agent | Same; record actual provider/model separately from harness name |
| Mopan | Existing-profile browser UI | New project, submit, clarify, observe final game, export evidence |
| Astrocade | Existing-profile browser UI | Same lifecycle, platform-specific UI detection |
| TapTap Maker | Existing-profile browser UI | Same lifecycle; record displayed credit changes when available |
| Manus | Existing-profile browser UI | New task, final managed Preview, task-credit provenance and access/expiry limits |

Use Harbor's supported agent interface and job configuration. Do not add a second
runner. Upstream Harbor having an agent is not proof our task, network policy,
account and artifact export all work with it. The current counter runs offline;
model network access requires a separately reviewed configuration.

## Browser wrapper: proposed lifecycle

```text
preflight → verify selected profile → fresh project → submit prompt
    → observe / answer clarification → confirm final delivery → freeze handoff
```

The future wrapper should expose the same high-level run entry as CLI agents.
Login, CAPTCHA and profile permission remain explicit human steps; never bypass
them or silently switch profiles. Attach only to the operator-selected browser;
do not copy the complete Chrome profile or read unrelated tabs/cookies.

- Confirm actual Send/navigation or message receipt, not merely filled input.
- Preserve visible progress and follow-ups before transient UI disappears.
- Record timestamps for accepted prompt, first playable artifact and final
  delivery, with observation gaps and clock/source notes.
- Use authored clarification policy. Record exact visible questions/answers and
  extra turns. No unsolicited feature additions or silent repair prompts.
- Terminal states: delivered game, explicit build failure, timeout, auth failure,
  browser transport failure. Do not treat a creator's "done" as game acceptance.
- Export the final playable URL/build identity or local bundle. A URL can change
  and is not an immutable artifact; record observation date and that limitation.
- Keep creator chat, billing and platform identity away from independent judges.
  Judges see the task, authorized game surface and verification instructions.
- Separate DOM-assisted operation from screenshot-only play; report the mode.
- Default selectors/options are observations, not hardcoded model identities.

## Free tests before real accounts

Use a fake local creation website and simulate clarification, missing Send,
stale completion, expired login, changed profile, quota exhaustion and timeout.
No CI job receives a personal browser profile. Only after review, request a
bounded real run specifying platform, task, attempts, wall time and spend limit.

Historical Tetris observations used `一个经典俄罗斯方块`, fresh projects and
platform defaults. The proposed reproducible recipe is one attempt, no automatic
retry, 60-minute creation cap and logged clarification answers. These are method
references, not executable browser code or proof every historical run followed
identical conditions. See each [report](../reports/README.md) for its caveats.
