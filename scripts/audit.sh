#!/usr/bin/env bash
# Read-only audit snapshot for the local AI-agent tooling.
#
# Safety contract:
#   - explicit allowlist of commands and paths
#   - never prints environment variables or config values
#   - never starts MCP servers, executes hooks, or loads plugins
#   - never modifies the system
#
# Usage: bash scripts/audit.sh [--json]

set -euo pipefail

JSON=0
[[ "${1:-}" == "--json" ]] && JSON=1

section() { printf '\n== %s ==\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

CONFIG_DIRS=(
  "$HOME/.config/opencode"
  "$HOME/.claude"
  "$HOME/.codex"
  "$HOME/.omp"
  "$HOME/.agents"
  "$HOME/.gemini"
  "$HOME/.kiro"
  "$HOME/.copilot"
  "$HOME/.config/zed"
)

section "harness binaries"
for c in opencode claude codex omp freebuff zed delta gh git node npm uv; do
  if have "$c"; then
    printf '%-10s %s\n' "$c" "$(command -v "$c" | sed "s#$HOME#~#")"
  else
    printf '%-10s NOT FOUND\n' "$c"
  fi
done

section "versions (safe --version only)"
for c in opencode claude codex omp freebuff zed delta node npm uv git gh; do
  have "$c" || continue
  v=$(timeout 10 "$c" --version 2>/dev/null | head -1 || true)
  printf '%-10s %s\n' "$c" "${v:-<no version output>}"
done

section "config directories"
for d in "${CONFIG_DIRS[@]}"; do
  if [[ -d "$d" ]]; then
    printf 'present  %s\n' "${d/#$HOME/~}"
  else
    printf 'absent   %s\n' "${d/#$HOME/~}"
  fi
done

section "skill directories"
for d in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.omp/agent/managed-skills" \
         "$HOME/.config/opencode/skills" "$HOME/.copilot/skills" "$HOME/.gemini/config/skills" \
         "$HOME/.kiro/skills" "$HOME/.codex/skills"; do
  [[ -d "$d" ]] || { printf 'absent   %s\n' "${d/#$HOME/~}"; continue; }
  count=$(find "$d" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
  broken=$(find "$d" -mindepth 1 -maxdepth 1 -type l ! -exec test -e {} \; -print 2>/dev/null | wc -l | tr -d ' ')
  printf '%-6s %-40s entries=%s broken_symlinks=%s\n' "present" "${d/#$HOME/~}" "$count" "$broken"
done

section "MCP config files (existence only)"
for f in "$HOME/.config/opencode/opencode.json" "$HOME/.claude.json" "$HOME/.codex/config.toml" \
         "$HOME/.omp/agent/mcp.json" "$HOME/.config/zed/settings.json" \
         "$HOME/.gemini/config/mcp_config.json" "$HOME/.kiro/settings/mcp.json"; do
  if [[ -f "$f" ]]; then printf 'present  %s\n' "${f/#$HOME/~}"; else printf 'absent   %s\n' "${f/#$HOME/~}"; fi
done

section "local MCP services (listening check only)"
if have ss; then
  for port in 9010 27200 7600; do
    if ss -ltn 2>/dev/null | grep -q ":$port "; then
      printf 'listening  %s\n' "$port"
    else
      printf 'not listening  %s\n' "$port"
    fi
  done
else
  echo "ss not available"
fi

section "plugin state files (metadata counts only)"
if [[ -f "$HOME/.omp/plugins/installed_plugins.json" ]]; then
  python3 - "$HOME/.omp/plugins/installed_plugins.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("omp installed_plugins:", len(d.get("plugins", {})))
PY
fi
if [[ -f "$HOME/.claude/plugins/installed_plugins.json" ]]; then
  python3 - "$HOME/.claude/plugins/installed_plugins.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("claude installed_plugins:", len(d.get("plugins", {})))
PY
fi

section "git hook state (read-only)"
git config --global --get core.hooksPath >/dev/null 2>&1 \
  && echo "core.hooksPath is set (value not printed)" \
  || echo "core.hooksPath unset"

section "safety"
echo "Runtime verification: not performed for safety"
echo "No MCP server, hook, plugin, or skill script was executed."

if [[ "$JSON" == "1" ]]; then
  echo '(JSON output not implemented; this report is human-readable)' >&2
fi
