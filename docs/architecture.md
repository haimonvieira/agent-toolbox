# Architecture

Verified relationships in this setup. Every edge is backed by a local file or an official
documentation page; inferred edges are marked.

```text
                         ┌────────────────────────────────────────────┐
                         │           ~/.agents/skills                 │
                         │  canonical global skill store (349 dirs)   │
                         └───────┬──────────┬──────────┬──────────────┘
                                 │          │          │
              direct read        │          │          │        symlink (proposed)
        ┌────────────────────────┘          │          └──────────────┐
        │                                   │                         │
   ┌────▼─────┐   ┌──────────┐   ┌──────────▼───┐   ┌─────────┐  ┌────▼──────────┐
   │ OpenCode │   │  Codex   │   │     OMP      │   │   Zed   │  │ Claude Code   │
   └────┬─────┘   └────┬─────┘   └──────┬───────┘   └────┬────┘  └────┬──────────┘
        │              │                │                │            │
        │ plugin       │ plugin         │ plugins        │ MCP        │ plugin
   ┌────▼──────────┐   │                │                │            │
   │oh-my-opencode │   │                │                │            │
   │    -slim      │   │                │                │            │
   └────┬──────────┘   │                │                │            │
        │ injects      │                │                │            │
        ├─ context7     │                │                │            │
        ├─ gh_grep      │                │                │            │
        ├─ omgskills    │                │                │            │
        └─ skills       │                │                │            │
                         │                │                │            │
   ┌─────────────────────▼────────────────▼────────────────▼────────────▼─────────┐
   │                        MCP configurations per harness                        │
   │  opencode.json · .claude.json · codex config.toml · omp mcp.json · zed       │
   │  gemini mcp_config.json · kiro mcp.json                                      │
   └───────────────────────────────────┬──────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼────────────────────────────────┐
        │                              │                                │
  remote HTTP MCPs              local stdio MCPs                 local services
  (cloudflare, figma,           (pencil, insomnia,               (browseros :9010,
   graphify, doop)               teams, aas, broken ones)         obsidian :27200,
                                                                  starry :7600)
```

## Harness → configuration

| Harness | Config root | MCP file | Plugin mechanism | Skill source |
| --- | --- | --- | --- | --- |
| OpenCode | `~/.config/opencode` | `opencode.json` (`mcp.servers`) | `plugin` array → npm cache | `~/.agents/skills` (official) |
| Claude Code | `~/.claude` + `~/.claude.json` | `~/.claude.json` (`mcpServers`) | marketplace cache | `~/.claude/skills` (symlinks supported) |
| Codex CLI | `~/.codex` | `config.toml` (`[mcp_servers.*]`) | `[plugins.*]` + marketplace | `$HOME/.agents/skills` (official) |
| OMP | `~/.omp/agent` | `mcp.json` | `installed_plugins.json` + extensions | `~/.agents/skills` via `agents` provider (default on) |
| Zed | `~/.config/zed` | `settings.json` (`context_servers`) | none found | `~/.agents/skills` (official) |
| Delta | unknown | none found | none found | unknown (Zed-based, inferred) |
| freebuff | none found | none found | none found | not documented |
| VS Code ChatGPT | `~/.vscode/extensions` | none | extension | none |

## Dynamic ownership and injection

| Node | Type | Provided by | Injected by | Directly configured | Dynamic | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `context7` | MCP | `oh-my-opencode-slim` 3.0.6 | plugin | no | yes | Runtime session tools + plugin package |
| `gh_grep` | MCP | `oh-my-opencode-slim` | plugin | no | yes | Runtime session tools |
| `omgskills` | MCP | `oh-my-opencode-slim` | plugin | no | yes | Runtime session tools |
| `memory` | tool | plugin/runtime | plugin | no | yes | Observed at runtime; exact owner unverified |
| `pencil` | MCP | pen.dev app | — | yes (4 harnesses) | no | Config + binary |
| `browseros-neo` | MCP | BrowserOS | — | yes (6 harnesses) | no | Config |
| `security-guidance` | plugin + hooks | OMP marketplace | — | plugin install | no | `installed_plugins.json` + hook manifest |
| `ponytail` | plugin + hooks + skills | marketplace | — | plugin install | no | Config in 3 harnesses |
| `superpowers` | plugin + skills + hooks | OMP marketplace | — | plugin install | no | Installed 7.0.0; 6.3.0 stale |
| `pr-template-guard` | extension | local | — | extension file | no | Local TypeScript |

