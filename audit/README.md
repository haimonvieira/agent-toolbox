# Agent Toolbox

A personal, reproducible toolbox for the AI coding-agent ecosystem I use: harnesses, skills,
MCP servers, plugins, hooks, and the configuration patterns that connect them.

This repository documents **what is actually installed on this machine**, where it came from,
how to reproduce it, and what is broken, duplicated, or unclear. It is an audit-first map — not
a generic list of tools.

> **Status:** audit snapshot of 2026-10-25. Runtime verification of third-party components was
> **not performed for safety**. See [evidence levels](../docs/security.md#evidence-levels).

## Purpose

- Keep one canonical source of truth for my agent tooling.
- Make a new machine reproducible without copying caches, secrets, or `node_modules`.
- Surface duplicates, orphaned configuration, broken references, and supply-chain risk.
- Document installation and removal commands that are supported by evidence.

## What is documented

| Area | What you will find |
| --- | --- |
| [Harnesses](../docs/harnesses.md) | OpenCode, Claude Code, Codex CLI, OMP, freebuff, Zed, Delta, VS Code, plus orphaned Kiro/Gemini/Copilot config |
| [Skills](../docs/skills.md) | Global `~/.agents/skills` layout, Claude duplicate copy, OMP managed skills, plugin skills |
| [MCP servers](../docs/mcps.md) | 19 configured servers: transport, command, provenance, duplicates, broken executables |
| [Plugins](../docs/plugins.md) | 17 plugin/extension entries across five harnesses, plus stale caches |
| [Hooks](../docs/hooks.md) | Plugin lifecycle hooks, OMP extensions, Git hook status, orphaned project hooks |
| [Installation](../docs/installation.md) | Reproducible procedures by category, with verification and removal |
| [Updating](../docs/updating.md) | Safe update matrix and pinning policy |
| [Security](../docs/security.md) | Secret hygiene, evidence levels, findings, local secret-at-rest notes |
| [Troubleshooting](../docs/troubleshooting.md) | Known local failures and how to diagnose them |
| [Recommended resources](../docs/recommended-resources.md) | Verified skill directories and catalog sites |
| [Architecture](../docs/architecture.md) | Ownership/injection graph, skill-store compatibility, external-volume dependencies |

## Repository structure

```text
agent-toolbox/
├── README.md
├── .env.example                 # environment variable NAMES only
├── .gitignore
├── docs/                        # human-readable guides
├── inventory/                   # machine-readable YAML inventories
├── configs/examples/            # sanitized config examples per harness
├── scripts/                     # safe read-only audit/verify/link-check scripts
├── skills/README.md             # skills-specific guidance
├── mcps/README.md               # MCP-specific guidance
├── plugins/README.md            # plugin-specific guidance
└── audit/                       # audit report, changelog, environment snapshot
```

## Quick start

1. Read [docs/overview.md](../docs/overview.md) for scope, method, and the drift note.
2. Read [audit/AUDIT-REPORT.md](./AUDIT-REPORT.md) for the findings that need attention.
3. Use [inventory/](../inventory/) when you need exact paths, versions, and provenance.
4. Follow [docs/installation.md](../docs/installation.md) to rebuild the setup on another machine.
5. Run the read-only checks before making changes:

```bash
bash scripts/audit.sh    # inspect only; never starts MCPs or executes hooks
bash scripts/verify.sh   # repository consistency + secret-pattern scan
bash scripts/check-links.sh
```

## Harnesses

Installed and verified locally: **OpenCode 2.1.4**, **Claude Code 2.1.309**, **Codex CLI 0.164.0**,
**OMP 18.12.6**, **freebuff 0.2.34**, **Zed 1.25.3**, **Delta 0.20.1**, **VS Code + ChatGPT extension**.

Orphaned configuration without a locally installed executable: **Kiro**, **Gemini/Antigravity**,
**GitHub Copilot CLI**. Details in [docs/harnesses.md](../docs/harnesses.md).

## Skills

- `~/.agents/skills` is the primary global skill store: 351 entries at snapshot (352 at final check), 192 tracked by the
  `skills` CLI lock file, 159 with unknown provenance at snapshot (161 at final check).
- `~/.claude/skills` is a **byte-identical duplicate** of most of that tree (269 MB each).
- `~/.omp/agent/managed-skills` holds 55 locally authored, project-specific skills.
- Installed plugins provide another 40 skills, with overlap against the global store.

Start with [docs/skills.md](../docs/skills.md).

## MCP servers

19 distinct servers. Five have missing executables or impossible paths (`codegraph`,
`codebase-memory`, `openagents`, `hostinger-api`, `gemini-notebook-mcp`). Three remote
endpoints are local services that were not running at audit time (`browseros-neo`,
`obsidian-mcp-connector`, `starry`). Details in [docs/mcps.md](../docs/mcps.md).

## Plugins

13 plugin bundles plus 4 OMP extension files. `ponytail` is installed in Claude Code, Codex, and OMP.
OMP carries the largest set (11), including two superseded cache versions and a plugin with a
source-available license. Details in [docs/plugins.md](../docs/plugins.md).

## Hooks

No Git hooks are active and `core.hooksPath` is unset. Agent hooks are plugin-provided; the most
notable is the `security-guidance` SessionStart hook, which can create a Python venv and install a
package at session start. No hook was executed during the audit. Details in
[docs/hooks.md](../docs/hooks.md).

## Recommended resources

Verified discovery sites: [skills.sh](https://www.skills.sh/), [aaskills.tech](https://aaskills.tech/),
[omgskills.com](https://omgskills.com/). See
[docs/recommended-resources.md](../docs/recommended-resources.md) for what each one is, how to use it,
and the security checks required before installing anything.

## Security

- No secrets are stored in this repository.
- Environment variables are recorded by **name only**.
- Third-party source code is **not vendored**; the repository documents upstream sources instead.
- Discovery directories are not trusted sources. Verify the upstream repository, inspect scripts,
  check the license, and review requested permissions before installing.
- Before publishing this repository, re-read the note about project-specific skill names in
  [docs/security.md](../docs/security.md#before-publishing-this-repository).

## Updating the toolbox

Re-run the audit after meaningful changes:

```bash
bash scripts/audit.sh > /tmp/agent-toolbox-audit.txt
# compare versions/paths with inventory/, then update the affected YAML and docs
```

The update matrix (what updates itself, what is pinned, what must be manual) is in
[docs/updating.md](../docs/updating.md).

## Phase 2 — remediation plan

Phase 2 did **not** change the machine. It turned the audit into evidence-backed plans:

| Document | Purpose |
| --- | --- |
| [phase2-start.md](./phase2-start.md) | Baseline, remote state, divergence |
| [skill-dedup-plan.md](./skill-dedup-plan.md) | Duplicate classification + canonical-store migration design |
| [unknown-skills-triage.md](./unknown-skills-triage.md) | 153 unknown entries clustered by origin |
| [pre-publish-check.md](./pre-publish-check.md) | Pass/Warning/Blocker gates before publication |
| [architecture.md](../docs/architecture.md) | Ownership/injection graph and skill-store compatibility |

**Remote:** a public GitHub repository already exists with **6 unrelated commits on `main`**. The
local branch is unborn and has no remote configured. No fetch, merge, rebase, push, or history
change was performed. Integration is **Gate F** and is blocked until private names are sanitized.

**Credential permissions:** the four reviewed configs are all mode `600` now (Phase 1 saw `644`,
`777`, `664`). No rotation is recommended without exposure evidence.

## Audit status

| Item | Status |
| --- | --- |
| Audit snapshot | Complete (2026-10-25) |
| Repository organization | Phase 3 complete on `docs/toolbox-audit` |
| Remote integration | **Complete** — branch based on `origin/main`; pushed; PR #1 |
| Commit / push | **Done** — commit `06504dd`; branch `docs/toolbox-audit`; PR #1 |
| Runtime verification of MCPs/hooks/plugins | **Not performed for safety** |
| Repository license | Existing MIT `LICENSE` and Apache-2.0 `NOTICE` preserved |
| Public-release review | **Complete** — private names sanitized; checks passed |

## Disclaimer

Third-party tools, skills, plugins, and MCP servers belong to their respective authors and are
governed by their own licenses. This repository documents them and links to upstream sources; it
does not redistribute their source code. Names and descriptions are used for identification only.
