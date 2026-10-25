# Profile: Claude Code (`claude-code`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `mostly_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

Claude Code 2.1.309 (native install) with the ponytail plugin, its MCP servers in ~/.claude.json, and the canonical skill store consumed through per-skill symlinks in ~/.claude/skills.

## What this profile is not

Declarative only. Loading a profile installs nothing, changes no configuration and starts no server. It is a checklist that can be compared with the current machine.

## Installation order

1. Runtime prerequisites (`requirements.commands`, minus the harness itself).
2. Harness.
3. Plugins (marketplace or npm resolver).
4. Canonical skill store `~/.agents/skills`.
5. Harness-specific skill stores and built-in skills.
6. MCP packages and remote services.
7. Sanitized configuration files.
8. Verification (`./scripts/audit.sh --profile claude-code`).

## Harnesses

| Component | Requirement | Ownership | Version | Upstream |
| --- | --- | --- | --- | --- |
| _none_ | | | | |

## Plugins

| Component | Requirement | Ownership | Version | Upstream |
| --- | --- | --- | --- | --- |
| _none_ | | | | |

## MCP servers

| Component | Requirement | Ownership | Version | Upstream |
| --- | --- | --- | --- | --- |
| _none_ | | | | |

## Skills

| Component | Requirement | Ownership | Version | Upstream |
| --- | --- | --- | --- | --- |
| _none_ | | | | |

## Hooks

| Component | Requirement | Ownership | Version | Upstream |
| --- | --- | --- | --- | --- |
| _none_ | | | | |

## Environment variables (names only)

- **Required:** _none_
- **Optional:** _none_

## Requirements

- **Commands:** `claude`
- **Files:** `~/.claude/settings.json`, `~/.claude.json`
- **Directories:** `~/.claude/skills`, `~/.agents/skills`

## External dependencies

_none_

## Reproducibility

- **Status:** `mostly_reproducible`
- **Reasons:**
  - harness-claude-code: upstream not verified
  - plugin-ponytail: upstream not verified
  - mcp-pencil: upstream not verified
  - mcp-browseros-neo: upstream not verified

## Notes

Claude Code only reads ~/.claude/skills, so the canonical store is exposed with per-skill symlinks (333 currently). Plugin and bundled skills stay separate, and the name "synced" is reserved by Claude Code.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
