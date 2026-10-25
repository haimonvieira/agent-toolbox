# Recommended resources

Discovery sites verified during the audit (HTTP 200 on 2026-10-25). All three are **catalogs or
installers**, not trusted publishers. See the security note at the end.

## Skill directories

### skills.sh — The Agent Skills Directory

- **URL:** <https://www.skills.sh/>
- **Type:** catalog + CLI installer + leaderboard (by Vercel).
- **What it provides:** a searchable directory of skills, packs, topics, "official" collections,
  security audits, and install counts. The CLI is `npx skills add <owner/repo>`.
- **How to use it:** discover a skill, then **install from the upstream repository**, not from the
  directory page. Prefer a tag/commit.
- **Installation:** semi-automatic. `npx skills add <owner>/<repo>` clones and installs; it is not a
  one-click web install.
- **Evidence locally:** `~/.agents/.skill-lock.json` is written by this CLI (version 3), with
  `sourceUrl`, `skillPath`, `skillFolderHash`, and timestamps for 192 skills.
- **Verify upstream:** open the skill's source repository, confirm the `SKILL.md` path and commit,
  read the scripts, check the license.
- **Precautions:** install counts are not a security signal; a popular skill can still run arbitrary
  code. `skills add` at branch head is not pinned.

### aaskills.tech — AAS Core

- **URL:** <https://aaskills.tech/>
- **Type:** skill catalog + local workflow/MCP contract ("agent chooses, you stay in control").
- **What it provides:** a catalog of Agentic Awesome Skills, a local CLI/MCP (`aas mcp`), and a
  review-before-install workflow. The npm package is `agentic-awesome-skills`.
- **How to use it:** browse the catalog, let the agent select exact IDs, review the recorded plan,
  then install separately.
- **Installation:** manual/contract-driven. The MCP entry exists locally (`aas-core`) at pinned but
  **conflicting** versions: 19.15.0 (OpenCode, disabled) and 18.10.0 (OMP).
- **Verify upstream:** <https://github.com/sickn33/agentic-awesome-skills> (MIT, verified).
- **Precautions:** two versions in two harnesses will produce different catalogs. Align them before
  relying on IDs.

### omgskills.com

- **URL:** <https://omgskills.com/>
- **Type:** discovery site + macOS menu-bar app + catalog API/MCP.
- **What it provides:** search across GitHub and X, curated lists, trending skills, one-click install
  on macOS, and a public catalog. It also exposes an MCP (`omgskills`) that was added to this
  OpenCode session during the audit.
- **How to use it:** discover, then use a **pinned install plan**. The MCP exposes
  `pinned_install.repo`, `path`, `commit_sha`, and `skill_md_sha`; records marked
  `discovery_only` must not be installed from `install_cmd`.
- **Installation:** automatic only in the macOS app; on Linux use the catalog/API and install
  manually or with the `skills` CLI.
- **Verify upstream:** follow `github_url` and compare `skill_md_sha`.
- **Precautions:** "trending on X" is not curation. The app is macOS-only; this host is Linux.

## Skill source repositories already in use

These are upstream repositories recorded in the local skills lock (all returned HTTP 200 during the
audit). They are sources, not directories:

| Repository | Used for |
| --- | --- |
| <https://github.com/obra/superpowers> | Core engineering workflow skills (brainstorming, TDD, reviews, worktrees) |
| <https://github.com/anthropics/skills> / <https://github.com/anthropics/knowledge-work-plugins> | Document, frontend, and knowledge-work skills |
| <https://github.com/openai/skills> | Codex-oriented engineering skills |
| <https://github.com/vercel-labs/skills> / <https://github.com/vercel-labs/agent-skills> | Agent and web engineering skills |
| <https://github.com/mattpocock/skills> | TypeScript, diagnosis, planning, TDD |
| <https://github.com/addyosmani/agent-skills> | Web performance and quality |
| <https://github.com/coreyhaines31/marketingskills> | Marketing skills (49 installed) |
| <https://github.com/heygen-com/hyperframes> | Video/motion skills (21 installed) |
| <https://github.com/remotion-dev/skills> | Programmatic video |
| <https://github.com/Leonxlnx/taste-skill> | Design taste skills |
| <https://github.com/cloudflare/skills> | Cloudflare |
| <https://github.com/supabase/agent-skills> | Supabase/Postgres |
| <https://github.com/getsentry/skills> | Sentry |
| <https://github.com/better-auth/skills> | Auth |
| <https://github.com/planetscale/database-skills> | MySQL/Postgres |
| <https://github.com/stablyai/orca> | Orca CLI/orchestration |

## Plugin marketplaces in use

| Marketplace | Source | Used by |
| --- | --- | --- |
| `claude-plugins-official` | <https://github.com/anthropics/claude-plugins-official> | Claude Code catalog, OMP (7 plugins) |
| `ponytail` | <https://github.com/DietrichGebert/ponytail> | Claude Code, Codex, OMP |
| `superpowers-marketplace` | <https://github.com/obra/superpowers-marketplace> | OMP (catalog path currently malformed) |
| `ui-ux-pro-max-skill` | <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> | OMP (catalog path currently malformed) |
| `teimurjan` (lethe) | <https://github.com/teimurjan/lethe> | OMP |
| `omp-best-of` | <https://github.com/wolfiesch/omp-best-of> | OMP |

## Official harness documentation

| Harness | Docs |
| --- | --- |
| OpenCode | <https://opencode.ai/docs> |
| Claude Code | <https://docs.claude.com/en/docs/claude-code/overview> |
| Codex | <https://developers.openai.com/codex> |
| OMP | <https://github.com/can1357/oh-my-pi> |
| MCP specification | <https://modelcontextprotocol.io> |
| Zed | <https://zed.dev/docs> |
| Kiro | <https://kiro.dev/docs> |
| Antigravity | <https://antigravity.google/docs> |
| Copilot CLI | <https://docs.github.com/en/copilot/how-tos/copilot-cli> |
| freebuff | <https://freebuff.com> |

## Security note

> Discovery directories are not automatically trusted sources. Before installing a skill, MCP
> server, plugin, or hook, verify the upstream repository, inspect executable code, check the
> license, review requested permissions/environment variables, and prefer pinned versions when
> appropriate.

Additional checks for this setup:

- Prefer `pinned_install` metadata when a catalog provides it; reject `discovery_only` records.
- Do not run `curl … | sh` install snippets found inside skills or READMEs.
- A skill with scripts is executable code. Review `scripts/`, `hooks/`, and any `*.js`/`*.py` before
  enabling it.
- Check the license in the upstream repository, not in a directory listing. `sonarqube` here is
  source-available, not open source.
