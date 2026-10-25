# Changelog — audit

## 2026-10-25 — initial audit and repository creation

### Context

- No `agent-toolbox` repository existed on this machine. A new repository was initialized at
  `~/agent-toolbox` on branch `docs/toolbox-audit`.
- No commit, tag, push, or remote configuration was performed.
- No system, harness, MCP, plugin, skill, or hook configuration was modified.

### Added

- `README.md` — purpose, structure, quick start, audit status, disclaimer.
- `docs/` — overview, harnesses, skills, MCPs, plugins, hooks, installation, updating, security,
  troubleshooting, recommended resources.
- `inventory/` — `manifest.yaml`, `harnesses.yaml`, `skills.yaml` (463 entries), `mcps.yaml`,
  `plugins.yaml`, `hooks.yaml`.
- `configs/examples/` — sanitized per-harness MCP/config examples.
- `scripts/` — `audit.sh` (read-only inventory), `verify.sh` (YAML/JSON/TOML + secret patterns),
  `check-links.sh`.
- `skills/README.md`, `mcps/README.md`, `plugins/README.md` — category entry points.
- `audit/AUDIT-REPORT.md`, `audit/environment-snapshot.md`, this changelog.
- `.env.example` — environment variable names with placeholders only.
- `.gitignore` — local secrets, sessions, caches, build output.

### Changed

- Nothing outside the repository.
- Inside the repository: nothing pre-existing (new repository).

### Not changed (intentionally)

- `~/.config/opencode/*`, `~/.claude/*`, `~/.codex/*`, `~/.omp/*`, `~/.agents/*`, `~/.kiro/*`,
  `~/.gemini/*`, `~/.copilot/*`, `~/.config/zed/*`.
- Shell startup files, Git global config, package installations, services.
- No credentials were rotated.

### Security notes

- Secret-like values were redacted in memory; only variable/field names were written.
- No third-party source code was copied.
- No hook, plugin, MCP, or skill script was executed.
- `scripts/verify.sh` found no secret patterns in the repository at creation time.

### Drift observed during the audit

- 11:07: OpenCode plugin `oh-my-opencode-slim` added by another process; `context7` and `gh_grep`
  MCPs and 12 skills appeared.
- Later: `omgskills` MCP and a `memory` tool appeared.
- Recorded in `audit/environment-snapshot.md`; not attributed to this audit.

### Next audit

Re-run `bash scripts/audit.sh`, regenerate `inventory/skills.yaml`, and update the affected
documents. See `docs/updating.md`.

### Corrections made during Pass B

- The external volume referenced by one global skill symlink was mounted mid-audit. The finding was
  corrected from "broken symlink" to "volume-dependent symlink", and the Codex project hooks became
  inspectable.
- Codex was initially described as having no skills. A hidden `.system` directory was found later:
  5 built-in skills are now inventoried.
- Plugin counts were normalized to 17 entries (13 bundles + 4 OMP extension files).
- A later drift added `omgskills` and a `memory` tool; `omgskills` was added to the MCP inventory.

### Verification performed

| Check | Command | Result |
| --- | --- | --- |
| YAML validity | `bash scripts/verify.sh` | all 6 inventories parse |
| JSON examples | `bash scripts/verify.sh` | all 5 parse |
| TOML example | `bash scripts/verify.sh` | parses |
| Internal Markdown links | Python link check | 0 broken |
| External links | `bash scripts/check-links.sh` | 41 checked, 0 failed |
| Secret patterns | `bash scripts/verify.sh` + manual regex | none found |
| Absolute home paths | `bash scripts/verify.sh` | none |
| Read-only audit script | `bash scripts/audit.sh` | runs without side effects |
| Git hooks executed | — | none |
| MCP/hook/plugin/script execution | — | none |

## 2026-10-25 — Phase 2: remediation planning

### Added

- `audit/phase2-start.md` — baseline, remote divergence, scope.
- `audit/skill-dedup-plan.md` — duplicate classification and migration design.
- `audit/unknown-skills-triage.md` — 5 requested clusters + 54 other unknown entries.
- `audit/pre-publish-check.md` — Pass/Warning/Blocker gates.
- `audit/orphaned-configs.md` — Kiro, Gemini/Antigravity, Copilot CLI.
- `audit/nvme-dependencies.md` — external-volume dependencies.
- `audit/approval-gates.md` — Gates A–F with exact proposals.
- `docs/architecture.md` — ownership/injection graph + canonical-store evidence.

### Updated

- `inventory/*.yaml` — Phase 2 fields (`source_type`, `provided_by`, `injected_by`, `managed_by`,
  `directly_configured`, `generated`, `dynamic`), repair classes, pinning, cluster provenance,
  version-conflict notes, counts.
- `docs/skills.md` — canonical-store compatibility matrix, Phase 2 counts, dedup summary.
- `docs/mcps.md` — broken-entry classification, pinning table.
- `docs/plugins.md` — security-guidance detail, version conflicts.
- `docs/hooks.md` — exact security-guidance install command and kill switches.
- `docs/security.md` — resolved permissions, remote/licensing state.
- `docs/harnesses.md` — Copilot shim correction, canonical-store link.
- `docs/installation.md`, `docs/updating.md` — pinned forms and SDK pre-provision.
- `README.md` — Phase 2 section, remote status, audit status.

### Not changed

- No skill, plugin, hook, MCP, harness, or credential file was modified.
- No remote was added; no fetch/merge/rebase/push.
- No package installed or removed.
- No token rotated.

### Verification

- YAML/JSON/TOML: pass.
- Internal links: pass.
- External links: 46 checked, 0 failed.
- Secret patterns: none.
- Absolute home paths: none.

## 2026-10-25 — Phase 3 execution

- Recorded Gate C1 as **Completed / Mitigated**: `claude-agent-sdk==0.2.174` pre-installed; healthy
  venv returns `NOOP_VENV`; unpinned failure path remains.

### Phase 3 cleanup

- Moved `superpowers` 6.3.0, `security-guidance` 2.0.7, and the older VS Code ChatGPT extension to
  `~/.agent-toolbox-backups/20261025-phase3/stale-caches/` (private, not committed).
- Active `superpowers` 7.0.0 and `security-guidance` 2.0.15 remain.

### Phase 3 publication

- Commit `06504dd` on `docs/toolbox-audit`, based on `origin/main` (`d40efaed`).
- Pushed without force; PR #1 opened against `main`.
- `main` and the curated catalog were not modified.
