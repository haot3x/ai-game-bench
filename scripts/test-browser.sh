#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
task_dir="$repo_dir/datasets/smoke-create-v0.2/create-click-counter-zh-001"
image_tag="ai-game-bench-browser:playwright-1.62.0"

docker build -t "$image_tag" "$task_dir/environment"
# Only task/tests/fixtures are mounted, read-only. Never mount the repo root,
# .env files, Docker socket, or any model credentials into the test container.
docker run --rm --network none --read-only --shm-size=256m \
  --tmpfs /tmp:rw,exec,nosuid,size=512m \
  --mount "type=bind,source=$task_dir,target=/task,readonly" \
  --mount "type=bind,source=$repo_dir/tests,target=/checks,readonly" \
  --mount "type=bind,source=$repo_dir/fixtures/browser/click-counter,target=/fixtures,readonly" \
  --env GAMEBENCH_DOM_TASK=/task \
  --env GAMEBENCH_BROWSER_FIXTURES=/fixtures \
  --env GAMEBENCH_BROWSER_TESTS=1 \
  "$image_tag" python -m pytest /checks/test_dom_browser.py -q -p no:cacheprovider \
  -o 'markers=browser: real Chromium calibration'
