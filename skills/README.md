# Skills (repository entry point)

This directory is documentation only — **no skill source code is vendored here**.

- Full inventory: [`inventory/skills.yaml`](../inventory/skills.yaml) (463 entries).
- Install, update, duplicate and removal guide: [`docs/skills.md`](../docs/skills.md).
- Discovery sites: [`docs/recommended-resources.md`](../docs/recommended-resources.md).

## Store layout

| Store | Scope | Count | Managed by |
| --- | --- | ---: | --- |
| `~/.agents/skills` | global shared | 350 entries | `skills` CLI + manual |
| `~/.claude/skills` | global Claude | 348 dirs | duplicate copy |
| `~/.omp/agent/managed-skills` | global OMP | 55 | OMP autolearn |
| plugin caches | plugin | 40 | plugin installers |
| `~/.codex/skills/.system` | global Codex | 5 | Codex built-in |

## Policy

1. Install from upstream with provenance (`npx skills add <owner>/<repo>`), pinned where possible.
2. Do not copy plugin-provided skills into the global store.
3. Prefer symlinks over copies when the same skill must serve several harnesses.
4. Never copy `node_modules`, caches, or secrets.
5. Check the upstream license and scripts before enabling a skill.
