#!/usr/bin/env bash
set -euo pipefail

# Infrastructure failures intentionally produce details but NO reward file.
# Harbor 0.22 ignores the script exit code; absence of reward raises a verifier
# exception instead of silently counting a broken browser as an agent failure.
exec python3 /tests/verify_submission.py
