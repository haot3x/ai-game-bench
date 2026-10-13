# Claude Code

**Historical route:** local Claude Code CLI with a separately configured model
provider. **Public status:** reference only, not an executable public adapter.

## Connection and execution

Follow the [CLI procedure](../shared/cli-workflow.md). Record harness, CLI version,
provider/model and effort separately: the name "Claude Code" does not prove a
Claude model was used. The historical pilot used user-configured CC Switch
routing; no CC Switch database, API key, proxy credential or personal settings
file belongs in this repository. Contributors configure their own authorized
provider outside the checkout. A provider ping is a separate recorded call.

Use a new conversation and empty game workspace. Save native events and final
game files. Harbor 0.22.0 provides
`harbor.agents.installed.claude_code:ClaudeCode` (`claude-code`), but the historical
local routing configuration must not be assumed to transfer into a container.
Validate that separately before enabling the public run command.

## Delivery, evaluation and costs

Freeze the local game and evaluate a game-only loopback surface. Record the
native CLI cost **as reported**, with provider-pricing mapping confidence.
The historical $0.55 figure was a CLI estimate with unverified pricing mapping,
not a reconciled provider bill. Do not silently price a third-party model as
Claude or treat an existing allowance as a zero-cost invocation. Preserve model
provenance in evidence even if the presentation row is labeled only Claude Code.

## References and remaining work

[Integration metadata](integration.json),
[Report 001](../../reports/001-tetris-five-platform/reference.json),
[Report 003](../../reports/003-manus-six-platform-tetris/reference.json).
Next: public provider setup recipe, free routing/artifact contract tests and a
bounded authorized Harbor smoke. No provider credentials or real model call are
required to inspect this reference.
