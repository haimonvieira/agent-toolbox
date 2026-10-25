# Overview

## What this repository is

A map of the AI coding-agent tooling installed on one Linux workstation, created from a
read-only audit on **2026-10-25**. It covers five layers:

1. **Harnesses** — the programs that host an agent loop (OpenCode, Claude Code, Codex CLI, OMP,
   freebuff, editor-embedded agents).
2. **Skills** — `SKILL.md` packages that add procedural knowledge.
3. **MCP servers** — Model Context Protocol endpoints that add tools and data.
4. **Plugins / extensions** — bundles that add skills, commands, agents, hooks, or UI.
5. **Hooks** — lifecycle commands that run around agent events.

## Method

Pass A (audit snapshot) was completed before any repository file was written:

- Located and inspected the repository target (none existed; a new repository was created).
- Enumerated executables with `command -v` and `--version`.
- Read configuration files statically; values of secret-like keys were redacted in memory.
- Computed skill counts and duplicate hashes without executing skill scripts.
- Queried public package registries and GitHub for upstream metadata only.
- Checked executable existence and listening localhost ports.
- Did **not** start MCP servers, execute hooks, load plugins, or run health/doctor commands.

Pass B wrote this documentation. The original environment state is captured in
[environment-snapshot.md](../audit/environment-snapshot.md); repository edits did not change it.

## Environment drift (important)

The machine changed **during** the audit:

- At **11:07** local time, `~/.config/opencode/opencode.json` gained the
  `oh-my-opencode-slim` plugin, an LSP section, a new `~/.config/opencode/AGENTS.md`, and a
  plugin config file.
- A second OpenCode process was running (`opencode.exe`).
- As a result, `context7` and `gh_grep` MCPs and 12 skills became available at runtime.

Those additions are documented as **observed drift**, not as part of the 10:55 snapshot. Values
from the original snapshot (counts, versions, findings) remain marked accordingly. If you are
reading this later, re-run `scripts/audit.sh` before trusting a specific path or version.

## Environment at a glance

| Layer | Count (snapshot) | Notes |
| --- | ---: | --- |
| Harnesses with a local executable | 8 | 4 terminal agents, 3 editor apps, 1 extension |
| Harness configs without an executable | 3 | Kiro, Gemini/Antigravity, Copilot CLI |
| Distinct skills (union of all sources) | ~436 | 351 global + 55 OMP managed + 40 plugin-provided + 5 Codex built-in |
| Global skill directory entries | 351 | `~/.agents/skills`; 1 symlink into an external volume |
| Claude skill copies | 348 | Byte-identical copies, 269 MB |
| Distinct MCP servers | 19 | 2 unresolved upstreams disabled; 3 repaired; 3 local services down |
| Installed plugins/extensions | 17 | Plus 3 stale/orphaned caches |
| Hook sites documented | 17 | Plugin hooks, OMP extensions, 1 orphaned project hooks file |
| Active Git hooks | 0 | `core.hooksPath` unset |

## Evidence levels

Every inventory entry carries one of:

| Level | Meaning |
| --- | --- |
| **Verified locally** | Path, version, or config was read directly on this machine. |
| **Verified upstream** | A public registry/repository was queried and matched. |
| **Locally detected, upstream not verified** | Present locally; no upstream confirmation. |
| **Inferred** | Conclusion drawn from indirect evidence (e.g., directory layout). |
| **Unknown** | Not determinable from safe inspection. |

Runtime behaviour of third-party code is always **not verified** in this snapshot, even when
the file exists and is configured.

## Scope boundaries

In scope: agent harnesses, their configs, skills, MCP definitions, plugins, hooks, and the
package metadata needed to reproduce them.

Out of scope: general desktop packages, browser profiles, password stores, cloud credentials,
shell history, unrelated repositories, and any recursive scan of the home directory.

## Reading order

1. [AUDIT-REPORT.md](../audit/AUDIT-REPORT.md) — findings by severity.
2. [harnesses.md](harnesses.md) — what runs the agents.
3. [skills.md](skills.md), [mcps.md](mcps.md), [plugins.md](plugins.md), [hooks.md](hooks.md).
4. [installation.md](installation.md) and [updating.md](updating.md) — rebuild and maintain.
5. [security.md](security.md) — secret handling and pre-publication checks.
