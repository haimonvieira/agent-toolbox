#!/usr/bin/env bash
# Fast repository-only validation. No local environment scan.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/audit.py verify "$@"
