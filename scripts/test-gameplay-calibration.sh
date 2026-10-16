#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
image_tag="ai-game-bench-browser:playwright-1.62.0"
mkdir -p "$repo_dir/artifacts/gameplay-calibration"
output_dir="$(mktemp -d "$repo_dir/artifacts/gameplay-calibration/run.XXXXXX")"
printf 'Local evidence (retained even if checks fail): %s\n' "$output_dir"
docker build -t "$image_tag" "$repo_dir/datasets/smoke-create-v0.2/create-click-counter-zh-001/environment"
# Original local fixtures only. No account, model, host browser, or external network.
docker run --rm --network none --read-only --shm-size=256m \
  --tmpfs /tmp:rw,exec,nosuid,size=512m \
  --mount "type=bind,source=$repo_dir/fixtures/calibration/gameplay-v1,target=/fixtures,readonly" \
  --mount "type=bind,source=$repo_dir/tests,target=/checks,readonly" \
  --mount "type=bind,source=$output_dir,target=/output" \
  --env GAMEBENCH_GAMEPLAY_TESTS=1 \
  "$image_tag" python -m pytest /checks/test_gameplay_calibration_browser.py \
  -q -p no:cacheprovider -o 'markers=browser: real Chromium calibration' "$@"
