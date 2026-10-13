# Platform integration references

These six directories document the routes used in the historical Tetris pilots.
They are **reference integrations, not six working `agb run` plugins**. Browser
creation was operated through a consented Chrome connection; historical local CLI
runs also need account/runtime setup that is not distributed here. The public
checkout currently executes only free Oracle/Nop calibration.

| Platform | Historical creation route | Start here |
| --- | --- | --- |
| Codex | Local CLI → local game files | [Codex](codex/README.md) |
| Claude Code | Local CLI, separately configured model provider → local files | [Claude Code](claude-code/README.md) |
| Mopan | Website chat → delivered game/preview URL | [Mopan](mopan/README.md) |
| TapTap Maker | Website chat → preview game | [TapTap Maker](taptap-maker/README.md) |
| Manus | Website task → managed Preview | [Manus](manus/README.md) |
| Astrocade | Website create → editor Game Preview | [Astrocade](astrocade/README.md) |

One common entry point, with no login, browser control or model spending:

```bash
uv run agb platforms
uv run agb platforms mopan
uv run agb platforms claude-code --json
```

Each directory has `integration.json` (route, setup/evidence fields, historical
report references and explicit readiness) and `README.md` (the actual procedure,
delivery checks and platform-specific pitfalls). These files are documentation
inputs, never executable imports. Do not embed credentials, private project IDs,
current prices or personal Chrome paths. A cost belongs to a **run**, not to a
platform plugin: the same platform can use different models/plans over time.

Shared material:

- [CLI procedure](shared/cli-workflow.md)
- [Browser procedure](shared/browser-workflow.md)
- [Record template](shared/record.example.json) — blank fields, no historical data

## Turn a reference into an executable integration

Contribute a Harbor agent/configuration, not a second runner. Keep platform-specific
setup and observation logic in its own directory/module and reuse the common
submission/evidence contract. Do not introduce a dynamic plugin loader that runs
arbitrary code just to list platforms.

1. Add credential-free contract/fake-site tests for setup, submission, follow-ups,
   final delivery, timeout and access failure.
2. Produce the artifact handoff required by a compatible task. The current frozen
   DOM counter does **not** accept a remote URL or assess Tetris.
3. Document account setup without exporting login state. Obtain separate approval
   for a bounded live smoke; record actual versions and all attempts.
4. After maintainer review, wire the adapter through Harbor and update the CLI's
   supported execution path. Changing `public_execution_supported` alone must not
   enable execution. Keep historical reports labeled historical.

See [platform contract](../docs/platforms.md) and
[contribution checks](../docs/contribution-workflow.md).
