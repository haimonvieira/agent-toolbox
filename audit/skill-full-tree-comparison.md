# Skill full-tree comparison

- **Date:** 2026-10-25
- **Method:** SHA-256 over every relative file path + file content in each skill directory. Symlinks recorded by target. Excluded: `.DS_Store`, `__pycache__`, `.git`.
- **No script executed.**
- Stores compared: `~/.agents/skills` (canonical) vs `~/.claude/skills` (harness).

## Summary

| Class | Count |
| --- | ---: |
| `FULLY_IDENTICAL` | **342** |
| `CONTENT_DIFFERS` | **4** (`code-review`, `find-docs`, `graphify`, `synced`) |
| `ONLY_IN_CANONICAL_STORE` | **9** |
| `ONLY_IN_HARNESS_STORE` | **1** (`.trash`) |
| Plugin-managed (separate cache) | 40 skills / 16 overlapping names |
| Built-in (Codex) | 5 |

The earlier `SKILL.md`-only comparison found 343 identical. Full-tree hashing reduced the safe set
to **342**; `synced` is Claude's reserved sync directory and is excluded.

## Safe candidates — 342 fully identical

Every one of these has identical relative paths and identical file contents, including scripts,
references, and assets. They are eligible for per-skill symlinks after a pilot.

Not converted automatically:

- `synced` (reserved; harness-managed)
- `.trash` (quarantine, not a skill)
- the 3 divergent skills below
- plugin-managed and built-in skills

## Divergent — manual review / intentionally separate

| Skill | Difference | Assessment |
| --- | --- | --- |
| `code-review` | Shared copy is newer (2026-10-21, CodeRabbit metadata `0.1.0`) and has 2 extra references (`auth-recovery.md`, `cli-workflows.md`). Claude copy is 2026-09-26. | Not proven strict superset; both reference harness-specific execution. **Manual review required**; excluded from consolidation. |
| `graphify` | Claude copy (2026-10-20) uses `Agent`/`CLAUDE.md`; shared copy (2026-09-28) uses `Task`/`AGENTS.md`. Also differs in `references/hooks.md`. | Harness-specific variants. **Intentionally separate**; do not symlink. |
| `find-docs` | Shared copy adds a Codex-specific sandbox note (2 lines). | Codex-only content; the Claude copy is correctly tailored. **Intentionally separate**. |
| `synced` | Claude.ai sync directory, reserved name. | **Intentionally separate**; never symlink. |

## Only in canonical store (9)

`autofix`, `mysql`, `postgres`, `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`,
`ponytail-help`, `ponytail-review`.

- `autofix`, `mysql`, `postgres` are global skills without a Claude copy.
- The `ponytail` skills appeared after the Phase 2 snapshot (plugin/drift); they are not in Claude's
  personal store.

## Only in harness store (1)

`.trash` — Claude Code's deleted-skill quarantine. Not a skill; preserve.

## Plugin-managed (do not touch)

16 names overlap plugin-provided skills. They remain in plugin caches:

`autofix`, `brainstorming`, `code-review`, `dispatching-parallel-agents`, `executing-plans`,
`finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`,
`subagent-driven-development`, `systematic-debugging`, `test-driven-development`,
`using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`,
`writing-skills`.

## Built-in (do not touch)

Codex: `imagegen`, `openai-docs`, `review-agent`, `skill-creator`, `skill-installer`.
Claude bundled skills are harness-managed and not part of the personal directory.

## Decision

- Convert the **342 FULLY_IDENTICAL** Claude directories to symlinks after a pilot.
- Keep `code-review`, `graphify`, `find-docs`, `synced`, `.trash` as real directories.
- Keep plugin and built-in skills untouched.
