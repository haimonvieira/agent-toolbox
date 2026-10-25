# Plugins (repository entry point)

- Full inventory: [`inventory/plugins.yaml`](../inventory/plugins.yaml) (17 entries: 13 plugin bundles + 4 extensions, plus stale caches).
- Guide: [`docs/plugins.md`](../docs/plugins.md).

## Installed by harness

| Harness | Plugins |
| --- | --- |
| Claude Code | `ponytail` 5.3.2 |
| Codex CLI | `ponytail` 5.3.2 |
| OMP | `ponytail`, `superpowers`, `sonarqube`, `42crunch-api-security-testing`, `coderabbit`, `feature-dev`, `context7`, `github`, `security-guidance`, `lethe`, `best-of` + 4 extensions |
| OpenCode | `oh-my-opencode-slim` 3.0.6 |
| VS Code | `openai.chatgpt` (two versions) |

## Rules

1. Plugins execute code and hooks; install only from a marketplace/source you trust.
2. Read the hook manifest after install and after every update.
3. Do not vendor plugin code into this repository (licenses vary; `sonarqube` is source-available).
4. Remove stale cache versions after confirming the current version works.
5. Empty install directories are a failed install, not a working plugin.