Only `oh-my-opencode-slim` demonstrably injects MCP servers at runtime. The `memory` tool appeared
alongside it but its provider is not proven; mark as **inferred**.

## Skill-store consumption

| Harness | Reads `~/.agents/skills` | Native store | Symlink support | Built-ins separate | Source |
| --- | --- | --- | --- | --- | --- |
| OpenCode | Yes | `~/.config/opencode/skills` + `~/.claude/skills` + `~/.agents/skills` | Folder entries | Yes (bundled/plugin) | <https://opencode.ai/docs/skills/> |
| Codex CLI | Yes (`$HOME/.agents/skills`) | `.agents/skills` + `.codex/skills` | Yes, follows symlink targets | Yes (`$CODEX_HOME/.system`) | <https://learn.chatgpt.com/docs/build-skills> |
| OMP | Yes (`agents` provider, `enableAgentsUser` default true) | `~/.omp/agent/skills` + `managed-skills` | Not documented | Yes (native/plugins/managed priorities) | <https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md> |
| Zed | Yes | `~/.agents/skills` only | Docs recommend symlinks for other paths | Yes (`create-skill`) | <https://zed.dev/docs/ai/skills> |
| Claude Code | No | `~/.claude/skills` | Yes, skill-folder symlinks; dedups by target | Yes (bundled/plugin) | <https://code.claude.com/docs/en/skills> |
| Delta | Unknown | Unknown | Unknown | Unknown | No config found |
| freebuff | Unknown | Unknown | Unknown | Unknown | No docs/config found |

## Hook ownership

| Hook | Owner | Managed by | Directly configured |
| --- | --- | --- | --- |
| Ponytail SessionStart / SubagentStart / UserPromptSubmit | `ponytail` plugin | plugin manager | no |
| Security-guidance SessionStart / prompt / post-tool / stop | `security-guidance` plugin | plugin manager | no |
| SonarQube SessionStart | `sonarqube` plugin | plugin manager | no |
| Superpowers SessionStart | `superpowers` plugin | plugin manager | no |
| Lethe index refresh | `lethe` plugin | plugin manager | no |
| `pr-template-guard` | local extension | OMP extension loader | yes (file) |
| Orca extensions (3) | Orca app (inferred) | OMP extension loader | yes (files) |
| Codex project hooks | project on external volume | Codex trusted hashes | yes (config) |
| Git hooks | none active | — | — |

## External-volume dependencies

```text
<external-volume>/<project>/
├── .agents/skills/coordenacao-commit-seguro   ← symlink target from ~/.agents/skills
└── .codex/hooks.json                          ← Codex trusted project hooks
```

| Dependency | Failure mode when unmounted |
| --- | --- |
| `~/.agents/skills/coordenacao-commit-seguro` | Broken symlink; skill unavailable |
| Codex project trusts (`config.toml`) | Hook paths unavailable; hooks skipped/fail |
| 19 project-local skills | Not discoverable in that project |
| OMP session history (path names only) | Historical sessions remain, but project files are unavailable |

The external placement appears intentional (large private project). No local fallback exists.

## Credential boundaries

```text
~/.config/opencode/opencode.json   (600) ─┐
~/.omp/agent/mcp.json              (600) ─┼─→ MCP auth headers / tokens
~/.kiro/settings/mcp.json          (600) ─┤
~/.oleafly/config.json             (600) ─┘   provider + GitHub + MCP tokens
```

No credential values are stored in this repository, and no credential is copied between configs.

## What is not proven

- Whether plugin-injected MCPs remain stable across plugin updates.
- Whether Delta reads the Zed skill store.
- Whether freebuff supports skills at all.
- Whether `memory` is provided by the plugin or by the harness itself.
- Runtime behaviour of every hook and MCP.


## Self-audit data flow

```text
allowlisted local paths
        │  scripts/audit.py collect (read-only)
        ▼
local-state/current.yaml  (sanitized, gitignored)
        │
        ├── compare with local-state/baseline.yaml (committed)
        ▼
audit/drift-report.yaml / .md, audit/backlog.md
        │
        └── repository validator (schemas, links, secrets, privacy)
                │
                └── GitHub Actions validates repository data only
```

The collector never reads environment values, credential values, or private content. Managed-skill
names are redacted; external-volume paths collapse to `<external-volume>/<project>`.
