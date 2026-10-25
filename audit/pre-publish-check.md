# Pre-publication validation — Phase 3 final

- **Date:** 2026-10-25
- **Branch:** `docs/toolbox-audit` (based on `origin/main`, HEAD `d40efaed`)
- **Target:** `https://github.com/<owner>/agent-toolbox.git`
- **Decision:** **READY TO PUBLISH** as a feature branch. `main` is not modified.

## Checklist

| # | Check | Status | Evidence |
| ---: | --- | --- | --- |
| 1 | No secret values | **Pass** | `scripts/verify.sh` pattern scan + high-entropy scan: 0 hits. Examples use `<REDACTED>` / `YOUR_*_HERE`. |
| 2 | No private/authenticated URLs | **Pass** | No embedded credentials; no authenticated URLs; MCP URLs are public or localhost. |
| 3 | No absolute `/home/<username>` paths | **Pass** | `grep "$HOME"` = 0 in repository files. |
| 4 | No private org/client/project names | **Pass** | Four private tokens replaced with `<private-org>` / `<private-project>` throughout. Managed-skill local paths are placeholders. |
| 5 | No unlicensed third-party source copied | **Pass** | No third-party skill/plugin source vendored. Existing remote `NOTICE` (Apache-2.0 `mine/skill-creator/`) preserved. |
| 6 | Sanitized example configs | **Pass** | 7 examples; validated; placeholders only. |
| 7 | YAML / JSON / TOML validity | **Pass** | 6 inventories + 5 JSON + 1 TOML parse. |
| 8 | Markdown internal links | **Pass** | 0 broken relative links. |
| 9 | External links | **Pass** | 51 checked, 0 failed (2026-10-25). |
| 10 | Git history integration | **Pass** | Feature branch created from `origin/main`; remote history preserved; no force push. |

## Accepted warnings

| Warning | Assessment |
| --- | --- |
| Public GitHub handle appears in pre-existing remote files (`catalog.json`, `scripts/build.py`, `LICENSE`) | Already public in the repository; not a local path or secret. Pre-existing catalog content was not rewritten. |
| Claude runtime skill discovery not launched | Symlinks verified at filesystem level (333, 0 broken); launching Claude would execute an agent. |
| MCP runtime not started | Syntax, executable presence, package metadata and pins verified; no MCP handshake. |
| `codegraph` / `openagents` upstreams unresolved | Preserved and disabled in OMP; no package installed. |

## Skill migration validation

| Check | Result |
| --- | --- |
| Full-tree-identical candidates | 342 |
| Converted to symlinks | 333 |
| Broken symlinks | 0 |
| Excluded (`pm-*` no top-level SKILL.md) | 9 |
| Divergent kept as directories | 3 (`code-review`, `graphify`, `find-docs`) |
| `synced` / `.trash` preserved | Yes |
| Plugin-managed / built-in untouched | Yes |
| Rollback | Hardlink backup at `<private-backup>/claude-skills-hardlink` |

## MCP validation

| Check | Result |
| --- | --- |
| JSON syntax | Pass (OpenCode, OMP) |
| Executables present | `codebase-memory-mcp`, `hostinger-api-mcp`, `notebooklm-mcp` |
| Pins applied | `mcp-insomnia@0.8.2`, `@floriscornel/teams-mcp@1.0.1` |
| `gemini-notebook-mcp` | Linux path; Windows path removed |
| `codegraph`, `openagents` | Disabled/preserved; not installed |
| Runtime | **Intentionally not tested** |

## Remote integration

| Field | Value |
| --- | --- |
| Remote | `https://github.com/<owner>/agent-toolbox.git` |
| Base | `origin/main` (`d40efaed`) |
| Working branch | `docs/toolbox-audit` |
| Remote history preserved | Yes (feature branch, no merge/rebase/force) |
| Remote `main` overwritten | No |
| Curated catalog preserved | Yes (`catalog.json`, `data/`, `recommended/`, `mine/`, `skills/*.md`, `mcps/*.md`, original README body) |
| README collision | Resolved by appending an audit navigation section; original content preserved |
| License | Existing MIT `LICENSE` and `NOTICE` preserved |

## Publish step

Commit and push the feature branch only; do not touch `main`. Open a PR if the repository workflow
allows it. If the push or PR fails, the branch remains local and the failure is reported.

## Sign-off

| Gate | Status |
| --- | --- |
| Private-name sanitization | Pass |
| License decision | Pass (existing MIT preserved) |
| History integration | Pass (feature branch from `origin/main`) |
| Final checks | Pass |
| Blockers | **0** |
