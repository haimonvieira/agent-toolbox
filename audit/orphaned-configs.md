# Orphaned harness configurations

No executable, desktop entry, snap, flatpak, or VS Code extension was found for the tools below.
No config was deleted or modified. Credential values were not read.

## Kiro

| Field | Value |
| --- | --- |
| Path | `~/.kiro/` |
| Files | `settings/mcp.json` (modified 2026-10-25 11:09), `skills/starryai` |
| Executable | none (`command -v kiro`, flatpak, snap, `/opt`, desktop entries all empty) |
| Credential reference | `Authorization` header for `starry` (value not read) |
| Other consumer | Starry app is installed (`/usr/bin/Starry`) but its binary contains no `.kiro` references |
| Classification | **Orphaned / unknown consumer** — config is actively modified but no owner was identified |

Why it may still matter: `mcp.json` changed on the same morning as the Phase 2 audit, so something
writes it. Do not remove until the writer is identified.

## Gemini / Antigravity

| Field | Value |
| --- | --- |
| Path | `~/.gemini/` |
| Files | `settings.json` (2026-10-15), `config/mcp_config.json` (2026-10-22), `antigravity/mcp_config.json`, `config/skills/browseros-neo` |
| Executable | none (`gemini`, `antigravity` not on PATH; no app package) |
| Credential reference | none observed in the inspected MCP config |
| Classification | **Orphaned / possibly IDE-managed** — Antigravity may be an IDE whose binary is not installed here |

## GitHub Copilot CLI

| Field | Value |
| --- | --- |
| Path | `~/.copilot/` (mtime 2026-10-22) |
| Contents | `skills/browseros-neo`, `ide/`, `logs/`, `auth.db` |
| Executable | `/usr/bin/copilot` exists but is a **VS Code shim**; running it says the CLI is not installed |
| Credential reference | `auth.db` exists (not read) |
| Classification | **Orphaned CLI config / possibly active IDE integration** — `ide/` may be written by the VS Code Copilot extension |

## Cleanup checklist (requires explicit approval — Gate E)

1. **Backup**
   ```bash
   tar -C "$HOME" -czf ~/agent-config-backup-$(date +%F).tgz .kiro .gemini .copilot
   ```
2. **Credential review**: identify every token/header in the three configs by name; decide which are
   still valid.
3. **Revocation decision**: revoke tokens only if the tool is retired or the token was exposed.
4. **Removal**: remove config directories only after confirming no IDE/extension reads them.
5. **Verification**: confirm no harness logs errors, and that a reinstall can recreate the config.

Do not run this checklist until the Kiro writer and the Copilot IDE integration are understood.

## Related

- `docs/harnesses.md` — harness table and status.
- `inventory/harnesses.yaml` — machine-readable entries.
