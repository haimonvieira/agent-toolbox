# External volume dependencies

- **Volume:** the external volume was unmounted at the Phase 1 baseline and mounted later.
- **Rule:** no file was moved or copied. Paths are normalized to `<external-volume>`.

## Agent-related dependencies

| # | Dependency | Path | Purpose | Failure mode unmounted | Placement appears intentional? | Local fallback |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Global skill symlink | `~/.agents/skills/coordenacao-commit-seguro` → `<external-volume>/<project>/.agents/skills/coordenacao-commit-seguro` | Project-specific commit/PR workflow available globally | Broken symlink; skill not discovered | Yes — it is a project skill shared globally | No |
| 2 | Codex project trust | `~/.codex/config.toml` `[projects."<external-volume>/..."]` | Marks the project trusted | Trust entry inert; project can still be opened but is not pre-trusted | Yes | No |
| 3 | Codex project hooks | `<external-volume>/<project>/.codex/hooks.json` + `hooks/state_freshness.py` | Reminds the agent to refresh canonical project state | Hook command cannot resolve; skipped/fails | Yes | No |
| 4 | Project-local skills | `<external-volume>/<project>/.agents/skills/` (19 skills) | Coordination workflow skills | Not discoverable while working in that project | Yes | No |
| 5 | OMP session history (metadata) | `~/.omp/agent/sessions/--media-<volume>-...` | Historical sessions only | Sessions remain readable but reference unavailable files | Yes | n/a |

## Classification

| Dependency | Class |
| --- | --- |
| Global symlink | **Should move local** or accept volume dependency |
| Codex trust + hooks | **Intentionally external**; keep volume mounted |
| Project-local skills | **Intentionally external** |
| OMP session history | **Intentionally external / historical** |

## Failure test (read-only)

```bash
# While mounted
test -e ~/.agents/skills/coordenacao-commit-seguro/SKILL.md && echo OK

# After unmounting (do not actually unmount during work)
test -e ~/.agents/skills/coordenacao-commit-seguro/SKILL.md || echo "would break"
```

## Options (no action taken)

1. **Accept**: keep the volume mounted; document the dependency (current state).
2. **Decouple the skill only**: copy `coordenacao-commit-seguro` into a local directory and replace
   the symlink with a real directory (requires approval, Gate D). The project copy stays authoritative.
3. **Decouple hooks**: move the Codex hook into a local path and update trusted hashes (requires
   approval; changes hook trust).

## Risk

If the volume is unmounted while a session is running, the skill disappears mid-session and Codex
hooks fail open. No data loss is expected; the failure is availability, not corruption.
