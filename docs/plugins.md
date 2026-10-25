# Plugins and extensions

A plugin bundles skills, commands, agents, hooks, MCP definitions, or UI for one harness. Plugins
are **not portable by copy**: each harness installs and enables them differently.

OMP records installed plugins without an explicit enabled flag; "Enabled" below means **installed and present in the active cache** (activation inferred, not runtime-verified).

Full metadata: [inventory/plugins.yaml](../inventory/plugins.yaml): 15 plugin bundles plus 4 OMP
extension files (19 entries; `ponytail` is shared by three harnesses).

## Installed

| Plugin | Version | Harness | Source | License | Status |
| --- | --- | --- | --- | --- | --- |
| `ponytail` | 5.3.2 | Claude Code, Codex, OMP | `DietrichGebert/ponytail` | MIT | Enabled in all three |
| `superpowers` | 7.0.0 | OMP | `obra/superpowers` | MIT | Enabled; duplicates standalone skills |
| `sonarqube` | 2.6.0 | OMP | `anthropics/claude-plugins-official` | Sonar Source-Available v1.0 | Enabled; redistribution restricted |
| `42crunch-api-security-testing` | 1.5.5 | OMP | official marketplace | unknown (no LICENSE at root) | Enabled |
| `coderabbit` | 1.1.1 | OMP | official marketplace | MIT | Enabled |
| `feature-dev` | 0.0.0 | OMP | official marketplace | see plugin | Enabled |
| `context7` | 0.0.0 | OMP | official marketplace | unknown | Enabled; cache contains README only |
| `github` | 0.0.0 | OMP | official marketplace | unknown | Enabled; **empty install directory** |
| `security-guidance` | 2.0.15 (catalog 2.0.16) | OMP | official marketplace | Apache-2.0 | Enabled; startup hook installs a Python package |
| `lethe` | 0.19.0 | OMP | `teimurjan/lethe` | unknown (no LICENSE) | Enabled; adds hooks |
| `best-of` | 0.2.0 | OMP | `wolfiesch/omp-best-of` | MIT | Enabled |
| `oh-my-opencode-slim` | 3.0.6 | OpenCode | `alvinunreal/oh-my-opencode-slim` | MIT | Enabled (added during audit) |
| `envsitter-guard` | 0.1.0 resolved (`@latest`) | OpenCode | `boxpositron/envsitter-guard` | MIT | Enabled, floating |
| `opencode-mem` | 2.34.0 resolved (`@latest`) | OpenCode | `tickernelz/opencode-mem` | MIT | Enabled, floating |
| `openai.chatgpt` (VS Code extension) | 26.1021.22027 | VS Code | Marketplace | unknown | Enabled; older 26.1007 moved to backup |
| OMP extensions (4 files) | — | OMP | Orca-managed + locally authored | unknown | Loaded from `~/.omp/agent/extensions` |

## Phase 2 verification notes

| Plugin | Finding |
| --- | --- |
| `security-guidance` 2.0.15 | Apache-2.0. Marketplace catalog offers **2.0.16**. **Gate C1 completed:** `claude-agent-sdk==0.2.174` is pre-installed in the venv; bootstrap returns `NOOP_VENV`. Residual failure-path install remains. |
| `superpowers` 7.0.0 | Installed; 6.3.0 remains in cache. 16 of its skills overlap the standalone global store. |
| `ponytail` 5.3.2 | Same version intentionally installed in Claude Code, Codex, and OMP. |
| `sonarqube` 2.6.0 | Sonar Source-Available License v1.0 — not open source. |
| `github` 0.0.0 | Install directory is empty; the plugin is not actually usable. |

## Version conflicts — Phase 2 classification

| Conflict | Versions | Owner | Classification | Notes |
| --- | --- | --- | --- | --- |
| `superpowers` | 6.3.0 (cache) vs 7.0.0 (installed) | OMP marketplace | **Stale cache candidate** | 7.0.0 is the active install; 6.3.0 is from 2026-09-12 |
| `security-guidance` | 2.0.7 (cache) vs 2.0.15 (installed) vs 2.0.16 (catalog) | OMP marketplace | **Stale cache + update candidate** | Update only after reviewing the hook diff |
| `aas-core` | 19.15.0 (OpenCode, disabled) vs 18.10.0 (OMP) | two harness configs | **Unknown / consolidation candidate** | Different catalogs; align before relying on IDs |
| `ponytail` | 5.3.2 × 3 harnesses | Claude, Codex, OMP | **Intentional coexistence** | Same version; separate hook runs |
| `superpowers` skills | standalone + plugin 7.0.0 + plugin 6.3.0 | skills store + plugin | **Safe consolidation candidate (after review)** | 16 overlapping names |
| `code-review` | shared vs Claude copy vs coderabbit plugin | three owners | **Manual review** | Content differs; see dedup plan |

