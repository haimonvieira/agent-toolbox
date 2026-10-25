# Profile: Oh My Pi (OMP) (`omp`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `mostly_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

OMP 18.12.6 with its marketplace plugins, local extensions, managed skills, and the MCP servers configured in ~/.omp/agent/mcp.json.

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
8. Verification (`./scripts/audit.sh --profile omp`).

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
- **Optional:** `HOSTINGER_API_TOKEN`, `OA_WORKSPACE_TOKEN`, `CONTEXT7_API_KEY`

## Requirements

- **Commands:** `omp`
- **Files:** `~/.omp/agent/config.yml`, `~/.omp/agent/mcp.json`, `~/.omp/plugins/installed_plugins.json`
- **Directories:** `~/.omp/agent/managed-skills`, `~/.omp/plugins`

## External dependencies

_none_

## Reproducibility

- **Status:** `mostly_reproducible`
- **Reasons:**
  - harness-oh-my-pi-omp: upstream not verified
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
  - mcp-pencil: upstream not verified
  - mcp-browseros-neo: upstream not verified
  - mcp-cloudflare-api: upstream not verified
  - mcp-figma: upstream not verified
  - mcp-codebase-memory: upstream not verified
  - mcp-hostinger-api: upstream not verified
  - mcp-gemini-notebook-mcp: upstream not verified

## Notes

OMP discovers the canonical skill store through its "agents" provider (skills.enableAgentsUser defaults to true) and adds 55 locally authored managed skills. Five agent profiles exist locally: code-reviewer, qa, repo-researcher, security-reviewer and team-lead.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
