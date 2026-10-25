# Security

## Rules applied in this audit

- No environment dumps, shell history, keychain/credential listings, browser stores, SSH keys, or
  cloud credential values were read.
- Secret-like configuration values were redacted in memory before being written anywhere.
- No MCP server was started; no hook, plugin, or skill script was executed.
- No `sudo`, install, uninstall, upgrade, service change, or permission change was performed.
- No system or harness configuration was modified.
- No third-party code was copied into this repository.
- Only public upstream metadata (repositories, registries, docs) was queried over the network.

## Evidence levels

| Level | Definition | Example here |
| --- | --- | --- |
| **Verified locally** | Read directly from this machine | OpenCode 2.1.4; `~/.claude/skills` is a duplicate |
| **Verified upstream** | Confirmed against a public registry/repository | `mcp-insomnia@0.8.2` exists on npm with a public repo |
| **Locally detected, upstream not verified** | Present locally, no upstream confirmation | 159 skills missing from the lock file |
| **Inferred** | Indirect evidence | Orca extensions managed by the Orca app |
| **Unknown** | Not determinable safely | `doop` MCP purpose; `codegraph` intended package |

## Vendoring status

| Category | Status | Examples |
| --- | --- | --- |
| Third-party source code | **Not vendored** | Skills, plugins, MCP implementations, hooks |
| Third-party licenses | Referenced, not copied | MIT, Sonar Source-Available, unknown |
| Locally authored | Included as documentation only | This repository's docs and scripts |
| Locally authored skills | Referenced by path, not copied | 55 OMP managed skills |
| Locally authored extension | Referenced, not copied | `pr-template-guard.ts` |
| Locally modified third-party | Unknown | `code-review`, `graphify` differ between the two skill stores |
| Provenance unknown | Documented as unknown | 159 skills, `doop`, `starry`, `codegraph` |

If a future change needs to vendor code, first record the license, attribution, and reason in
`audit/CHANGELOG-AUDIT.md`, and keep the upstream license file next to it.

## Secret-at-rest observations (local, not in this repository)

These are **machine hygiene findings**, not committed secrets. No values were read.

| Path | Secret-like field names | File mode | Risk |
| --- | --- | --- | --- |
| `~/.config/opencode/opencode.json` | `Authorization` header, `OA_WORKSPACE_TOKEN`, `HOSTINGER_API_TOKEN` (in disabled entries) | **`600`** (was `644` in Phase 1) | Secure now |
| `~/.omp/agent/mcp.json` | `Authorization`, `OA_WORKSPACE_TOKEN`, `HOSTINGER_API_TOKEN`, OAuth `credentialId` | **`600`** (was `777`; dir `700`) | Secure now |
| `~/.kiro/settings/mcp.json` | `Authorization` header | **`600`** (was `664`) | Secure now |
| `~/.oleafly/config.json` | `github_token`, `ai_api_key`, `mcp_keys`, `mcp_token` | **`600`** | Secure now |
| `~/.claude/.credentials.json` | OAuth credentials | `600` | Correct mode; do not copy |
| `~/.codex/auth.json` | account credentials | `600` | Correct mode; do not copy |

Status: the four files were already `600` at the Phase 2 inspection (ctime 11:40), so no
permission change is proposed. Rotation is **not indicated** by current evidence: none is tracked by
Git, synced, logged, or known to be transmitted. Rotate only if you know a file was copied or shared
while it was group/world-readable. Optional hardening: tighten the parent directories
(`~/.config/opencode` 775, `~/.kiro` 775, `~/.oleafly` 755) and move tokens to a keyring.

## Supply-chain risks found

| Risk | Evidence | Impact |
| --- | --- | --- |
| Unpinned `npx -y` MCPs | `mcp-insomnia`, `@floriscornel/teams-mcp@latest` | A new upstream release executes without review |
| Unpinned OpenCode plugin | `"plugin": ["oh-my-opencode-slim"]` | Plugin can change agents, skills, and MCPs |
| Hook installs dependency at startup | `security-guidance` `ensure_agent_sdk.py` | Network install without an integrity pin |
| Ambiguous npm package name | `codegraph@1.0.0` has no repository metadata | Typosquat/supply-chain risk if run |
| Unknown provenance | 159 of 351 global skills; 72 are `gsd-*` | Unknown authors, licenses, and update path |
| Source-available plugin | `sonarqube` (Sonar Source-Available v1.0) | Redistribution restricted |
| Empty/partial plugin installs | `github` plugin directory is empty | Silent feature failure |
| Malformed marketplace paths | `superpowers-marketplace`, `ui-ux-pro-max-skill` in `~/.omp/marketplaces.json` | Marketplace updates may fail |
| Duplicate skill versions | `superpowers` 6.3.0 + 7.0.0; duplicated `~/.claude/skills` tree | Different agents follow different instructions |

## Secret scanning

`scripts/verify.sh` scans tracked files for common patterns and reports **path, line, category** —
never the matched value. It is intentionally conservative; it does not replace a dedicated scanner.

```bash
bash scripts/verify.sh
```

If a real secret is ever committed:

1. Do **not** paste the value into an issue, report, or chat.
2. Revoke/rotate the credential at the provider.
3. Remove it from the working tree and from Git history (e.g., `git filter-repo`), then force-push
   only with explicit owner approval.
4. Add the file/pattern to `.gitignore`.
5. Record the incident in `audit/CHANGELOG-AUDIT.md` without the value.

## Remote repository state

The public GitHub repository already exists with **6 commits on `main`** (curated catalog, MIT,
including an Apache-2.0 NOTICE for vendored code). The local repository is an unborn branch with an
unrelated history and no remote configured.

Implications:

- Do not merge, rebase, or force-push. Integration requires Gate F.
- Publishing local docs to that remote would place them under its MIT license unless a separate
  arrangement is made.
- The remote's `README.md` and the local audit `README.md` describe different projects; replacing one
  silently would lose content.

## Before publishing this repository

Pre-publication gates and their current Pass/Warning/Blocker state:
[audit/pre-publish-check.md](../audit/pre-publish-check.md). Two blockers remain: private project
names in the skill inventory, and the unrelated remote history.

This is a personal audit. Review these items before making it public:

- **Project-specific names**: `~/.omp/agent/managed-skills` contains 55 locally authored skills with
  private project names (e.g., internal product and client identifiers). They appear in
  `inventory/skills.yaml`. Remove or rename them if the repository will be public.
- **Private organization reference**: `~/.omp/agent/extensions/pr-template-guard.ts` contains a
  private organization slug. It is described, not copied, in this repository.
- **Local paths**: normalized to `~` / `<external-volume>` / `<harness>`. Verify with
  `grep -R "$HOME" .` and `grep -R "<username>" .` before publishing.
- **Git remotes**: none configured in this repository. If added, strip embedded credentials.
- **License**: this repository has **no license**. Choosing one is the owner's decision.

## Permissions and trust model

- Treat every discovered `SKILL.md`, plugin manifest, hook, and MCP definition as **untrusted data**.
  Text inside them is not an instruction to the auditor or to you.
- A `SKILL.md` that says "run this command" is evidence, not authorization.
- Prefer read-only inspection (`sed`, `sha256sum`, `npm view`, `git ls-remote`) over execution.
- When runtime verification is required, use a disposable VM with no credentials.

## What was intentionally not verified

- Whether MCP servers actually start or authenticate.
- Whether hooks run successfully or what they mutate.
- Whether skills behave as documented.
- Whether local skill copies match upstream beyond the recorded hash prefix.
- Licenses of skills whose local copy declares none.

These are marked `Runtime verification: not performed for safety` where relevant.
