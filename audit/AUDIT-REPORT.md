# Audit report — AI-agent tooling

- **Date:** 2026-10-25 (America/Sao_Paulo)
- **Scope:** harnesses, skills, MCP servers, plugins, hooks, package provenance on one Linux host
- **Method:** read-only static inspection; no MCP/hook/plugin/skill execution
- **Snapshot:** see [environment-snapshot.md](environment-snapshot.md)
- **Evidence levels:** see [docs/security.md](../docs/security.md#evidence-levels)

> Runtime verification of third-party components: **not performed for safety**.

> **Phase 2 update (2026-10-25):** the four credential configs reviewed in C1 are now mode `600`
> (they were `644`/`777`/`664` in Phase 1). No rotation is indicated by current evidence. H1 entries
> are classified in `docs/mcps.md` (two repairable, one stale path, two unknown upstream). Remote
> integration is blocked by unrelated history — see `audit/pre-publish-check.md`.

> **Evidence basis:** unless a finding says otherwise, the evidence level is **Verified locally**
> (static file inspection). Package/repository checks are **Verified upstream**. Conclusions drawn
> from indirect signals are marked **Inferred**; undeterminable items are **Unknown**. Runtime
> behaviour of MCPs, hooks, plugins, and scripts is **not verified**.

## Summary

| Severity | Count | Headline |
| --- | ---: | --- |
| Critical | 2 | Plaintext credentials in world-readable config; unpinned startup dependency install |
| High | 7 | Broken MCPs, broken skill symlink, ambiguous package, unknown-provenance executable skills |
| Medium | 11 | Duplicates, orphaned configs, stale caches, license/provenance gaps |
| Low | 6 | Naming, backups, clutter, stale aliases |

The environment is functional but **not reproducible as-is**: 159 of 351 global skills at snapshot (161 of 352 at final check) have no
recorded origin, five MCP entries cannot start, and three harness configs outlive their executables.

---

## Critical

### C1 — Plaintext credentials in world-readable configuration

- **Evidence:** static inspection found secret-like fields in:
  - `~/.config/opencode/opencode.json` (mode `644`): `Authorization` header for a local MCP and
    `OA_WORKSPACE_TOKEN` / `HOSTINGER_API_TOKEN` in (some disabled) entries.
  - `~/.omp/agent/mcp.json` (mode `777`, parent `700`): `Authorization`, `OA_WORKSPACE_TOKEN`,
    `HOSTINGER_API_TOKEN`, OAuth `credentialId`.
  - `~/.kiro/settings/mcp.json` (mode `664`): `Authorization` header.
  - `~/.oleafly/config.json`: `github_token`, `ai_api_key`, `ai_keys`, `mcp_token` in plaintext.
- **Impact:** any local process/user that can read these files obtains usable credentials. The
  OpenCode file is readable by every local user (`644`).
- **Recommended action:** move secrets to harness credential stores or the OS keyring; set `600`;
  rotate tokens that were world-readable. **Requires machine changes — not applied.**
- **Repository exposure:** none. No value was copied into this repository.

### C2 — Automatic dependency installation at agent startup

- **Evidence:** `security-guidance` 2.0.15 SessionStart hook runs `ensure_agent_sdk.py`, which
  creates `~/.claude/security/agent-sdk-venv` and `pip install`s `claude_agent_sdk` when missing.
- **Activation:** the plugin is installed in OMP; `installed_plugins.json` has no enabled flag, so activation is **inferred** from installation and hook manifests.
- **Impact:** network access and code installation on first session start, without a pinned
  version or integrity check. A compromised package or index affects every session.
- **Recommended action:** pre-provision the SDK at a pinned version, or disable the plugin if the
  feature is not needed. **Requires machine change — not applied.**

---

## High

### H1 — Five MCP servers cannot start

- **Evidence / paths:**
  - `codegraph` — no executable; npm `codegraph@1.0.0` has no repository metadata.
  - `codebase-memory` — no `codebase-memory-mcp` executable.
  - `openagents` — no `agn` executable.
  - `hostinger-api` — no `hostinger-api-mcp` executable.
  - `gemini-notebook-mcp` — `C:\Users\…\notebooklm-mcp.EXE` on Linux.
- **Impact:** failed MCP startups, noisy sessions, tools missing when expected.
- **Recommended action:** install the verified packages at pinned versions, fix the Windows path to
  `~/.local/bin/notebooklm-mcp`, and remove `codegraph` until its upstream is identified.
  **Requires machine change.**

### H2 — Ambiguous npm package name (`codegraph`)

- **Evidence:** config runs `codegraph serve --mcp`; npm `codegraph@1.0.0` has no repository URL and
  no local executable.
- **Impact:** installing "the package with that name" is a typosquat/supply-chain risk.
- **Recommended action:** do not install until the intended project is confirmed from upstream.
  **Requires machine change if installed.**

### H3 — Global skill symlink depends on an external volume

- **Evidence:** `~/.agents/skills/coordenacao-commit-seguro` → `<external-volume>/…/team-lead/.agents/skills/coordenacao-commit-seguro`.
  At snapshot time the target was absent (`test -e` failed); the volume was mounted later in the
  audit and the link resolved (19 project-local skills are now reachable there).
- **Impact:** the skill disappears whenever the volume is unmounted; harnesses may log errors or
  silently skip it. It is the only global skill backed by removable storage.
- **Recommended action:** keep the volume mounted, or copy the skill into a local directory and
  replace the symlink. **Requires machine change if you want it decoupled.**

### H4 — 159 skills (snapshot) with unknown provenance, 62 with executable scripts

- **Evidence:** 351 entries in `~/.agents/skills`; 192 are in `~/.agents/.skill-lock.json`; 159 are
  not. 62 skills contain `.sh`/`.py`/`.js`/`.ts` files. Clusters: 72 `gsd-*`, 12 `gitnexus-*`,
  12 `penpot-*`, 9 `pm-*`, 7 `maestri-*`.
- **Impact:** unknown author, license, update path, and code behaviour for a large part of the
  instruction surface. Agents may follow unreviewed instructions.
- **Recommended action:** triage by cluster; record source/license for keepers, delete the rest.
  **Requires machine change to remove.**

### H5 — Unpinned execution paths

- **Evidence:** `npx -y mcp-insomnia`, `@floriscornel/teams-mcp@latest`, OpenCode plugin
  `"oh-my-opencode-slim"` (no version), branch-tracking skill installs.
- **Impact:** silent upstream changes execute with agent privileges.
- **Recommended action:** pin exact versions/commits; update deliberately. **Requires machine
  change for the configs.**

### H6 — Duplicate skill trees with conflicting content

- **Evidence:** `~/.agents/skills` and `~/.claude/skills` are 269 MB each; 345 identical SKILL.md
  hashes, `code-review` and `graphify` differ. `superpowers` exists standalone and in plugin
  7.0.0 and stale 6.3.0. `code-review`/`autofix` duplicate the CodeRabbit plugin.
- **Impact:** two agents can follow different instructions for the same task; double disk use.
- **Recommended action:** choose one canonical store, symlink the other, and remove stale plugin
  versions. **Requires machine change.**

### H7 — Orphaned harness configurations holding credentials

- **Evidence:** Kiro (`~/.kiro`, bearer header), Gemini/Antigravity (`~/.gemini`), Copilot CLI
  (`~/.copilot`, `auth.db`) have config but no executable or app package.
- **Impact:** stale credentials and MCP entries; unclear which agent is still in use.
- **Recommended action:** confirm the apps are retired, then archive/remove their config and rotate
  credentials. **Requires machine change.**

---

## Medium

### M1 — Malformed OMP marketplace catalog paths

`~/.omp/marketplaces.json` points `superpowers-marketplace` and `ui-ux-pro-max-skill` at
`/home/<user>/C:\Users\...`, which does not match the real cache dir. Marketplace updates for those
two may fail. Fix the JSON paths after confirming the intended location.

### M2 — Stale plugin caches

`superpowers` 6.3.0 and `security-guidance` 2.0.7 remain after upgrades. Inert but confusing; remove
after confirming the current versions work.

### M3 — Empty/partial plugin installs

`github@claude-plugins-official` has an empty install directory. `context7@…` contains only a
README. Reinstall or remove; do not assume the tools exist.

### M4 — `aas-core` version conflict

OpenCode pins 19.15.0 (disabled); OMP pins 18.10.0 (enabled). Different catalogs and IDs. Align them.

### M5 — Codex trusted hashes for an external-volume project

`~/.codex/config.toml` trusts hooks from an external volume. While it was unmounted the hooks were
inoperative and unverifiable. After mounting, they run a local `state_freshness.py` (3 s timeout,
fail-open) on prompt, stop, and session end. Keep the volume mounted, or remove the
`[hooks.state."…"]` entries if the project is retired — but review the script first.

### M6 — Skill lock drift

3 lock entries have no local directory (`planning-with-files`, `playwright-skill`, `ui-ux-pro-max`);
159 local skills have no lock entry. The lock no longer describes the installed set.

### M7 — Unverified remote MCP provenance

`graphify` (`api.graphify.com`), `doop` (`doop.design`), and `starry` (`127.0.0.1:7600`) have no
verifiable upstream repository or purpose from local metadata. Treat as untrusted third parties.

### M8 — Windows path in OMP MCP config

`gemini-notebook-mcp` points to a Windows `.EXE`; a working Linux binary exists. Fix the path.

### M9 — Project-specific names in a potentially public repository

55 locally authored OMP skills include private project/client identifiers, and `pr-template-guard.ts`
references a private organization. They are documented by name in `inventory/skills.yaml`. Decide
whether to sanitize before publishing.

### M10 — Repository license not specified

The repository has no `LICENSE`. Choosing one is the owner's decision; none was added.

### M11 — Configuration changed during the audit

At 11:07 an OpenCode plugin, LSP config, `AGENTS.md`, and plugin config were added by another
process; `context7`, `gh_grep`, `omgskills`, and a `memory` tool appeared later. Counts in this
report refer to the 10:55 snapshot plus documented drift. Re-run `scripts/audit.sh` before acting on
a specific version.

---

## Low

### L1 — Duplicate VS Code extension version

`openai.chatgpt` 26.1007 and 26.1021 are both installed.

### L2 — Zip files and nested bundle in the skill store

`algorithmic-art.zip`, `skills.zip`, and `~/.agents/skills/synced/<uuid>/` (15 nested skills) are not
loadable top-level skills.

### L3 — Ten directories without a top-level SKILL.md

`pm-*` plugin bundles and `synced/` contain nested skills; they are not directly discoverable.

### L4 — Orphaned statusline script

`~/.claude/ponytail-statusline.sh` exists but no `statusLine` reference was found in
`~/.claude/settings.json`.

### L5 — Stale auth cache for absent plugins

`~/.claude/mcp-needs-auth-cache.json` lists 13 `plugin:*` entries for plugins that are not installed.

### L6 — Naming and alias clutter

`opencode2` alias, `opencode.exe` and `claude.exe` copies on Linux `PATH`, `.bak` config files, and a
literal `C:\Users\...` directory in the home directory.

---

## Things that are fine

- No secrets are committed to this repository.
- No third-party source code is vendored here.
- `codex/config.toml` and Claude credential files use restrictive modes (`600`).
- All 31 upstream skill repositories referenced by the lock returned HTTP 200.
- `ponytail`, `superpowers`, `coderabbit`, `best-of`, and `oh-my-opencode-slim` ship MIT licenses.
- No active Git hooks in the inspected repository; `core.hooksPath` is unset.
- The repository's own scripts never start MCPs, execute hooks, or print secrets.

## Recommended sequence

1. Rotate/relocate credentials from C1 and restrict file modes.
2. Decide on `security-guidance` (C2) before the next session.
3. Repair or remove the five broken MCP entries (H1) and never install `codegraph` blind (H2).
4. Fix the broken skill symlink (H3) and triage unknown skills by cluster (H4).
5. Pin every `@latest`/unversioned entry (H5).
6. Consolidate duplicate skill stores and stale plugin caches (H6, M2).
7. Decide the fate of Kiro/Gemini/Copilot configs (H7).
8. Only then publish — after sanitizing project-specific names (M9) and choosing a license (M10).
