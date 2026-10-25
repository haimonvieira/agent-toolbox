# Environment snapshot

Read-only record of what was inspected before repository documentation was written.

## Repository phase 0

| Check | Result |
| --- | --- |
| Repository lookup (`~`, depth ≤ 7, excluding caches/node_modules) | **No `agent-toolbox` directory existed** |
| Working directory repository | none (`~/` is not a Git repo) |
| Action | Created `~/agent-toolbox`, branch `docs/toolbox-audit`, no commit, no remote |
| Existing README/docs to preserve | none (new repository) |
| Existing LICENSE | none |
| User changes in the working tree | none (new repository) |

Because the repository did not exist, there was no pre-existing content to preserve or overwrite.

## Commands used (representative)

All read-only. No command printed environment variables, shell history, credentials, or secret values.

```text
command -v / --version for: opencode claude codex omp freebuff zed delta git gh node npm uv npx
ls / stat on known config directories
python3 JSON/TOML/YAML parsing with in-memory redaction of secret-like keys
find with maxdepth limits and symlink pruning
sha256sum / Python hashing for duplicate detection
ss -ltn (localhost listening check only)
npm view <pkg> version repository.url license
curl -s -o /dev/null -w '%{http_code}' against public GitHub/registry/docs URLs
git config --global --get core.hooksPath
git remote -v inside one discovered profile repository (sanitized)
```

Not used: `env`, `printenv`, shell history, keychain/credential dumps, browser stores, recursive home
scans, MCP handshakes, hook execution, plugin loading, `doctor`/health commands, package installs,
`sudo`.

## Paths inspected

```text
~/.config/opencode/{opencode.json,cli.json,service.json,AGENTS.md,oh-my-opencode-slim.json,skills/}
~/.claude/{settings.json,CLAUDE.md,plugins/,skills/,mcp-needs-auth-cache.json,ponytail-statusline.sh}
~/.claude.json (MCP + project keys only; account state not copied)
~/.codex/{config.toml,plugins/,skills/}
~/.omp/{agent/{config.yml,mcp.json,extensions/,managed-skills/},plugins/,marketplaces.json,profiles/}
~/.agents/{.skill-lock.json,skills/}
~/.gemini/{settings.json,config/,antigravity/}
~/.kiro/{settings/mcp.json,skills/}
~/.copilot/{skills/,ide/,auth.db (not read)}
~/.config/zed/settings.json (context_servers only)
~/.config/github-copilot/ (metadata only)
~/.oleafly/config.json (key names only; values not read)
~/.vscode/extensions/openai.chatgpt-*/package.json
~/TeleDrive/.git/hooks
~/Applications/pen (MCP binary existence)
```

## Findings at a glance

| Item | Count |
| --- | ---: |
| Harnesses with executable | 8 |
| Harness configs without executable | 3 |
| Global skill entries (`~/.agents/skills`) | 351 |
| Skills in `skills` CLI lock | 192 |
| Skills not in lock | 159 |
| Stale lock entries | 3 |
| Broken skill symlinks | 1 |
| Skills with executable scripts | 62 |
| Claude duplicate skill dirs | 348 (269 MB) |
| OMP managed skills | 55 |
| Plugin-provided skills | 40 |
| Distinct MCP servers | 19 |
| Broken MCP entries | 5 |
| MCP local services down at audit | 3 |
| Installed plugins/extensions | 17 |
| Hook sites documented | 17 |
| Active Git hooks | 0 |

## Drift timeline (environment changed during the audit)

| Time | Observation |
| --- | --- |
| 10:48–10:52 | OpenCode config backed up (`opencode.json.bak-20261025-104956`), MCP list stable |
| 10:55 | Snapshot baseline captured |
| 11:07 | `opencode.json` gained `plugin: ["oh-my-opencode-slim"]`, LSP config; `AGENTS.md`, `oh-my-opencode-slim.json`, `tui.json` created; another `opencode.exe` process running |
| 11:07+ | `context7`, `gh_grep` MCPs and 12 plugin skills appeared in the live session |
| 11:2x | `omgskills` MCP and a `memory` tool appeared |
| 11:25 | External volume mounted; the `coordenacao-commit-seguro` symlink began resolving and the Codex project hooks became inspectable |

The audit did not cause these changes. They are recorded so later readers know why counts and live
sessions may disagree. The repository documents both the baseline and the additions.

## Limitations

- Runtime behaviour of MCPs, hooks, plugins, and skill scripts is **not verified**.
- Licenses were read only where a local LICENSE file or package metadata existed; otherwise they are
  marked unknown.
- Skills not present in the lock were not diffed against upstream.
- The external volume referenced by one symlink and two Codex projects was **unmounted at the
  baseline and mounted later in the audit**; findings that depend on it are marked as conditional.
- Project-local skills inside that volume (19) were counted but not individually inventoried: the
  project is private.
- Windows-side installations (paths such as `C:\Users\...`) were not inspected.
