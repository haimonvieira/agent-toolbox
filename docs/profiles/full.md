# Profile: Full supported environment (`full`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `partially_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

Every component of the local environment that has a verified upstream and a documented install path. Unknown upstreams, orphaned configurations and private tools are excluded from "required" and listed as unresolved.

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
8. Verification (`./scripts/audit.sh --profile full`).

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
- **Optional:** `CONTEXT7_API_KEY`, `HOSTINGER_API_TOKEN`

## Requirements

- **Commands:** `opencode`, `claude`, `codex`, `omp`, `freebuff`, `zed`
- **Files:** `~/.config/opencode/opencode.json`, `~/.claude/settings.json`, `~/.codex/config.toml`, `~/.omp/agent/mcp.json`
- **Directories:** `~/.agents/skills`, `~/.claude/skills`, `~/.omp/agent/managed-skills`

## External dependencies

- `external-nvme` (required: False) — Project-local Codex hooks and trust entries only.

## Reproducibility

- **Status:** `partially_reproducible`
- **Reasons:**
  - 6 component(s) excluded as unresolved
  - harness-opencode: upstream not verified
  - harness-claude-code: upstream not verified
  - harness-codex-cli: upstream not verified
  - harness-oh-my-pi-omp: upstream not verified
  - harness-freebuff: upstream not verified
  - harness-zed: upstream not verified
  - harness-vs-code-chatgpt-extension: upstream not verified
  - plugin-ponytail: upstream not verified
  - plugin-superpowers: upstream not verified
  - plugin-security-guidance: upstream not verified
  - plugin-sonarqube: upstream not verified
  - plugin-coderabbit: upstream not verified
  - plugin-lethe: upstream not verified
  - plugin-best-of: upstream not verified
  - plugin-feature-dev: upstream not verified
  - plugin-context7: upstream not verified
  - plugin-42crunch-api-security-testing: upstream not verified
  - plugin-oh-my-opencode-slim: upstream not verified
  - plugin-oh-my-opencode-slim: version resolved by the plugin manager
  - plugin-envsitter-guard: upstream not verified
  - plugin-opencode-mem: upstream not verified
  - mcp-pencil: upstream not verified
  - mcp-pencil: needs a locally installed binary
  - mcp-browseros-neo: upstream not verified
  - mcp-cloudflare-api: upstream not verified
  - mcp-figma: upstream not verified
  - mcp-insomnia: needs an installed binary
  - mcp-teams-mcp: needs an installed binary
  - mcp-aas-core: needs an installed binary
  - mcp-codebase-memory: upstream not verified
  - mcp-codebase-memory: needs an installed binary
  - mcp-hostinger-api: upstream not verified
  - mcp-hostinger-api: needs an installed binary
  - mcp-gemini-notebook-mcp: upstream not verified
  - mcp-gemini-notebook-mcp: needs a locally installed binary
  - 1 floating version(s)

## Notes

This profile intentionally excludes unknown-upstream MCPs, orphaned harness configurations and unverified private tools from "required". The canonical skill store, plugin caches and built-in skills remain separate locations. The openagents MCP entry was removed on 2026-10-25 and the OpenCode npm plugins are pinned to exact versions.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
