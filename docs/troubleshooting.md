# Troubleshooting

Known local issues, in order of likelihood. All diagnostics below are read-only.

## Skills

### A skill does not appear in a harness

1. Confirm the file exists: `test -f <skill-dir>/SKILL.md`.
2. Confirm the directory the harness reads:
   - OpenCode: `~/.agents/skills`
   - Claude Code: `~/.claude/skills`
   - OMP: `~/.omp/agent/managed-skills`
   - Codex: `~/.codex/skills`
3. Validate frontmatter has `name` and `description`.
4. Restart the harness; most load the skill list at session start.

### Symlink into an unmounted volume

`coordenacao-commit-seguro` points into an external volume. It was broken during the snapshot
(target absent) and resolved after the volume was mounted mid-audit. This is a **conditional**
failure, not a permanently broken link.

Either keep the volume mounted, or copy the skill locally and replace the symlink. Do not delete the
link blindly: its target is a project-local skill that exists only on that volume.

### Two different versions of the same skill

Known overlaps: `superpowers` (standalone + plugin 7.0.0 + stale 6.3.0), `code-review`/`autofix`
(standalone + CodeRabbit plugin), `penpot-*` vs `source-command-penpot-*`. Decide which copy is
canonical, then remove or symlink the others.

### `~/.claude/skills` diverges from `~/.agents/skills`

Expected for `code-review` and `graphify`. Everything else was identical at snapshot time. Re-check:

```bash
find ~/.agents/skills ~/.claude/skills -name SKILL.md -print0 | xargs -0 sha256sum | sort | uniq -w64 -d
```

## MCP servers

### Server marked broken

| Server | Fix |
| --- | --- |
| `codegraph` | Identify the correct upstream first; the npm name is unverified. Leave disabled. |
| `codebase-memory` | Fixed in Phase 3: installed `0.12.1`; binary present |
| `hostinger-api` | Fixed in Phase 3: installed `3.8.1`; binary present |
| `openagents` | Resolved on 2026-10-25: the entry was removed from both harness configs (upstream never identified). |
| `gemini-notebook-mcp` | Fixed in Phase 3: command replaced with `~/.local/bin/notebooklm-mcp` |

### Local HTTP MCP unreachable

```bash
ss -ltn | grep -E ':(9010|27200|7600)'
```

- `9010` → start BrowserOS.
- `27200` → enable the Obsidian MCP connector plugin.
- `7600` → Starry app; Kiro is not installed here anyway.

### Windows paths in configs

Two places contain `C:\Users\...`:

- `~/.omp/agent/mcp.json` → `gemini-notebook-mcp`.
- `~/.omp/marketplaces.json` → malformed `catalogPath` for `superpowers-marketplace` and
  `ui-ux-pro-max-skill` (they resolve to `/home/<user>/C:\Users\...`).

Fix the JSON paths to Linux equivalents (`~/.omp/...`). The stray files currently live in a literal
`C:\Users\...` directory in the home directory.

### Package name ambiguity

`codegraph` on npm (`1.0.0`) has no repository metadata. Do not `npx codegraph` to "see what
happens". Verify the intended project before installing anything with that name.

## Plugins

### Plugin installed but no content

`github@claude-plugins-official` has an empty install directory in the OMP cache. Reinstall it or
remove it; do not assume its tools are available.

### Stale caches

`superpowers` 6.3.0 and `security-guidance` 2.0.7 remain on disk after upgrades. They are inert but
confusing. Remove only after confirming the newer version works.

### Duplicate VS Code extensions

Phase 3 moved the older `openai.chatgpt` 26.1007 directory to a private backup. Only 26.1021 remains.

## Hooks

### Session start is slow or installs packages

The `security-guidance` SessionStart hook can create a venv and `pip install claude_agent_sdk`.
Check `~/.claude/security/agent-sdk-venv`. If this is unwanted, disable the plugin in OMP.

### Hook errors after moving a project

Codex has trusted hashes for a project on an external volume. When the volume is unmounted the hooks
are skipped or fail. After mounting, `~/.codex` still points at the absolute path, so the hooks work
again but remain volume-dependent. Review the hooks (see `inventory/hooks.yaml`) before re-trusting.

### Accidentally trusted a changed hook

Codex stores SHA-256 hashes. If an update changes a hook, Codex should require re-trust. Review the
manifest before approving.

## Harnesses

### `opencode` config was overwritten

`~/.config/opencode/opencode.json.bak` and timestamped `.bak-*` files exist. Compare before
restoring; the live file changed during the audit because another process was writing it.

### Claude auto-update is off

This is intentional in the local config (`autoUpdates: false`). Update through the official
procedure and record the new version in `inventory/harnesses.yaml`.

### `pen` / `pencil` appears to hang

The CLI is a TUI. Running `pen --version` opened the interface and did not exit promptly during the
audit. Do not use it in scripts expecting a one-line version.

## Repository checks

```bash
bash scripts/verify.sh      # YAML/JSON validity, expected paths, secret patterns
bash scripts/check-links.sh # external links (network required)
```

If `verify.sh` reports a missing path, it may simply mean this snapshot is stale — re-run
`scripts/audit.sh` and update the inventory.
