# Architecture

## 1) Architectural Style

- Primary style: data-driven documentation/tooling repository with standalone Python scripts; profile logic is a reusable module called by the audit CLI.
- Why: `scripts/build.py` loads JSON inputs to generate catalog/docs; `scripts/audit.py` validates and collects state; `scripts/profile_engine.py` models inventory and profile evaluation.
- Primary constraints: catalog generation is separated from environment collection; profiles are declarative and do not mutate the machine; local audit is designed to sanitize paths/credentials and limit scanning to allowlisted locations. Evidence: `scripts/build.py`, `scripts/gather.py`, `docs/profiles.md`, `scripts/audit.py`.

## 2) System Flow

```text
inventory/data + profiles/config/schemas
          -> Python scripts (build, audit, profile engine, emit_config)
          -> generated docs/catalog/reports or validation output
          -> human review / harness configuration
```

1. `data/*.json` feeds `scripts/build.py`, which composes catalog entries and generated Markdown pages.
2. `inventory/*.yaml`, `profiles/*.yaml`, `schemas/*.json`, and `config/*.yaml` are read by audit/profile validation.
3. `scripts/audit.py` repository verification checks structure, schemas, duplicate IDs, links, syntax, secrets, paths, and profile references.
4. Local collection is performed separately by `scripts/audit.py` and explicitly excludes execution of hooks, plugins, MCP servers, and skill scripts (`docs/security.md`).
5. `scripts/profile_engine.py` resolves inventory references, inheritance, evaluation, comparison, and reproducibility.
6. `scripts/emit_config.py` translates catalog MCP entries into selected agent config formats; default behavior prints output, `--write` writes it.

## 3) Layer/Module Responsibilities

| Layer/module | Owns | Must not own | Evidence |
|---|---|---|---|
| `data/` | Catalog-generation inputs | Runtime local-state collection | `scripts/build.py`, `scripts/gather.py` |
| `inventory/` + `schemas/` | Component records and structural contracts | Installation/execution of components | `inventory/manifest.yaml`, `schemas/inventory.schema.json`, `docs/security.md` |
| `profiles/` + `scripts/profile_engine.py` | Profile expectations and evaluation over inventory/snapshot | Installing or removing components | `docs/profiles.md`, `scripts/profile_engine.py` |
| `scripts/audit.py` | Collection, validation, drift and reporting CLI | Executing discovered third-party tools or exposing credentials | `scripts/audit.py` module safety contract |
| `scripts/build.py` | Deterministic transformation from data inputs to public docs/catalog | Reading live machine state | `scripts/build.py` module description |
| `scripts/emit_config.py` | Format MCP catalog records for harnesses | Secret provisioning; it emits placeholders | `scripts/emit_config.py` |

## 4) Reused Patterns

| Pattern | Where found | Purpose evidenced by code/docs |
|---|---|---|
| Declarative inventory + stable references | `inventory/*.yaml`, `profiles/*.yaml`, `scripts/profile_engine.py` | Profiles refer to inventory IDs instead of duplicating component metadata (`docs/profiles.md`). |
| Read-only audit and drift comparison | `scripts/audit.py` | Compare sanitized current state with baseline and policy, without automatic remediation. |
| Build-from-data generation | `scripts/build.py` | Rebuild catalog and rendered pages from `data/` inputs. |
| Schema validation | `scripts/audit.py`, `schemas/*.json` | Validate inventory and profile shape before reports/CI pass. |

## 5) Known Architectural Risks

- `scripts/gather.py` is a separate legacy/environment-specific collector: its module doc refers to `/var/minis/skills` and `minis-mcp-cli`, while the current README and inventory describe a portable catalog and self-audit. Verify which workflow is currently supported before relying on it. Evidence: `scripts/gather.py`, `README.md`, `scripts/audit.py`.
- No recognized dependency manifest or lockfile was found by the scan, while CI installs unpinned PyYAML. This leaves dependency reproducibility/version compatibility unspecified. Evidence: scan output, `.github/workflows/validate-toolbox.yml`.
- Root README describes a curated catalog and later adds a sanitized machine audit/profile layer; readers may conflate generated public catalog with local-only collection. The README separates these but architecture has two flows. Evidence: `README.md`, `docs/overview.md`, `scripts/audit.py`.

## 6) Evidence

- `scripts/build.py`
- `scripts/gather.py`
- `scripts/audit.py`
- `scripts/profile_engine.py`
- `scripts/emit_config.py`
- `docs/profiles.md`
- `.github/workflows/validate-toolbox.yml`
