# Technology Stack

## 1) Runtime Summary

| Area | Value | Evidence |
|---|---|---|
| Primary language | Python 3; version floor for scripts is [TODO] (CI uses Python 3.12) | `scripts/audit.py`, `.github/workflows/validate-toolbox.yml` |
| Other formats | YAML, JSON, Markdown, Bash | `inventory/*.yaml`, `schemas/*.json`, `scripts/*.sh` |
| Runtime + version | Python 3.12 in CI; local required version [TODO] | `.github/workflows/validate-toolbox.yml` |
| Package manager | No project dependency manifest or lockfile detected; CI installs PyYAML with pip | Scan output; `.github/workflows/validate-toolbox.yml` |
| Module/build system | Standalone Python scripts; generated documentation/catalog artifacts are produced by `scripts/build.py` | `scripts/build.py`, `scripts/audit.py` |

## 2) Production Frameworks and Dependencies

This is a local documentation/inventory utility, not a web application. No production framework is declared.

| Dependency | Version | Role | Evidence |
|---|---|---|---|
| PyYAML | Unpinned in CI | YAML parsing/serialization for audit, profiles, and inventory | `.github/workflows/validate-toolbox.yml`, `scripts/audit.py`, `scripts/profile_engine.py` |
| Python standard library | CI uses Python 3.12 | Filesystem, JSON, TOML, subprocess, hashing, validation | `scripts/audit.py`, `scripts/profile_engine.py` |

## 3) Development Toolchain

| Tool | Purpose | Evidence |
|---|---|---|
| `unittest` | Unit/repository tests | `.github/workflows/validate-toolbox.yml`, `tests/test_audit.py`, `tests/test_profiles.py` |
| `bash -n` | Shell syntax validation | `.github/workflows/validate-toolbox.yml`, `scripts/verify.sh` |
| GitHub Actions | Repository validation on push, PR, and weekly schedule | `.github/workflows/validate-toolbox.yml` |
| Python audit validator | YAML/JSON/schema/link/secret/privacy checks | `scripts/audit.py`, `scripts/verify.sh` |

## 4) Key Commands

```bash
python3 scripts/build.py
python3 scripts/audit.py verify
python -m unittest discover -s tests -v
bash -n scripts/*.sh
./scripts/audit.sh --quick
```

The full local audit and generated reports are distinct from the repository-only verification.

## 5) Environment and Config

- Config sources: `inventory/*.yaml`, `profiles/*.yaml`, `config/*.yaml`, `schemas/*.json`, `.env.example`.
- Environment-variable names listed in `.env.example`: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `CONTEXT7_API_KEY`, `GITHUB_TOKEN`, `OA_WORKSPACE_TOKEN`, `HOSTINGER_API_TOKEN`, `OBSIDIAN_MCP_TOKEN`, `STARRY_TOKEN`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`. Whether each is required by this repository's scripts: [TODO]. Never include actual values.
- Runtime constraints: audit implementation imports PyYAML and `tomllib`; Git, Bash and Python are used by verification. `tomllib` requires Python 3.11+, although CI specifies 3.12. Evidence: `scripts/audit.py`, `.github/workflows/validate-toolbox.yml`.

## 6) Evidence

- `scripts/audit.py`
- `scripts/profile_engine.py`
- `.github/workflows/validate-toolbox.yml`
- `.env.example`
- `README.md`
- Scan output generated for this documentation run (temporary, not retained in `docs/codebase/`).
