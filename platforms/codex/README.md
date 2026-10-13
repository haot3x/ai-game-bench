# Codex

**Historical route:** local CLI creating game files, then a browser playtest of
the delivered game. **Public status:** reference only; `agb run --agent codex`
is intentionally disabled until a public account/network/artifact recipe passes.

## Connection and execution

Follow the [CLI procedure](../shared/cli-workflow.md). Contributors supply their
own authorized account. Start with an empty workspace and new conversation;
do not run inside this benchmark checkout and accidentally expose rubrics or
reference solutions. Retain CLI version, requested model/effort and the native
session's reported values. Historical settings are observations, not defaults
for a new run.

Harbor 0.22.0 already provides `harbor.agents.installed.codex:Codex` (`codex`).
Reuse that implementation for the future public adapter rather than adding a
second CLI scheduler. Its presence is not evidence that our account forwarding,
network policy and task output contract work together. The public smoke task
is offline; model access requires a separately reviewed creator configuration.

## Delivery, evaluation and costs

Freeze the runnable game files and startup instructions. Serve only that game
on loopback; give the evaluator a clean game surface. Record native input/cache/
output usage with its semantics and price-table date. The historical displayed
USD model estimate was not an invoice or a known per-run subscription charge.
Never reuse the historical dollar value as the next run's cost.

## References and remaining work

[Integration metadata](integration.json) links
[Report 001](../../reports/001-tetris-five-platform/reference.json),
[Report 002](../../reports/002-codex-gpt-6-sol-astra-tetris/reference.json) and
[Report 003](../../reports/003-manus-six-platform-tetris/reference.json).
The reports are historical evidence, not exact public replay packages.
Next: pinned creator configuration, safe credential setup, free contract tests,
then an explicitly approved native Harbor end-to-end run.
