#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Both are real Harbor trials; no model calls, credentials or external game URLs.
run_suffix="$(date -u +%Y%m%dT%H%M%S)-$$"
uv run --locked agb run --agent oracle --job-name "smoke-oracle-$run_suffix"
uv run --locked agb inspect "jobs/smoke-oracle-$run_suffix" --expect 1
uv run --locked agb run --agent nop --job-name "smoke-nop-$run_suffix"
uv run --locked agb inspect "jobs/smoke-nop-$run_suffix" --expect 0
