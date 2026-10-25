#!/usr/bin/env bash
# Repository consistency and secret-pattern checks. Read-only.
#
# Reports file:line:category for suspicious patterns. It NEVER prints the
# matched value. This is a conservative heuristic, not a replacement for a
# dedicated secret scanner.

set -euo pipefail

cd "$(dirname "$0")/.."
fail=0
note() { printf '%s\n' "$*"; }

note "== YAML validity =="
if python3 - <<'PY'
import glob, sys, yaml
ok = True
for f in sorted(glob.glob("inventory/*.yaml")):
    try:
        yaml.safe_load(open(f, encoding="utf-8"))
        print(f"ok   {f}")
    except Exception as e:
        ok = False
        print(f"FAIL {f}: {type(e).__name__}")
sys.exit(0 if ok else 1)
PY
then :; else fail=1; fi

note ""
note "== JSON example validity =="
if python3 - <<'PY'
import glob, json, sys
ok = True
for f in sorted(glob.glob("configs/examples/*.json")):
    try:
        json.load(open(f, encoding="utf-8"))
        print(f"ok   {f}")
    except Exception as e:
        ok = False
        print(f"FAIL {f}: {type(e).__name__}")
sys.exit(0 if ok else 1)
PY
then :; else fail=1; fi

note ""
note "== TOML example validity =="
if python3 - <<'PY'
import glob, sys
try:
    import tomllib
except ModuleNotFoundError:
    print("skip (tomllib unavailable)")
    sys.exit(0)
ok = True
for f in sorted(glob.glob("configs/examples/*.toml")):
    try:
        tomllib.load(open(f, "rb"))
        print(f"ok   {f}")
    except Exception as e:
        ok = False
        print(f"FAIL {f}: {type(e).__name__}")
sys.exit(0 if ok else 1)
PY
then :; else fail=1; fi

note ""
note "== expected local paths (warnings only) =="
for f in \
  "$HOME/.config/opencode/opencode.json" \
  "$HOME/.claude/settings.json" \
  "$HOME/.codex/config.toml" \
  "$HOME/.omp/agent/mcp.json" \
  "$HOME/.agents/skills" \
  "$HOME/.claude/skills"; do
  if [[ -e "$f" ]]; then
    note "present  ${f/#$HOME/~}"
  else
    note "MISSING  ${f/#$HOME/~} (snapshot may be stale)"
  fi
done

note ""
note "== broken symlinks inside skill stores =="
for d in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
  [[ -d "$d" ]] || continue
  find "$d" -mindepth 1 -maxdepth 1 -type l ! -exec test -e {} \; -print 2>/dev/null \
    | sed "s#$HOME#~#" | sed 's/^/broken  /' || true
done

note ""
note "== secret-pattern scan (paths only) =="
# Patterns target common credential shapes. Matched text is discarded.
set +e
grep -rInE \
  '(sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})' \
  --include='*.md' --include='*.yaml' --include='*.yml' --include='*.json' --include='*.toml' \
  --include='*.sh' --include='*.example' \
  . 2>/dev/null | awk -F: '{print $1":"$2": potential-secret"}' | head -50
found=${PIPESTATUS[0]}
set -e
if [[ "$found" == "0" ]]; then
  note "potential secrets found (values suppressed) — inspect the paths above"
  fail=1
else
  note "no common secret patterns found"
fi

note ""
note "== absolute home paths in documentation =="
set +e
hits=$(grep -RIl --include='*.md' --include='*.yaml' -- "$HOME" . 2>/dev/null | wc -l | tr -d ' ')
set -e
if [[ "$hits" != "0" ]]; then
  note "warning: $hits file(s) contain an absolute home path (paths not printed)"
else
  note "ok: no absolute home paths"
fi

note ""
if [[ "$fail" == "0" ]]; then
  note "verify: OK"
else
  note "verify: findings above"
  exit 1
fi
