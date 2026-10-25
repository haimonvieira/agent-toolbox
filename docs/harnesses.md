# Harnesses

Comparison of the harnesses **actually found on this machine** (not a general market comparison).

| Harness | Main role | Skills | MCP | Plugins | Hooks | Config location | Best use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OpenCode 2.1.4 | Terminal coding agent, primary | `~/.agents/skills` | 14 in config + plugin-injected | 1 plugin | Plugin hooks | `~/.config/opencode/` | Daily implementation work; multi-model routing |
| Claude Code 2.1.309 | Terminal coding agent | `~/.claude/skills` (duplicate) | 2 global | 1 plugin | Plugin hooks | `~/.claude/`, `~/.claude.json` | Deep reasoning (Opus), plugin ecosystem |
| Codex CLI 0.164.0 | Terminal coding agent | 5 system skills | 3 | 1 plugin | Config + plugin hooks | `~/.codex/config.toml` | Secondary agent, PR/review loops |
| OMP 18.12.6 | Terminal agent + orchestration | 55 managed + 40 plugin | 15 | 11 plugins + 4 extensions | Extensions + plugin hooks | `~/.omp/agent/` | Largest local toolset; multi-agent profiles |
| freebuff 0.2.34 | Terminal coding agent | none found | none found | none | none | unknown | Unknown; configured minimally |
| Zed 1.25.3 | Editor with agent panel | none | 1 context server | none | none | `~/.config/zed/settings.json` | Editing + quick agent assistance |
| Delta 0.20.1 | AI-native editor | none found | none found | none | none | unknown | Editing; provenance incomplete |
| VS Code + ChatGPT ext. | Editor + ChatGPT/Codex | none | none | 2 versions of one extension | none | `~/.vscode/extensions` | In-editor chat |
| Kiro | — (no executable) | 1 skill | 2 (1 broken service) | none | none | `~/.kiro/` | **Orphaned config** |
| Gemini/Antigravity | — (no executable) | 1 skill | 1 | none | none | `~/.gemini/` | **Orphaned config** |
| GitHub Copilot CLI | — (VS Code shim only) | 1 skill | none | none | none | `~/.copilot/` | **Orphaned config** |

## Terminal agents

### OpenCode

- **Command:** `opencode` → `~/.nvm/versions/node/v24.22.0/bin/opencode`
- **Version:** 2.1.4, installed as npm global `@opencode/cli` under nvm Node 24.22.0.
- **Config:** `~/.config/opencode/opencode.json` (MCP + plugin), `cli.json` (TUI),
  `AGENTS.md` (global instructions, created during the audit), `oh-my-opencode-slim.json`.
- **Skills:** reads the shared `~/.agents/skills` tree (inferred from the skill list exposed by the
  running session) plus plugin-provided skills.
- **MCP:** 14 servers in `opencode.json`; four disabled (`aas-core`, `codegraph`,
  `codebase-memory`, `openagents`).
- **Plugins:** `oh-my-opencode-slim` 3.0.6 (added 2026-10-25 11:07). Injects `context7`,
  `gh_grep`, `omgskills` and orchestration agents at runtime.
- **Hooks:** no native hook config found; plugin-managed.
- **Notes:** the live config changed while the audit ran. Treat the file, not this table, as truth.

### Claude Code

- **Command:** `claude` → `~/.local/bin/claude` → `~/.local/share/claude/versions/2.1.309`
- **Version:** 2.1.309, native install (`installMethod: native`), auto-updates disabled.
- **Config:** `~/.claude/settings.json`, `~/.claude.json` (MCP + account state), `~/.claude/CLAUDE.md`.
- **Skills:** `~/.claude/skills` — 348 directories, a copy of `~/.agents/skills`; 345 SKILL.md files
  are byte-identical, `code-review` and `graphify` differ.
- **MCP:** `browseros-neo` (HTTP) and `pencil` (stdio) globally; no project-level MCPs.
- **Plugins:** `ponytail@ponytail` 5.3.2 enabled.
- **Hooks:** none in `settings.json`; `ponytail` supplies SessionStart, SubagentStart, and
  UserPromptSubmit hooks.

### Codex CLI

