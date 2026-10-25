# MCP servers (repository entry point)

- Full inventory: [`inventory/mcps.yaml`](../inventory/mcps.yaml) (19 servers).
- Guide: [`docs/mcps.md`](../docs/mcps.md).
- Sanitized examples: [`configs/examples/`](../configs/examples/).

## Status summary

| Status | Servers |
| --- | --- |
| Configured with upstream/package evidence | `pencil`, `insomnia`, `aas-core`, `teams-mcp` |
| Remote, provider-managed | `cloudflare-api`, `figma`, `graphify`, `doop` |
| Local service not running at audit | `browseros-neo`, `obsidian-mcp-connector`, `starry` |
| Broken (missing executable/path) | `codegraph`, `codebase-memory`, `openagents`, `hostinger-api`, `gemini-notebook-mcp` |
| Plugin-injected | `context7`, `gh_grep`, `omgskills` |

## Rules

1. Never start an unknown MCP to "see if it works".
2. Pin package versions; avoid `npx -y <pkg>` without a version.
3. Keep secrets out of configs, or use the harness credential store.
4. Check the executable (`command -v`) and local port (`ss -ltn`) before assuming a server is down.
5. Do not install a package just because a config references its name — verify upstream first
   (`npm view <pkg> repository.url license`).
