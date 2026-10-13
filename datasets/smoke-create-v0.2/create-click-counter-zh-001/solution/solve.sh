#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/game/dist /workspace/gamebench
cp /solution/files/index.html /workspace/game/dist/index.html
printf '%s\n' '{"schema_version":"0.1","kind":"local_directory","entrypoint":"/workspace/game/dist/index.html","producer":{"name":"oracle"}}' \
  > /workspace/gamebench/submission.json