- **Command:** `codex` → npm global `@openai/codex` 0.164.0.
- **Config:** `~/.codex/config.toml` (model `gpt-6-luna`, MCP, plugins, trusted hook hashes).
- **Skills:** `~/.codex/skills/.system` contains 5 built-in skills (`imagegen`, `openai-docs`,
  `review-agent`, `skill-creator`, `skill-installer`). No user-installed skills.
- **MCP:** `graphify`, `browseros-neo`, `pencil`.
- **Plugins:** `ponytail@ponytail` enabled; `openai-curated-remote` is a downloaded marketplace
  cache, not an enabled plugin set.
- **Hooks:** trusted hashes for `ponytail` and for a project on an external volume. The project
  hooks (`state_freshness.py`, 3 s timeout) are inspectable only while that volume is mounted.
- **Notes:** `config.toml` is mode `600`; it contains no plaintext API keys.

### OMP (Oh My Pi)

- **Command:** `omp` → standalone 256 MB binary at `~/.local/bin/omp` 18.12.6.
- **Config:** `~/.omp/agent/config.yml`, `mcp.json`, `models.yml`; `~/.omp/marketplaces.json`;
  `~/.omp/plugins/installed_plugins.json`.
- **Skills:** 55 locally authored skills in `~/.omp/agent/managed-skills`, plus 40 from plugins.
- **MCP:** 15 entries, including 4 broken executables and 1 Windows-only path.
- **Plugins:** 11 installed across 6 marketplaces.
- **Extensions:** 4 TypeScript files in `~/.omp/agent/extensions` (Orca status/prefill/spinner and
  a local PR-template guard).
- **Profiles:** `code-reviewer`, `qa`, `repo-researcher`, `security-reviewer`, `team-lead`.
  `team-lead` is a Git clone of a personal repository (`github-command-center`).
- **Notes:** the most complex local setup; also the most exposed to stale caches and path bugs.

### freebuff

- **Command:** `freebuff` → npm global 0.2.34.
- **Upstream:** `https://github.com/CodebuffAI/freebuff-private` is private (public HTTP 404).
- **Config:** no config directory or MCP/plugin configuration was found.
- **Status:** installed, minimally configured, purpose not independently verifiable.

## Editor-embedded agents

| Tool | Version | MCP | Notes |
| --- | --- | --- | --- |
| Zed | 1.25.3 | `browseros-neo` via `context_servers` | Settings file is JSONC; one MCP configured |
| Delta | 0.20.1 | none found | AI-native editor; hidden data dir `~/.oleafly` holds provider/MCP settings and secret-like fields |
| VS Code ChatGPT extension | 26.1021.22027 + 26.1007.21434 | none | Two versions installed; older one is stale |

## Orphaned harness configurations

These have configuration on disk but **no executable, desktop entry, snap, or flatpak** was found:

| Harness | Config | Evidence | Risk |
| --- | --- | --- | --- |
| Kiro | `~/.kiro/settings/mcp.json`, `~/.kiro/skills/starryai` | `mcp.json` modified 2026-10-24; no `kiro` binary | Stale auth header and localhost MCP; unclear origin |
| Gemini / Antigravity | `~/.gemini/settings.json`, `config/mcp_config.json`, `antigravity/mcp_config.json` | No `gemini` binary or app package | One MCP + one skill remain configured |
| GitHub Copilot CLI | `~/.copilot/` (skill + `auth.db`) | `/usr/bin/copilot` is only a VS Code shim; running it reports the CLI is not installed | Auth database present, not read |

## Compatibility notes

- The **same `SKILL.md` format** is consumed by OpenCode, Claude Code, Codex, OMP, and most editor
  agents. The directory each harness reads differs.
- **Ponytail** ships integration manifests for Claude Code, Codex, OpenCode, Gemini, Copilot,
  Cursor, and Qoder; only Claude, Codex, and OMP are active here.
- **MCP JSON shape differs** between harnesses (`mcpServers` vs `mcp.servers`, `type` vs
  `serverUrl`). See [mcps.md](mcps.md) and `configs/examples/`.
- **Windows paths** appear in two configs (`gemini-notebook-mcp`, some marketplace catalog paths).
  They cannot work on this Linux host.
- **Canonical skill store:** `~/.agents/skills` is read directly by OpenCode, Codex, OMP, and Zed;
  Claude Code needs per-skill symlinks. The evidence matrix is in [skills.md](skills.md#can-agentskills-be-canonical).
