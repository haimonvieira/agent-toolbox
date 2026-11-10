# External Integrations

## 1) Integration Inventory

| System | Type | Purpose | Auth model | Criticality | Evidence |
|---|---|---|---|---|---|
| GitHub Actions | CI | Repository validation on push/PR and scheduled checks | GitHub Actions permissions specify `contents: read` | Medium | `.github/workflows/validate-toolbox.yml` |
| GitHub / public registries | External metadata lookup (optional) | Upstream update suggestions and pinned-source checks | Public metadata; no credential handling visible in update routine | Low/medium | `scripts/audit.py`, `scripts/verify_pins.py` |
| Agent harnesses / MCP servers | Config-output targets; no connections made by this repository's default build | Emit sample MCP configuration for OMP, Claude Code, OpenCode | Placeholder values emitted; actual auth supplied outside repo | Medium | `scripts/emit_config.py`, `configs/examples/`, `docs/mcps.md` |
| Git | Local history and repository validation | Churn/history evidence and version control | Local Git configuration | Medium | scan output, `scripts/audit.py`, `.github/workflows/validate-toolbox.yml` |

## 2) Data Stores

| Store | Role | Access layer | Key risk | Evidence |
|---|---|---|---|---|
| JSON files under `data/` | Inputs to generated catalog/documentation | `scripts/build.py` | Generated artifacts can become stale if inputs/build are not synchronized | `scripts/build.py`, `README.md` |
| YAML files under `inventory/`, `profiles/`, `config/`, `local-state/` | Inventories, profiles, policies, and audit snapshots | `scripts/audit.py`, `scripts/profile_engine.py` | Local snapshot contains environment metadata; current state is gitignored | `.gitignore`, `scripts/audit.py` |
| JSON schemas under `schemas/` | Structural validation | `scripts/audit.py` | Custom subset validator does not imply full JSON Schema compliance | `scripts/audit.py`, `schemas/*.json` |
| SQLite/database/cache services | [TODO] No application database integration evidenced | — | — | Scan output, `scripts/audit.py` |

## 3) Secrets and Credentials Handling

- Credential sources: `.env.example` lists variable names only; actual values are explicitly placeholders. Harness credentials are intended to remain in local configuration and are not part of this repository. Evidence: `.env.example`, `.gitignore`, `docs/security.md`.
- Hardcoding checks: repository validator scans tracked text files for common secret patterns and masks matched values in output. Evidence: `scripts/audit.py` (`scan_secrets`, `secret_categories`).
- Rotation/lifecycle: [TODO] no credential rotation mechanism in repository.
- Do not reproduce or store real secret values in docs or generated reports.

## 4) Reliability and Failure Behavior

- Retry/backoff: [TODO] no general retry policy evidenced.
- Timeout policy: subprocess and network metadata lookups use bounded timeouts in `scripts/audit.py`; individual values vary by call.
- Circuit breaker/fallback: local data build does not require upstream access; optional upstream checks report failure as unavailable. Evidence: `scripts/build.py`, `scripts/audit.py` (`write_update_suggestions`).

## 5) Observability for Integrations

- Logs: scripts print status, warning, and failure messages; secret-scanning output masks matched content. Evidence: `scripts/audit.py`, `scripts/emit_config.py`.
- Metrics/tracing: [TODO] no metrics or distributed tracing integration detected.
- Visibility gaps: MCP runtime handshakes, hooks, plugins, and third-party behavior are explicitly not executed/verified for safety. Evidence: `docs/security.md`, `docs/overview.md`.

## 6) Evidence

- `scripts/audit.py`
- `scripts/emit_config.py`
- `.github/workflows/validate-toolbox.yml`
- `.env.example`
- `.gitignore`
- `docs/security.md`
- `configs/examples/`
