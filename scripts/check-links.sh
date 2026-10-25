#!/usr/bin/env bash
# Validate external URLs found in documentation.
# Sends only the URLs (public information); never sends local file contents.
# Skips localhost, example domains, and placeholder URLs.

set -euo pipefail

cd "$(dirname "$0")/.."
TIMEOUT="${TIMEOUT:-15}"
UA="agent-toolbox-link-check/1.0"

urls=$(grep -rhoE 'https?://[^ )>"]+' docs README.md audit 2>/dev/null \
  | sed -E 's/[`.,;:]+$//' \
  | grep -vE '^https?://(127\.0\.0\.1|localhost)' \
  | grep -vE 'example\.(com|org)|[<>]' \
  | grep -vE '/mcp/?$' \
  | grep -vE 'freebuff-private' \
  | sort -u)

total=0
bad=0
while IFS= read -r url; do
  [[ -n "$url" ]] || continue
  total=$((total + 1))
  code=$(curl -s -o /dev/null -m "$TIMEOUT" -L -A "$UA" -w '%{http_code}' "$url" || true)
  [[ -n "$code" ]] || code="000"
  case "$code" in
    2*) printf 'ok   %s %s\n' "$code" "$url" ;;
    *)  printf 'FAIL %s %s\n' "$code" "$url"; bad=$((bad + 1)) ;;
  esac
done <<< "$urls"

printf '\nchecked=%s failed=%s\n' "$total" "$bad"
[[ "$bad" == "0" ]]
