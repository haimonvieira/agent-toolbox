# Codebase Structure

## 1) Top-Level Map

| Path | Purpose | Evidence |
|---|---|---|
| `README.md`, `catalog.json` | Human-facing overview and generated machine-readable catalog | `README.md`, `scripts/build.py` |
| `data/` | Inputs used to build the public catalog and recommendation pages | `scripts/build.py`, `data/*.json` |
| `inventory/` | Sanitized component inventories and repository manifest | `inventory/manifest.yaml`, `inventory/*.yaml` |
| `profiles/` | Declarative environment profiles and generated profile data | `profiles/*.yaml`, `scripts/profile_engine.py` |
| `docs/`, `audit/`, `recommended/`, `mcps/` | User documentation, audit reports, recommendations, MCP notes | `README.md`, these directories |
| `scripts/` | Collection, generation, configuration-emission, auditing, and verification tools | `scripts/*.py`, `scripts/*.sh` |
| `schemas/`, `config/`, `configs/examples/` | Validation schemas, policy/backlog settings, sanitized examples | `scripts/audit.py`, `schemas/*.json`, `config/*.yaml` |
| `tests/` | Python unit tests for audit and profiles | `tests/test_audit.py`, `tests/test_profiles.py` |
| `skills/` | Generated skill catalog pages | `scripts/build.py`, `README.md` |
| `.github/workflows/` | CI validation workflow | `.github/workflows/validate-toolbox.yml` |
| `mine/` | Locally authored skill content and supporting assets | `mine/incident-response/SKILL.md`, `mine/skill-creator/SKILL.md` |

## 2) Entry Points

- Main runtime entry: no single application entry point is declared; executable workflows are scripts.
- Repository-only validation: `scripts/verify.sh` delegates to `scripts/audit.py verify`.
- Local environment audit: `scripts/audit.sh` delegates to `scripts/audit.py`; options include quick/full modes and profile commands.
- Catalog generation: `scripts/build.py` reads `data/*.json` and writes README/catalog and generated pages.
- MCP config emission: `scripts/emit_config.py` reads catalog data and emits or writes target-harness configuration.
- CI entry: `.github/workflows/validate-toolbox.yml`.

## 3) Module Boundaries

| Boundary | What belongs here | Not established by evidence |
|---|---|---|
| `data/` | Source inputs for generated public catalog | [TODO] Whether every file is generated or partly hand-maintained |
| `inventory/` and `profiles/` | Sanitized observed inventory and declarative environment expectations | They do not install components; `docs/profiles.md` states profiles are declarative |
| `scripts/` | Transform, collect, validate, and report logic | [TODO] Formal package/API stability guarantees |
| `docs/`, `audit/`, generated pages | Human-facing guides and reports | Whether all docs are generated; verify per generator before editing |
| `tests/` | Unit tests for audit and profile behavior | [TODO] Additional untracked/ignored test conventions |

## 4) Naming and Organization Rules

- File naming: mostly lowercase kebab-case for docs and test names (`test_audit.py`); Python scripts use snake_case (`profile_engine.py`); evidence: `docs/*.md`, `scripts/*.py`, `tests/*.py`.
- Directory organization: top-level domain directories for inventory, profiles, schemas, docs, and tooling; not a Python `src/` package.
- Import aliasing/path conventions: scripts add their directory to `sys.path` for sibling module imports; no project alias configuration detected. Evidence: `scripts/audit.py`, `tests/test_audit.py`.

## 5) Evidence

- `README.md`
- `docs/overview.md`
- `docs/installation.md`
- `scripts/audit.py`
- `scripts/build.py`
- `.github/workflows/validate-toolbox.yml`
- Scan directory tree
