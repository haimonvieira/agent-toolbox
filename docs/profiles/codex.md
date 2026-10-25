# Profile: Codex CLI (`codex`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `mostly_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

Codex CLI 0.164.0 with the ponytail plugin, its built-in skills, the canonical shared skill store, and the MCP servers configured in ~/.codex/config.toml.

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
8. Verification (`./scripts/audit.sh --profile codex`).

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

- **Commands:** `codex`
- **Files:** `~/.codex/config.toml`
- **Directories:** `~/.codex/skills`, `~/.agents/skills`

## External dependencies

- `external-nvme` (required: False) — Project-local Codex trust entries and hooks live on an external volume; the profile works without them.

## Reproducibility

- **Status:** `mostly_reproducible`
- **Reasons:**
  - harness-codex-cli: upstream not verified
  - plugin-ponytail: upstream not verified
  - mcp-browseros-neo: upstream not verified
  - mcp-pencil: upstream not verified

## Notes

Codex reads $HOME/.agents/skills as its USER skill scope and follows symlinked skill folders, so the canonical store needs no copy. Built-in skills stay in $CODEX_HOME/.system.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
