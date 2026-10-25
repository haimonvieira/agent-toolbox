# Profiles

Declarative environment profiles. Read [docs/profiles.md](../docs/profiles.md) for the model.

| File | Profile | Notes |
| --- | --- | --- |
| `base.yaml` | shared baseline | runtime prerequisites + canonical skill store only |
| `opencode-go.yaml` | OpenCode (Go provider) | `oh-my-opencode-slim` preset, npm plugins, MCPs, injected tools |
| `omp.yaml` | Oh My Pi | marketplace plugins, local extensions, managed skills, plugin hooks |
| `codex.yaml` | Codex CLI | built-in skills, canonical store, project hooks on an external volume |
| `claude-code.yaml` | Claude Code | symlinked skill store, ponytail plugin, MCPs |
| `minimal.yaml` | minimal setup | one harness, canonical skills, no integrations |
| `full.yaml` | full environment | everything with a verified upstream; unknown items stay unresolved |

Generated (do not edit by hand, regenerate with `./scripts/audit.sh --profiles-report`):

- `reproducibility.yaml` — computed status per profile.
- `ownership-index.yaml` — component → owning profiles.
- `relationships.yaml` — profile → component relationships.

Rules:

- Reference inventory ids; never duplicate component metadata.
- Environment variables are names only.
- Private names are not allowed; use `scope: private` and `<private-project>`.
- Unknown upstreams belong in `unresolved`, never in `required`.
