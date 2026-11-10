# Coding Conventions

## 1) Naming Rules

| Item | Rule | Example | Evidence |
|---|---|---|---|
| Files | Python modules snake_case; Markdown docs mostly kebab-case; tests `test_*.py` | `profile_engine.py`, `pre-publish-check.md`, `test_profiles.py` | `scripts/`, `docs/`, `tests/` |
| Functions/methods | Python snake_case | `validate_profiles_repo`, `collect_state` | `scripts/audit.py` |
| Types/classes | PascalCase | `Catalog`, `PathNormalizationTests` | `scripts/profile_engine.py`, `tests/test_audit.py` |
| Constants/env vars | Python constants uppercase; env vars uppercase with underscores | `ROOT`, `OPENAI_API_KEY` | `scripts/audit.py`, `.env.example` |

## 2) Formatting and Linting

- Formatter: [TODO] no formatter configuration found in root scan.
- Linter: [TODO] no lint configuration found in root scan.
- Relevant enforced checks: YAML/JSON/TOML parsing, schema and inventory validation, internal Markdown links, secret/path privacy scans, shell syntax, unit tests. Evidence: `scripts/audit.py`, `.github/workflows/validate-toolbox.yml`.
- Run commands: `./scripts/verify.sh`; `python -m unittest discover -s tests -v`; `bash -n scripts/*.sh`.

## 3) Import and Module Conventions

- Import grouping/order: [TODO] no configured import sorter; standard-library imports appear before optional third-party imports in `scripts/audit.py`.
- Alias vs relative imports: scripts use `sys.path.insert` to import sibling modules; tests similarly add `scripts/` to `sys.path`. Evidence: `scripts/audit.py`, `tests/test_audit.py`.
- Public exports/barrels: [TODO] standalone scripts/modules; no barrel pattern found.

## 4) Error and Logging Conventions

- Error strategy: validation functions return error/warning lists; CLI prints `FAIL`/`WARN` and returns nonzero status. Evidence: `scripts/audit.py` (`verify_repository`, `cmd_verify`).
- Logging: primarily stdout/stderr status messages with `print`; no logging framework identified. Evidence: `scripts/audit.py`, `scripts/emit_config.py`.
- Sensitive data: audit masks detected secret values, reports categories and paths, and avoids printing environment values. Evidence: `scripts/audit.py`, `docs/security.md`.

## 5) Testing Conventions

- Test file naming/location: `tests/test_*.py`, using `unittest.TestCase`. Evidence: `tests/test_audit.py`, `tests/test_profiles.py`.
- Mocking/isolation: tests use temporary directories and replace selected module functions; no shared fixture framework identified. Evidence: `tests/test_audit.py`.
- Coverage expectation: [TODO] no coverage tool or threshold found.

## 6) Evidence

- `scripts/audit.py`
- `scripts/profile_engine.py`
- `scripts/emit_config.py`
- `tests/test_audit.py`
- `tests/test_profiles.py`
- `.github/workflows/validate-toolbox.yml`
