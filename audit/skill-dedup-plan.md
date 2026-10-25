# Skill de-duplication plan

- **Date:** 2026-10-25
- **Method:** SHA-256 of each `SKILL.md`, directory-name comparison, mtime inspection. No skill script was executed. Only `SKILL.md` was hashed; supporting files were **not** compared tree-wide.
- **Constraint:** nothing was deleted, moved, or replaced.

## Measured state

| Comparison | Count |
| --- | ---: |
| `~/.agents/skills` directories | 349 |
| `~/.claude/skills` directories | 347 (excluding `.trash`) |
| Names in both | 346 |
| Identical `SKILL.md` hash | 343 |
| Same name, different content | 3 (`code-review`, `find-docs`, `graphify`) |
| Only in `~/.agents` | 3 (`autofix`, `mysql`, `postgres`) |
| Only in `~/.claude` | 1 (`.trash`, not a skill) |
| Plugin skills overlapping a global name | 16 |
| OMP managed-skill overlaps | 0 |
| Codex built-in names overlapping a global name | 1 (`skill-creator`, different content) |

## Safe candidate for symlink

The **343 identical `SKILL.md` pairs** are candidates for:

1. Keep `~/.agents/skills/<name>` as the only real copy.
2. Replace `~/.claude/skills/<name>` with a symlink to it.

Before execution, each candidate still needs a **full-directory comparison** (assets, scripts, references), because the hash covered only `SKILL.md`. Claude Code documents that a personal skill folder may be a symlink to a directory elsewhere and loads the skill once if several locations point to the same target.

```bash
# Read-only pre-check for one skill (do not run as part of this audit)
diff -r ~/.agents/skills/<name> ~/.claude/skills/<name>
```

If the trees are identical, the proposed per-skill change is:

```bash
# Requires Gate D approval. Not executed.
rm -r ~/.claude/skills/<name>            # destructive: approval required
ln -s ~/.agents/skills/<name> ~/.claude/skills/<name>
```

For bulk migration, prefer a script that verifies every tree first and supports `--dry-run`.

## Different content — manual review required

| Skill | `~/.agents` copy | `~/.claude` copy | Assessment |
| --- | --- | --- | --- |
| `code-review` | 7,767 bytes, 2026-10-21, `metadata.version: 0.1.0` | 4,403 bytes, 2026-09-26, no version | Version skew (267 diff lines). The shared copy is newer and CodeRabbit-branded; the Claude copy is older. Do **not** symlink until one is chosen. |
| `graphify` | 40,775 bytes, 2026-09-28 | 41,051 bytes, 2026-10-20 | The Claude copy is newer (35 diff lines). Local modification or newer upstream unknown. Manual review. |
| `find-docs` | 8,131 bytes, 2026-10-25 11:07:54 | 7,881 bytes, 2026-10-25 11:07:54 | Same-second creation, 3 diff lines. Likely two installer writes of the same skill. Review, then keep one. |

## Must remain separate

| Item | Reason |
| --- | --- |
| `autofix`, `mysql`, `postgres` | Exist only in `~/.agents`; no duplicate to reconcile |
| `.trash` | Claude Code's deleted-skill quarantine, not a skill |
| `~/.agents/skills/synced/` | Nested 15-skill bundle from claude.ai sync; harnesses scan one level only. Claude reserves `synced` for its own sync directory. Do not flatten blindly. |
| `~/.omp/agent/managed-skills` | 55 locally authored project skills; no overlap with the shared store |

## Plugin-managed — do not touch

16 names overlap a plugin-provided skill. Plugin precedence differs by harness; copying plugin skills into the canonical store creates shadowing and version drift.

| Name(s) | Plugin owner |
| --- | --- |
| `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` | `superpowers` 7.0.0 (plus standalone copies) |
| `code-review`, `autofix` | `coderabbit` 1.1.1 (plus standalone copies) |

Handling: choose **either** the plugin **or** the standalone copy per harness. Do not symlink one over the other. Plugin updates can replace their own cache at any time.

## Built-in — do not touch

| Source | Skills |
| --- | --- |
| Codex `~/.codex/skills/.system` | `imagegen`, `openai-docs`, `review-agent`, `skill-creator`, `skill-installer` |
| Claude Code bundled | Managed by the harness; `disableBundledSkills` / `skillOverrides` control visibility |
| OMP native/plugin providers | Discovery priorities 90–100; managed skills last (5) |
| Zed built-in | `create-skill` |

`skill-creator` exists both as a Codex built-in and as a standalone global skill with different content. Keep both: they are different implementations for different harnesses.

## Unknown

| Item | Why |
| --- | --- |
| `moli-*` (3) | Upstream identified (`lexmount/moli`, Apache-2.0) but no binary/config remains locally; possibly stale |
| `penpot-*` + `source-command-penpot-*` (18) | Generated/migrated, no verified skill repository |
| `find-docs` | Installer not recorded |
| 55 OMP managed | Locally generated; project-specific |

## Proposed consolidation design (not executed)

| Harness | Reads canonical store? | Action after approval |
| --- | --- | --- |
| OpenCode | Yes, `~/.agents/skills` | None |
| Codex CLI | Yes, `$HOME/.agents/skills` | None |
| OMP | Yes, `agents` provider enabled by default (`skills.enableAgentsUser=true`) | None |
| Zed | Yes, `~/.agents/skills` | None |
| Claude Code | No, only `~/.claude/skills` | Replace identical copies with per-skill symlinks; keep the 3 divergent skills real until resolved |
| Delta | Unknown (Zed-based) | Verify before changing anything |
| freebuff | Unknown; no documented skill path | Do not consolidate |

## Execution order (Gate D, if approved)

1. Freeze: record `sha256sum` of every `SKILL.md` and a full-tree manifest.
2. Resolve the 3 divergent skills manually (choose version, preserve any local edits).
3. Verify full-tree equality for the 343 candidates.
4. Convert one pilot skill (low risk, no scripts) and verify Claude discovers it.
5. Bulk-convert with `--dry-run` first.
6. Keep `~/.claude/skills/.trash` and `synced/` untouched.
7. Re-run `scripts/audit.sh` and update this plan.

## Risks

- Claude Code may treat `synced` as reserved; never symlink the canonical store's `synced` bundle into it.
- Duplicate names across locations can make OpenCode/Codex list or load the wrong copy.
- A symlinked skill on an unmounted volume fails (see `coordenacao-commit-seguro`).
- Deleting a copy before verifying supporting files can lose local edits.
- This plan does not cover `~/.claude/skills/.trash` cleanup; that is separate and destructive.


## Phase 3 execution result (2026-10-25)

Full-tree hashing (paths + contents, not only `SKILL.md`) produced **342 FULLY_IDENTICAL** skills.

- **333 converted** to per-skill symlinks in `~/.claude/skills` → `~/.agents/skills/<name>`.
- **9 excluded** (`pm-*` bundles): no top-level `SKILL.md`, so a directory symlink would not be
  discovered as a skill.
- **3 divergent** (`code-review`, `graphify`, `find-docs`) kept as real directories.
- `synced` and `.trash` kept as real directories.
- Pilot: `ab-testing` converted first; symlink resolved and tree hash matched the canonical copy.
- Rollback: full hardlink backup at `<private-backup>/claude-skills-hardlink` (269 MB logical).
- Remaining real directories in `~/.claude/skills`: 14.
- Claude runtime discovery was **not** launched; verification is filesystem-level only.
