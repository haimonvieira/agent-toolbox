#!/usr/bin/env bash
# Thin wrapper for the read-only local audit.
# Default: full audit (validate + collect + drift + reports).
# Options: --quick, --full, --report-only, --accept-baseline --yes, --check-upstreams.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/audit.py "$@"