No version was removed or changed.

## Stale or orphaned

| Item | Path | Why it is stale |
| --- | --- | --- |
| `superpowers` 6.3.0 | moved to private backup | Superseded by 7.0.0; removed 2026-10-25 |
| `security-guidance` 2.0.7 | moved to private backup | Superseded by 2.0.15; removed 2026-10-25 |
| `openai-curated-remote` cache | `~/.codex/plugins/cache/openai-curated-remote` | ~30 downloaded plugin dirs; none enabled |
| `claude-plugins-official` catalog | `~/.claude/plugins/marketplaces/claude-plugins-official` | Catalog only; nothing installed from it |
| `superpowers-marketplace`, `ui-ux-pro-max-skill` catalogs | `~/.omp/marketplaces.json` | `catalogPath` has a malformed `/home/<user>/C:\Users\...` path |
| 13 `plugin:*` auth-cache entries | `~/.claude/mcp-needs-auth-cache.json` | Plugins not installed (design/marketing/engineering sets) |

## Install methods by harness

### Claude Code

```bash
# Marketplace add + install (official CLI syntax; verify with `claude plugin --help`)
claude plugin marketplace add <owner>/<repo>
claude plugin install <plugin>@<marketplace>
```

Locally observed: marketplace `ponytail` from `DietrichGebert/ponytail`, plugin `ponytail@ponytail`
enabled in `~/.claude/settings.json`. Plugin files live in `~/.claude/plugins/cache/`.

### Codex CLI

Plugins are declared in `~/.codex/config.toml`:

```toml
[marketplaces.ponytail]
source_type = "git"
source = "https://github.com/<owner>/<repo>.git"

[plugins."ponytail@ponytail"]
enabled = true
```

Installed plugins live in `~/.codex/plugins/cache/`. A marketplace cache may exist without any
plugin being enabled — that is the case for `openai-curated-remote`.

### OMP

State is in `~/.omp/plugins/installed_plugins.json`; marketplaces in `~/.omp/marketplaces.json`.
Install through OMP's plugin/marketplace UI or CLI (exact command not verified in this audit).
Plugin code is unpacked under `~/.omp/plugins/cache/plugins/<marketplace>___<plugin>___<version>`.

### OpenCode

Plugins are listed in `~/.config/opencode/opencode.json`:

```json
{ "plugin": ["oh-my-opencode-slim"] }
```

The package is resolved into `~/.cache/opencode/npm/` and configured by a sibling JSON file
(`oh-my-opencode-slim.json`). Because the entry is unpinned, the next resolution can pull a new
version.

## Duplicates and conflicts

- **Ponytail** is installed three times (Claude, Codex, OMP) at the same version. That is
  intentional for cross-harness use, but hooks run three times in three different agents.
- **Superpowers** skills exist standalone *and* in a plugin, with two plugin versions cached.
- **CodeRabbit** skills duplicate standalone `code-review` and `autofix`.
- **OMP marketplace paths** for `superpowers-marketplace` and `ui-ux-pro-max-skill` are broken:
  they point to `/home/<user>/C:\Users\<user>\.omp\...` instead of `~/.omp/...`. The actual JSON
  files sit in the home directory under a literal `C:\Users\...` directory name.
- **`github` plugin** has an empty install directory — the plugin is marked installed but has no
  content.

## Update and removal

| Harness | Update | Remove |
| --- | --- | --- |
| Claude Code | `claude plugin update <plugin>` (verify CLI) | `claude plugin uninstall <plugin>` |
| Codex | marketplace refresh + reinstall (verify CLI) | remove `[plugins."…"]` table |
| OMP | marketplace update in the UI | plugin uninstall in the UI |
| OpenCode | change/unpin the plugin entry, clear its npm cache dir | remove from `plugin` array |

No plugin was updated, removed, or executed during this audit.

**`security-guidance` status:** Gate C1 **completed** — `claude-agent-sdk==0.2.174` is pre-provisioned
and imports from `~/.claude/security/agent-sdk-venv`. The plugin remains installed at 2.0.15; no
update is required. The unpinned failure-path install is documented, not eliminated.

## License notes

- `sonarqube` uses the **Sonar Source-Available License v1.0**, not an OSI license. Do not copy its
  code into this repository.
- `lethe` and `42crunch-api-security-testing` have no LICENSE file in their installed cache.
  Treat redistribution rights as unknown.
- `ponytail`, `superpowers`, `coderabbit`, `best-of`, `oh-my-opencode-slim` include MIT LICENSE
  files locally.
- This repository vendors none of them.
