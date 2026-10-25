# Environment profiles

A **profile** describes one working AI-agent environment: which harnesses, plugins, skills, MCP
servers, hooks and versions belong together, and how reproducible that set is.

## What a profile is — and what it is not

| Profile is | Profile is not |
| --- | --- |
| A declarative expectation set | An installer or a script that changes your machine |
| A reference to inventory entries by stable id | A second copy of the inventory metadata |
| A way to compare two environments | A promise that the environment matches today |
| A reproducibility statement with reasons | A claim of full reproducibility without evidence |

Loading a profile installs nothing, removes nothing, starts no server and executes no hook.
Profiles are compared against the local snapshot by the read-only audit.

## How profiles differ from the inventory

| | `inventory/*.yaml` | `profiles/*.yaml` |
| --- | --- | --- |
| Scope | every component found on the machine | one coherent environment |
| Content | source, license, install method, paths, hashes | references to inventory ids plus expectations |
| Ownership | per component | who owns the component in this profile |
| Versioning | component versions | `profile_version` on top |

The inventory stays the only source of truth. A profile never repeats a source URL, license,
install command or config path unless it needs an explicit override.

## Stable references

Component ids are derived from the inventory, deterministically:

```text
<category>-<slug(name)>        harness-opencode, mcp-pencil, plugin-ponytail
```

Skill names that exist in more than one place get a deterministic suffix:

```text
skill-code-review              the canonical store copy
skill-code-review-plugin       the CodeRabbit plugin copy
skill-skill-creator-built-in   the Codex built-in copy
```

`ownership` values: `directly_configured`, `inherited`, `plugin_injected`, `plugin_managed`,
`built_in`, `canonical_shared`, `project_local`, `optional`, `unresolved`.

## Inheritance

`base.yaml` holds only what every profile shares: runtime prerequisites and the canonical skill
store. Harness-specific items never live in the base. Inheritance depth is capped at 2 and cycles
are rejected by the validator.

## Profiles in this repository

| Profile | Purpose | Status | Version | Reproducibility |
| --- | --- | --- | ---: | --- |
| [`base`](profiles/base.md) | shared runtime and skill-store expectations | active | 1 | fully reproducible |
| [`opencode-go`](profiles/opencode-go.md) | OpenCode with the `opencode-go` preset and its plugins | active | 1 | mostly reproducible |
| [`omp`](profiles/omp.md) | OMP with marketplace plugins, extensions and managed skills | active | 1 | mostly reproducible |
| [`codex`](profiles/codex.md) | Codex CLI with built-in skills and project hooks | active | 1 | mostly reproducible |
| [`claude-code`](profiles/claude-code.md) | Claude Code with the symlinked skill store | active | 1 | mostly reproducible |
| [`minimal`](profiles/minimal.md) | smallest useful setup: one harness, canonical skills, no integrations | active | 1 | mostly reproducible |
| [`full`](profiles/full.md) | every component with a verified upstream | active | 1 | partially reproducible |

## Commands

```bash
./scripts/audit.sh --list-profiles                 # list profiles and their reproducibility
./scripts/audit.sh --profile opencode-go           # validate one profile against this machine
./scripts/audit.sh --compare-profiles opencode-go omp   # show the meaningful deltas
./scripts/audit.sh --who-uses graphify              # which profiles own a component
./scripts/audit.sh --profiles-report                # regenerate profile docs and reports
```

Profile validation prints `PRESENT`, `MISSING`, `VERSION_MISMATCH`, `OPTIONAL_MISSING`,
`DYNAMIC_PRESENT`, `DYNAMIC_MISSING` and `UNKNOWN`, and exits `2` when a **required** component is
missing or has the wrong version. Nothing is installed to fix it.

## Reproducibility scoring

| Status | Meaning |
| --- | --- |
| `fully_reproducible` | every required component has an upstream reference and a documented install path, with no unresolved or floating pieces |
| `mostly_reproducible` | only minor gaps: upstream not independently verified, plugin-manager resolved versions, floating versions |
| `partially_reproducible` | at least one required component lacks provenance, or the profile deliberately excludes unresolved components |
| `blocked` | a required component has no upstream reference, or its executable is missing |

Reasons are always listed in `audit/profile-reproducibility.md`.

## Profile drift

Profile drift is reported next to global drift in `audit/drift-report.*`:

| Type | Meaning |
| --- | --- |
| `PROFILE_COMPONENT_MISSING` | a required component is not installed |
| `PROFILE_COMPONENT_EXTRA` | components are installed that the profile does not include (informational) |
| `PROFILE_VERSION_MISMATCH` | installed version differs from the profile expectation |
| `PROFILE_OPTIONAL_MISSING` | an optional component is absent (informational) |
| `PROFILE_DYNAMIC_CHANGED` | a plugin-injected component is not available |
| `PROFILE_COMPONENT_UNKNOWN` | a profile reference does not resolve to an inventory entry |
| `PROFILE_REPRODUCIBILITY_CHANGED` | the computed reproducibility status changed |

A global environment that contains more than a profile needs is **not** drift. Extras are reported
as informational only; see `config/drift-policy.yaml`.

## Ownership and relationships

Generated files:

- `profiles/ownership-index.yaml` — component → profiles, ownership, canonical/divergent flag.
- `profiles/relationships.yaml` — profile → components, plugin → injected MCP, harness → built-in
  skills.

## Lifecycle

| Status | Use |
| --- | --- |
| `draft` | being written; not validated against a machine yet |
| `active` | describes an environment that is used |
| `deprecated` | superseded; keep it, do not delete it |
| `archived` | no longer maintained |

`profile_version` is incremented when the composition changes materially (components added or
removed, expectation changed). Pure wording fixes do not need a version bump.

## Creating or changing a profile

1. Copy the closest existing profile into `profiles/<id>.yaml`.
2. Reference inventory ids only; add a new inventory entry first if the component is not listed.
3. Set `status: draft`, then validate with `./scripts/audit.sh --profile <id>`.
4. Bump `profile_version` when the composition changes.
5. Run `./scripts/audit.sh --profiles-report` to regenerate the documents and reports.
6. Never store secrets, private names or private URLs in a profile. Use `scope: private` and
   `<private-project>` placeholders.

## Related documentation

- [Self-audit](self-audit.md) — collector, drift detection and CI.
- [Inventory](../inventory/) — the component source of truth.
- [MCP servers](mcps.md), [plugins](plugins.md), [hooks](hooks.md), [skills](skills.md).
- [Installation](installation.md) — per-component installation procedures.
