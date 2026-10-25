# Phase 3 — remediation report

- **Date:** 2026-10-25
- **Scope:** execute safe remediation, consolidation, sanitization, and feature-branch publication.
- **Not executed:** no MCP server was started; no hook was executed; no agent session was launched for
  skill discovery.

## 1. Gate C1 — completed

| Item | Value |
| --- | --- |
| Package | `claude-agent-sdk` |
| Version | `0.2.174` |
| Upstream | `anthropics/claude-agent-sdk-python` |
| License | MIT |
| Venv | `~/.claude/security/agent-sdk-venv` |
| Import | succeeds (`__file__` present) |
| Bootstrap | healthy venv → `NOOP_VENV`; pip not run |
| Residual risk | If the import probe fails, the hook may clear the venv and install unpinned latest |

No reinstall was performed in Phase 3.

## 2. MCP changes

| MCP | Before | After | Version | Status | Runtime tested |
| --- | --- | --- | --- | --- | --- |
| `gemini-notebook-mcp` | Windows `.EXE` path | `~/.local/bin/notebooklm-mcp` | uv tool 0.15.7 | Repaired | No |
| `insomnia` | `npx -y mcp-insomnia` | `npx -y mcp-insomnia@0.8.2` | 0.8.2 | Pinned | No |
| `teams-mcp` | `…teams-mcp@latest` | `…teams-mcp@1.0.1` | 1.0.1 | Pinned | No |
| `codebase-memory` | missing executable | globally installed | 0.12.1 (MIT) | Repaired | No |
| `hostinger-api` | missing executable | globally installed | 3.8.1 (MIT) | Repaired | No |
| `codegraph` | missing; unverified npm name | preserved, `enabled: false` in OMP | none | Unknown upstream | No |
| `openagents` | missing; unrelated npm `agn` | preserved, `enabled: false` in OMP | none | Unknown upstream | No |

`aas-core` remains 19.15.0 in OpenCode (disabled) and 18.10.0 in OMP; both preserved.
`oh-my-opencode-slim` remains managed by OpenCode at resolved 3.0.6.

Backups: `~/.agent-toolbox-backups/20261025-phase3/opencode.json.bak`,
`omp-mcp.json.bak` (mode 600, private).

## 3. Skill consolidation

| Metric | Value |
| --- | ---: |
| Full-tree-identical skills | 342 |
| Converted to symlinks | 333 |
| Excluded (`pm-*`, no top-level SKILL.md) | 9 |
| Divergent, kept separate | 3 (`code-review`, `graphify`, `find-docs`) |
| `synced` / `.trash` kept | 2 |
| Broken symlinks | 0 |
| Remaining real directories in Claude store | 14 |
| Plugin-managed names overlapping | 16 |
| Codex built-ins | 5 |

Pilot: `ab-testing` converted first, symlink resolved, tree hash matched. Rollback available at
`<private-backup>/claude-skills-hardlink`.

## 4. Stale cache cleanup

Moved to private backup (not committed):

- `superpowers` 6.3.0 (active: 7.0.0)
- `security-guidance` 2.0.7 (active: 2.0.15)
- VS Code ChatGPT 26.1007 (active: 26.1021)

No active version was removed. Empty `github` plugin directory was left in place because the plugin
is still recorded as installed.

## 5. Sanitization

- Four private organization/project tokens replaced with `<private-org>` / `<private-project>` in
  the public inventory and documentation.
- External-volume project names removed from docs.
- No local absolute paths or usernames added.
- No secret values written.
- Pre-existing public GitHub handle in remote catalog files left untouched.

## 6. Git integration

| Item | Result |
| --- | --- |
| Base | `origin/main` (`d40efaed`) |
| Branch | `docs/toolbox-audit` (recreated on remote base) |
| Remote history | preserved |
| Curated catalog | preserved |
| Force push | none |
| `main` modified | no |
| Commit | `06504dd` |
| PR | #1 |

## 7. Remaining human decisions

- `codegraph` and `openagents`: identify upstreams or remove later.
- `code-review`, `graphify`, `find-docs`: harness-specific variants; manual review.
- Kiro/Gemini/Copilot configs: preserved pending owner/consumer identification.
- GSD cluster: exact origin/version unknown; not called stale.
- Global symlink into external volume: preserved.
