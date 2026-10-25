# Updating

## Principles

1. **Pin what you can.** Unpinned `@latest` / `npx -y` entries are the main reproducibility gap.
2. **Update one layer at a time** (harness → plugin → skills → MCP) so a failure is attributable.
3. **Read hook diffs before updating a plugin.** Plugin updates can change automatic commands.
4. **Re-run the audit** after updates and update `inventory/` and this repository.
5. **Never run a downloaded installer** just because a tool prompts you to.

## Update matrix

| Component | Current | Mechanism | Pinned? | Recommended action |
| --- | --- | --- | --- | --- |
| OpenCode | 2.1.4 | `npm i -g @opencode/cli@latest` | no | Update deliberately; note version in inventory |
| Claude Code | 2.1.309 | native installer; auto-update disabled | effectively pinned | Update manually via official procedure |
| Codex CLI | 0.164.0 | `npm i -g @openai/codex@latest` | no | Update deliberately |
| OMP | 18.12.6 | standalone release binary | yes (binary) | Replace binary from upstream release |
| freebuff | 0.2.34 | `npm i -g freebuff@latest` | no | Low priority |
| Zed / Delta | 1.25.3 / 0.20.1 | vendor app updater | yes (bundle) | Use app updater |
| Skills (`~/.agents`) | mixed | `npx skills add <repo>` | mostly branch-tracking | Re-add pinned tags/commits; diff first |
| Claude skill copies | — | manual/duplicate | n/a | Replace copies with symlinks or re-sync |
| OMP managed skills | local | OMP autolearn | n/a | Review before reuse on another machine |
| MCP `insomnia` | 0.8.2 | pinned npx | **yes** | Applied Phase 3 |
| MCP `teams-mcp` | 1.0.1 | pinned npx | **yes** | Applied Phase 3 |
| MCP `aas-core` | 19.15.0 / 18.10.0 | pinned, inconsistent | partially | Align both harnesses |
| MCP `codebase-memory` | 0.12.1 | global npm | **yes** | Applied Phase 3 |
| MCP `hostinger-api` | 3.8.1 | global npm | **yes** | Applied Phase 3 |
| MCP `codegraph` | unknown | `codegraph` command | n/a | **Do not install until upstream is identified** |
| Plugins | mixed | harness marketplace | versions recorded | Update via marketplace; read hook diffs |
| `security-guidance` | 2.0.15 | OMP marketplace | pinned by install | SDK pre-provisioned; no update required |
| VS Code ChatGPT ext. | 26.1021.22027 | VS Code auto-update | no | Uninstall the older duplicate |

## Safe update procedure

```bash
# 0. Snapshot current state (read-only)
bash scripts/audit.sh > /tmp/before.txt

# 1. Read upstream release notes and license
# 2. Update one component
# 3. Verify version and basic startup (do not run untrusted health commands)
<component> --version

# 4. Re-run the audit and diff
bash scripts/audit.sh > /tmp/after.txt
diff -u /tmp/before.txt /tmp/after.txt
```

For skills, update in a staging directory first:

```bash
git clone <upstream> /tmp/skill-update
git -C /tmp/skill-update checkout <tag-or-commit>
diff -ru /tmp/skill-update/skills/<name> ~/.agents/skills/<name> | head -100
```

## Pinning policy (recommended)

| Layer | Pin to |
| --- | --- |
| npm MCP servers | exact version (`pkg@1.2.3`) |
| Skills | tag or commit; record in the lock file |
| Plugins | marketplace version; record install path mtime/version |
| Harness CLIs | exact npm version for npm installs; keep the native installer version directory |
| Standalone binaries | keep the release artifact name/version in inventory |

## What updates automatically here

- VS Code extensions.
- Anything declared `@latest` (OpenCode plugin, `teams-mcp`).
- Plugin marketplaces when refreshed (not the same as updating installed plugins).
- Skills installed by a branch-tracking `skills add` only when re-run.

## Rollback

- npm tools: `npm i -g <pkg>@<previous-version>`.
- Native Claude: keep the previous version directory under `~/.local/share/claude/versions/` and
  re-point the symlink (manual; verify with `claude --version`).
- Plugins: reinstall the previous marketplace version; old cache directories may still exist
  (`superpowers` 6.3.0, `security-guidance` 2.0.7).
- Skills: keep a copy of the previous directory before replacing it.

## After updating: documentation checklist

- [ ] `inventory/harnesses.yaml` version + binary path
- [ ] `inventory/skills.yaml` regenerated (`scripts/audit.sh` prints the generator hint)
- [ ] `inventory/mcps.yaml` package version
- [ ] `inventory/plugins.yaml` version + stale caches
- [ ] `inventory/hooks.yaml` if a plugin's hook manifest changed
- [ ] `audit/CHANGELOG-AUDIT.md` entry
