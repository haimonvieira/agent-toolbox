# Profile: Shared baseline expectations (`base`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `fully_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

Expectations shared by every profile: the runtime prerequisites and the canonical skill store. Contains no harness-specific components on purpose.

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
8. Verification (`./scripts/audit.sh --profile base`).

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

- **Commands:** `git`, `node`, `npm`
- **Files:** _none_
- **Directories:** `~/.agents/skills`

## External dependencies

_none_

## Reproducibility

- **Status:** `fully_reproducible`

## Notes

~/.agents/skills is the canonical skill store for OpenCode, Codex CLI, OMP and Zed. Claude Code consumes it through per-skill symlinks; plugin and built-in skills stay in their own stores.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
