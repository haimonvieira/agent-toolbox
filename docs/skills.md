# Skills

## What a skill is here

A skill is a directory containing `SKILL.md` with YAML frontmatter (`name`, `description`) and
optional supporting files. Harnesses load the description and read the body when the task matches.
Skills may include executable scripts, assets, and references.

This repository does **not** vendor skill source code. It records where each skill came from and
how to reinstall it.

## Global vs project-local

| Scope | Path | Who reads it | Notes |
| --- | --- | --- | --- |
| Global (shared) | `~/.agents/skills/<name>/` | OpenCode, Codex, OMP, Zed; Claude via symlink | Canonical candidate: 349 directories |
| Global (Claude) | `~/.claude/skills/<name>/` | Claude Code | 347 directories; 343 identical to the shared store |
| Global (OMP) | `~/.omp/agent/managed-skills/<name>/` | OMP | 55 locally authored skills |
| Global (Codex) | `~/.codex/skills/.system/<name>/` | Codex | 5 built-in system skills; not user-managed |
| Project-local | `<repo>/.agents/skills/<name>/` | The harness working in that repo | 19 in the coordination project; one is the target of the global symlink |
| Plugin-provided | plugin cache `skills/` | The harness that installed the plugin | Not user-managed directly |
| Companion-app | `~/.config/opencode/skills`, `~/.copilot/skills`, `~/.gemini/config/skills`, `~/.kiro/skills` | Specific app | Single-skill installs (browseros-neo, starryai) |

## Can `~/.agents/skills` be canonical?

