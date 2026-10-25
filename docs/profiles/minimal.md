# Profile: Minimal agent setup (`minimal`)

- **Status:** active  ·  **Profile version:** 1
- **Reproducibility:** `mostly_reproducible`
- **Evidence:** Verified locally (last verified 2026-10-25)

## Purpose

The smallest useful setup that this environment supports: one terminal harness, the canonical skill store, and no optional integrations. Designed for a quick start or a constrained machine, not for feature parity.

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
8. Verification (`./scripts/audit.sh --profile minimal`).

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

- **Commands:** `opencode`
- **Files:** `~/.config/opencode/opencode.json`
- **Directories:** `~/.agents/skills`

## External dependencies

_none_

## Reproducibility

- **Status:** `mostly_reproducible`
- **Reasons:**
  - harness-opencode: upstream not verified

## Notes

Intentionally excluded: marketplace plugins (ponytail, superpowers, security-guidance, sonarqube, coderabbit, lethe, best-of), all MCP servers (design, browser, cloud, email, knowledge-graph and notebook integrations), the OpenCode orchestration plugin and its injected MCP servers, editor integrations, and OMP-specific components. Adding them later does not invalidate this profile.

## Related documentation

- [Environment profiles](../profiles.md)
- [Harnesses](../harnesses.md)
- [MCP servers](../mcps.md)
- [Plugins](../plugins.md)
- [Hooks](../hooks.md)
- [Installation guide](../installation.md)
- [Inventory](../../inventory/)
