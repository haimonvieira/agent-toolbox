# Profile: OpenCode (Go provider) (`opencode-go`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `mostly_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

OpenCode 2.1.4 running the oh-my-opencode-slim "opencode-go" preset, the npm plugins configured in opencode.json, the MCP servers configured in the same file, and the canonical skill store.

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
8. Verification (`./scripts/audit.sh --profile opencode-go`).

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
- **Optional:** `CONTEXT7_API_KEY`, `HOSTINGER_API_TOKEN`, `OA_WORKSPACE_TOKEN`

## Requirements

- **Commands:** `opencode`
- **Files:** `~/.config/opencode/opencode.json`, `~/.config/opencode/oh-my-opencode-slim.json`
- **Directories:** `~/.agents/skills`, `~/.cache/opencode/npm`

## External dependencies

_none_

## Reproducibility

- **Status:** `mostly_reproducible`
- **Reasons:**
  - harness-opencode: upstream not verified
  - plugin-oh-my-opencode-slim: upstream not verified
  - plugin-oh-my-opencode-slim: version resolved by the plugin manager
  - mcp-pencil: upstream not verified
  - mcp-pencil: needs a locally installed binary
  - mcp-browseros-neo: upstream not verified
  - mcp-cloudflare-api: upstream not verified
  - mcp-figma: upstream not verified
  - mcp-insomnia: needs an installed binary
  - mcp-teams-mcp: needs an installed binary
  - 2 floating version(s)

## Notes

The "opencode-go" preset selects model roles under the opencode-go provider (for example opencode-go/minimax-m3 and opencode-go/qwen3.8-max). No provider credentials belong in this profile. The injected MCP servers are owned by oh-my-opencode-slim and must not be configured independently.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