| Harness | Canonical store possible | Method | Symlink supported | Built-ins separate | Evidence |
| --- | --- | --- | --- | --- | --- |
| OpenCode | **Yes** | Reads `~/.agents/skills` directly | Folder entries | Yes (bundled/plugin) | [Official docs](https://opencode.ai/docs/skills/) |
| Codex CLI | **Yes** | `$HOME/.agents/skills` is the USER scope | Yes, follows symlink targets | Yes (`$CODEX_HOME/.system`) | [Official docs](https://learn.chatgpt.com/docs/build-skills) |
| OMP | **Yes** | `agents` provider; `skills.enableAgentsUser` defaults to `true` | Not documented | Yes (provider priorities) | [Official docs](https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md) |
| Zed | **Yes** | Global root is `~/.agents/skills` | Yes (docs recommend symlinks) | Yes (`create-skill`) | [Official docs](https://zed.dev/docs/ai/skills) |
| Claude Code | **Via symlink** | Personal root is `~/.claude/skills`; skill folders may be symlinks | Yes; dedups by target | Yes (bundled/plugin) | [Official docs](https://code.claude.com/docs/en/skills) |
| Delta | Unknown | Zed-based editor; no skill config found | Unknown | Unknown | Inferred |
| freebuff | Unknown | No documented skill path or local config | Unknown | Unknown | [Site](https://freebuff.com) |

**Conclusion:** a single canonical `~/.agents/skills` is feasible for four harnesses directly and for
Claude Code through per-skill symlinks. **Phase 3 converted 333 proven-identical Claude copies to
symlinks.** Plugin skills and built-ins remain separate. See
[skill-dedup-plan.md](../audit/skill-dedup-plan.md) and
[skill-full-tree-comparison.md](../audit/skill-full-tree-comparison.md).

## Current state (Phase 2, 2026-10-25)

| Metric | Value |
| --- | ---: |
| Entries in `~/.agents/skills` | 352 (349 directories, 1 symlink, 2 archives) |
| Tracked by the `skills` CLI lock file | 192 |
| Present locally but absent from the lock | 161 directories |
| Lock entries with no local directory | 3 (`planning-with-files`, `playwright-skill`, `ui-ux-pro-max`) |
| Codex built-in system skills | 5 (`imagegen`, `openai-docs`, `review-agent`, `skill-creator`, `skill-installer`) |
| Directories without a top-level `SKILL.md` | 10 (`pm-*` bundles, `synced/`) |
| Symlinks into an external volume | 1 (`coordenacao-commit-seguro`; breaks when unmounted) |
| Project-local skills | 19 in the coordination project (private; not inventoried individually) |
| Skills containing executable scripts | 62 (snapshot) |
| `~/.agents/skills` / `~/.claude/skills` size | 269 MB each |
| Full-tree-identical skills | 342 |
| Same name / different content | 4 (`code-review`, `find-docs`, `graphify`, `synced`) |
| Claude copies converted to symlinks | 333 |
| Claude real directories remaining | 14 |
| Plugin skills overlapping a global name | 16 |

Counts shift as the machine changes. Re-run `./scripts/audit.sh` before relying on a number; the snapshot is generated, the inventory is curated. Cluster-level provenance is in
[unknown-skills-triage.md](../audit/unknown-skills-triage.md).

The lock file `~/.agents/.skill-lock.json` (version 3) is the best provenance source: it records
`sourceUrl`, `skillPath`, `skillFolderHash`, and timestamps for 192 skills.

## Install a skill

### Recommended: install from an upstream repository with the skills CLI

```bash
# Discovery + install (verified on https://www.skills.sh/)
npx skills add <owner>/<repo>

# Example: a public repository with a skills/ directory
npx skills add obra/superpowers
```

Why recommended: the CLI records provenance in `.skill-lock.json`, which makes later audits and
updates possible. Prefer a pinned tag or commit when the CLI supports it; a bare `add` tracks the
default branch.

### Manual install (no CLI)

```bash
# 1. Clone the upstream at a known commit
git clone https://github.com/<owner>/<repo>.git /tmp/<repo>
cd /tmp/<repo> && git checkout <commit-sha>

# 2. Copy only the skill directory you need
mkdir -p ~/.agents/skills
cp -r /tmp/<repo>/skills/<skill-name> ~/.agents/skills/

# 3. Verify the expected structure
test -f ~/.agents/skills/<skill-name>/SKILL.md && echo OK
```

Do not copy the whole repository, its `.git`, its caches, or `node_modules`.

### From a plugin

Plugins install skills into their own cache and expose them automatically. Do not copy plugin
skills into `~/.agents/skills`; that creates the duplicates documented below.

## Use symlinks correctly

Use a symlink when you want **one canonical copy** consumed by several harnesses:

```bash
ln -s ~/.agents/skills/<skill-name> ~/.claude/skills/<skill-name>
```

Rules:

- Symlink to a path that is always mounted. The one existing broken skill points into an external
  volume and breaks when the volume is unmounted.
- Do not symlink a whole skill tree into a plugin cache; plugin updates may replace it.
- Record symlinks in `inventory/skills.yaml` (the `symlink_target` field).

## Update a skill

1. Read the upstream changelog at the recorded `upstream_repository`.
2. Check whether the local copy is modified (see below).
3. Reinstall with the same method used originally, pinned to a tag or commit.
4. Confirm `SKILL.md` changed as expected and that referenced scripts still exist.

The `skills` CLI's update subcommand was **not verified** in this audit; use the procedure
documented at <https://www.skills.sh/> for the installed CLI version. Manual installs are updated by
replacing the directory.

## Preserve locally modified skills before updating

```bash
# Compare local vs a fresh clone of the recorded upstream
git clone <upstream_repository> /tmp/upstream-skill
diff -ru /tmp/upstream-skill/skills/<name> ~/.agents/skills/<name> | head -100
```

If differences are intentional, copy them to a side directory (for example
`~/.agents/skills-local-patches/<name>/`) before replacing the skill, then re-apply.

The audit did **not** diff most skills against upstream; `locally_modified` is `unknown` in the
inventory unless stated otherwise.

## Remove a skill

```bash
# Manual removal (review first)
ls ~/.agents/skills/<skill-name>
rm -rf ~/.agents/skills/<skill-name>
```

Then remove its entry from `~/.agents/.skill-lock.json` if it was CLI-managed, and remove duplicate
copies in `~/.claude/skills` or harness-specific directories. This audit removed nothing.

## Identify duplicates

Phase 2 measurement:

- `~/.agents/skills` ↔ `~/.claude/skills`: **343 identical** `SKILL.md` hashes, **3 differing**
  (`code-review`, `find-docs`, `graphify`), 3 names only in the shared store (`autofix`, `mysql`,
  `postgres`), and `.trash` only in Claude.
- 16 plugin-provided names overlap a global copy (`superpowers` 7.0.0 plus stale 6.3.0, and
  `coderabbit`).
- `~/.agents/skills/synced/` is a nested 15-skill bundle and is not discoverable as a top-level skill.

Full classification and the non-destructive migration design:
[skill-dedup-plan.md](../audit/skill-dedup-plan.md). Only `SKILL.md` was hashed; supporting files
still need a full-tree comparison before any symlink is created.

Detection command (read-only):

```bash
find ~/.agents/skills ~/.claude/skills -name SKILL.md -print0 \
  | xargs -0 sha256sum | sort | uniq -w64 -d
```

## Verify the harness discovered a skill

There is no universal command. Use the harness's own skill list:

- **OpenCode:** start a session and inspect the available skills/commands; skill descriptions are
  injected into the session context.
- **Claude Code:** `/help` or the skills/commands list in the TUI.
- **OMP:** the skills picker in the TUI.
- **Codex:** check the skills list in the TUI and the configured `~/.codex/skills` directory.

A skill that does not appear is usually in the wrong directory, missing `SKILL.md`, or has invalid
frontmatter.

## Overlap to watch

| Cluster | Skills | Risk |
| --- | --- | --- |
| GSD workflow | 72 `gsd-*` | Unknown provenance; large surface area; conflicting workflow opinions |
| GitNexus | 12 `gitnexus-*` | Duplicated by the `pi-gitnexus` OMP package |
| Penpot | 12 `penpot-*` + 6 `source-command-penpot-*` | Two generations of the same guidance |
| Superpowers | 14 standalone + 14 in plugin 7.0.0 + 14 in plugin 6.3.0 | Version drift |
| Design taste | `ui-taste`, `design-taste-frontend`, `design-taste-frontend-v1`, `hallmark`, `impeccable` | Overlapping design guidance |

See `inventory/skills.yaml` for every entry, path, hash prefix, and provenance field.
