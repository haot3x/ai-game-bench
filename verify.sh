#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked agb submission policies
uv run --locked agb submission validate-all
