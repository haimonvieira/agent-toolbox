# Codebase Concerns

## 1) Top Risks (Prioritized)

| Severity | Concern | Evidence | Impact | Suggested action |
|---|---|---|---|---|
| Medium | No dependency manifest/lockfile detected; CI installs unpinned PyYAML | Scan output; `.github/workflows/validate-toolbox.yml` | Builds may see differing dependency versions | Pin PyYAML and document the supported Python baseline if reproducibility is required |
| Medium | Legacy `scripts/gather.py` references `/var/minis/skills` and `minis-mcp-cli` | `scripts/gather.py` | This workflow may not operate in the portable repository workflow without environment-specific tooling | Clarify supported/retired status and align docs or script accordingly |
| Low | `scripts/audit.py` is a large multi-purpose module (over 1,800 lines) | `scripts/audit.py` | Audit collection, validation, profile commands and report generation are coupled in one module | Consider boundaries only if changes make maintenance difficult |

## 2) Technical Debt

| Debt item | Why it exists | Where | Risk if ignored | Suggested fix |
|---|---|---|---|---|
| Conflicting/legacy collector assumptions | Separate collector still documents Minis-specific paths and CLI | `scripts/gather.py`, `README.md` | Users may invoke a workflow unsupported by the current portable catalog | Verify intent with maintainer; update/remove only after decision |
| Dependency versions are not locked for validation | CI installs latest PyYAML; no package manifest/lockfile was found | `.github/workflows/validate-toolbox.yml`, scan output | Non-reproducible CI dependency resolution | Pin the CI dependency or introduce a minimal reproducible validation setup |
| Generated documentation behavior needs per-file awareness | `scripts/build.py` regenerates README/catalog/pages; other docs are hand-authored | `scripts/build.py`, `README.md` | Manual changes to generated files may be overwritten | Confirm source-of-truth file before modifying generated output |

## 3) Security Concerns

| Risk | OWASP category | Evidence | Current mitigation | Gap |
|---|---|---|---|---|
| Placeholder env template names include secret variables | N/A | `.env.example`, `.gitignore` | Values are placeholders and `.env` is ignored; verifier scans common patterns | Pattern scanning is not a complete secret scanner (`docs/security.md`) |
| Inventory/audit handles sensitive environment metadata | N/A | `scripts/audit.py`, `docs/security.md` | Values are not emitted; paths normalized; managed skill names redacted | Private-term scan depends on a local-only file unavailable in CI |
| Optional upstream metadata requests are external network calls | N/A | `scripts/audit.py` | Explicit opt-in `--check-upstreams`; bounded timeouts | Upstream content/version is not independently signed or pinned |

## 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---|---|---|---|---|
| Repository scans traverse text files and inventory/profile data | `scripts/audit.py` (`iter_text_files`, `scan_secrets`, validators) | [TODO] No measured slow performance documented | Large repositories may increase verification time | Measure before optimizing; maintain existing exclusions/size limits |
| Full skill hashing reads file contents; quick mode uses metadata | `scripts/audit.py` (`fingerprint_skill`) | Full collection can do more I/O | Large skill trees can lengthen full audit | Use quick mode where content hashing is unnecessary; no speedup claim made |

## 5) Fragile/High-Churn Areas

Based on `git log --since='90 days ago'` scan; counts are file appearances in commits, not measured defect rates.

| Area | Why fragile | Churn signal | Safe change strategy |
|---|---|---|---|
| `README.md` | Main generated/user-facing project overview | 9 commits | Confirm which sections are generated before editing; run `scripts/build.py` where appropriate |
| `catalog.json` | Generated public catalog consumed by config emitter | 6 commits | Edit source data then regenerate; verify with repository checks |
| `audit/pre-publish-check.md` | Audit gate/report history | 6 commits | Preserve dated status and confirm current evidence before changing conclusions |
| `scripts/build.py`, `scripts/audit.py`, `inventory/manifest.yaml` | Core generator, validator, and project metadata | 5, 4, and 5 commits respectively | Use targeted tests/verification and keep generated outputs synchronized |

## 6) `[ASK USER]` Questions

1. [ASK USER] Is `scripts/gather.py` still a supported workflow, or should it be treated as legacy after the portable inventory/self-audit flow was introduced?
2. [ASK USER] Should CI dependency versions be pinned in a dedicated requirements file or directly in the workflow?

## 7) Evidence

- Scan output: no recognized package manifest; TODO/churn sections and tree
- `scripts/gather.py`
- `scripts/audit.py`
- `scripts/build.py`
- `.github/workflows/validate-toolbox.yml`
- `.env.example`
- `.gitignore`
- `docs/security.md`
- `git log --since='90 days ago'`
