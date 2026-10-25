# MCP servers

MCP (Model Context Protocol) servers expose tools and data to an agent. This machine has
**19 distinct servers** across seven harness configs (plus plugin-injected servers). Phase 3 repaired
three verified entries and disabled two unresolved upstreams; three depend on local services that
were not running at audit time.

Full metadata: [inventory/mcps.yaml](../inventory/mcps.yaml). Sanitized examples:
[configs/examples/](../configs/examples/).

## Inventory

| Server | Transport | Harnesses | Command / URL | Status |
| --- | --- | --- | --- | --- |
| `pencil` | stdio | OpenCode, Claude, OMP, Kiro | pen.dev bundled binary | Configured, executable exists |
| `browseros-neo` | HTTP | OpenCode, Claude, Codex, OMP, Zed, Gemini | `http://127.0.0.1:9010/mcp` | Configured, **service down at audit** |
| `graphify` | HTTP | OpenCode, Codex, OMP | `https://api.graphify.com/mcp` | Configured, provenance unverified |
| `cloudflare-api` | HTTP | OpenCode, OMP | `https://mcp.cloudflare.com/mcp` | Configured |
| `figma` | HTTP | OpenCode, OMP | `https://mcp.figma.com/mcp` | Configured |
| `doop` | HTTP | OpenCode, OMP | `https://doop.design/mcp` | Configured, purpose unknown |
| `obsidian-mcp-connector` | HTTP | OpenCode, OMP | `http://127.0.0.1:27200/mcp` | Config has bearer header; **service down** |
| `insomnia` | stdio | OpenCode, OMP | `npx -y mcp-insomnia@0.8.2` | Configured, pinned |
| `aas-core` | stdio | OpenCode (disabled), OMP | `npx … agentic-awesome-skills@<ver> … aas mcp` | Version conflict 19.15.0 vs 18.10.0 |
| `teams-mcp` | stdio | OpenCode, OMP | `npx -y @floriscornel/teams-mcp@1.0.1` | Configured, pinned |
| `codegraph` | stdio | OpenCode (disabled), OMP (disabled) | `codegraph serve --mcp` | Unknown upstream — preserved/disabled |
| `codebase-memory` | stdio | OpenCode (disabled), OMP | `codebase-memory-mcp` | Installed 0.12.1 |
| `openagents` | stdio | OpenCode (disabled), OMP (disabled) | `agn mcp-server …` | Unknown upstream — preserved/disabled |
| `hostinger-api` | stdio | OpenCode (disabled), OMP | `hostinger-api-mcp` | Installed 3.8.1 |
| `gemini-notebook-mcp` | stdio | OMP | `~/.local/bin/notebooklm-mcp` | Repaired (Linux path) |
| `starry` | HTTP | Kiro | `http://127.0.0.1:7600/mcp` | Kiro not installed; service down |
| `context7` | plugin-managed | OpenCode | injected by `oh-my-opencode-slim` | Added during audit |
| `gh_grep` | plugin-managed | OpenCode | injected by `oh-my-opencode-slim` | Added during audit |
| `omgskills` | plugin-managed | OpenCode | injected by `oh-my-opencode-slim` | Added during audit (after 11:07) |

## Broken / questionable entries — Phase 2 classification

| Server | Class | Evidence | Proposed action (approval required) |
| --- | --- | --- | --- |
| `codegraph` | **Unknown upstream** | No executable. npm `codegraph@1.0.0` is a 2024 package by an unrelated maintainer with no repository metadata. | **Applied:** disabled in OMP with `enabled: false`; OpenCode already disabled. Do not `npx codegraph`. |
| `codebase-memory` | **Repairable** | npm `codebase-memory-mcp@0.12.1`, MIT, repo `DeusData/codebase-memory-mcp` verified. | **Applied:** installed globally at 0.12.1; binary present. Runtime not started. |
| `openagents` | **Unknown upstream** | No `agn` executable. npm `agn@0.1.2` is an unrelated 2022 package; no OpenAgents CLI found. | **Applied:** disabled in OMP with `enabled: false`; preserved for identification. |
| `hostinger-api` | **Repairable** | npm `hostinger-api-mcp@3.8.1`, MIT, repo `hostinger/api-mcp-server` verified. | **Applied:** installed globally at 3.8.1; binary present. Runtime not started. |
| `gemini-notebook-mcp` | **Stale config** | Config pointed to a Windows `.EXE`; Linux binary exists at `~/.local/bin/notebooklm-mcp` (uv tool 0.15.7). | **Applied:** command replaced with the Linux path; args preserved. |
| `browseros-neo` | **Requires manual service** | Port 9010 closed at audit time. | Start BrowserOS. |
| `obsidian-mcp-connector` | **Requires manual service** | Port 27200 closed at audit time. | Enable the Obsidian connector plugin. |
| `starry` | **Requires manual service / unknown** | Port 7600 closed; Kiro not installed; Starry app exists but no consumer confirmed. | Resolve the consumer before editing. |

**Replacement analysis:** `graphify` (remote knowledge graph) and `pi-gitnexus` (OMP package) may
cover part of the intent of `codegraph`/`codebase-memory`, but behavioural equivalence is **not
verified**. Do not remove the broken entries on that assumption alone.

## Local vs remote

- **stdio** servers are child processes started by the harness. They must have a runnable command;
  otherwise the harness reports a failed server. Four stdio entries here have no executable.
- **HTTP** servers point at a URL. Local URLs (`127.0.0.1`) require a companion app to be running.
  Remote URLs leave the machine and may require OAuth.
- **Plugin-managed** servers are not in `opencode.json`; they appear at runtime because a plugin
  registers them. They cannot be removed without changing the plugin.

## Configuration patterns per harness

### OpenCode — `~/.config/opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "example-local": {
        "type": "local",
        "command": ["npx", "-y", "some-mcp@1.2.3"]
      },
      "example-remote": {
        "type": "remote",
        "url": "https://example.com/mcp",
        "headers": { "Authorization": "Bearer <REDACTED>" }
      }
    }
  }
}
```

Notes: `type` is `local` or `remote`; `disabled: true` keeps an entry but does not start it.

### Claude Code — `~/.claude.json`

```json
{
  "mcpServers": {
    "example-local": {
      "type": "stdio",
      "command": "/absolute/path/to/server",
      "args": ["--flag"]
    },
    "example-remote": {
      "type": "http",
      "url": "http://127.0.0.1:9010/mcp"
    }
  }
}
```

Notes: project-scoped servers live under `projects["<path>"].mcpServers`. `~/.claude.json` also
contains account state; never copy the whole file into a repository.

### Codex CLI — `~/.codex/config.toml`

```toml
[mcp_servers.example-local]
command = "/absolute/path/to/server"
args = ["--flag"]

[mcp_servers.example-remote]
url = "https://example.com/mcp"
```

Notes: TOML tables; no `type` field in the entries observed locally.

### OMP — `~/.omp/agent/mcp.json`

```json
{
  "mcpServers": {
    "example-local": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "some-mcp@1.2.3"],
      "env": { "SOME_TOKEN": "<REDACTED>" }
    },
    "example-remote": {
      "type": "http",
      "url": "https://example.com/mcp",
      "enabled": true
    }
  }
}
```

Notes: OMP supports an `auth` object with OAuth metadata. The observed file is mode `777` but sits
inside a `700` directory.

### Zed — `~/.config/zed/settings.json` (JSONC)

```jsonc
{
  "context_servers": {
    "example-remote": {
      "url": "http://127.0.0.1:9010/mcp",
      "source": "custom",
      "enabled": true
    }
  }
}
```

### Gemini / Antigravity — `~/.gemini/config/mcp_config.json`

```json
{
  "mcpServers": {
    "example-remote": { "serverUrl": "http://127.0.0.1:9010/mcp" }
  }
}
```

### Kiro — `~/.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "example-remote": {
      "url": "http://127.0.0.1:7600/mcp",
      "headers": { "Authorization": "Bearer <REDACTED>" }
    },
    "example-local": {
      "command": "/absolute/path/to/server",
      "args": ["--app", "desktop", "--agent", "kiroCLI"],
      "env": {}
    }
  }
}
```

The same server therefore needs **different syntax** in each harness. Do not copy a Claude block
into an OpenCode config without translating the wrapper key and transport field.

## Environment variables

Recorded by name only:

| Server | Variable names |
| --- | --- |
| `teams-mcp` | `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET` (upstream-documented; not present locally) |
| `openagents` | `OA_WORKSPACE_TOKEN` |
| `hostinger-api` | `HOSTINGER_API_TOKEN` |
| `obsidian-mcp-connector` | `OBSIDIAN_MCP_TOKEN` (header-based locally) |
| `starry` | `STARRY_TOKEN` |
| `context7` | `CONTEXT7_API_KEY` (optional) |

Set them in the harness's environment or its secret mechanism; never commit values. See
[.env.example](../.env.example).

## Secrets hygiene

Observed local practice that should be improved:

- `~/.config/opencode/opencode.json` is mode `644` and contains a bearer header and workspace token
  for local/remote MCPs.
- `~/.omp/agent/mcp.json` is mode `777` (inside a `700` directory).
- `~/.kiro/settings/mcp.json` is mode `664` and contains a bearer header.
- `~/.oleafly/config.json` stores provider keys, a GitHub token, and an MCP token in plaintext
  (not read; names observed only).

Recommended: move MCP secrets to the harness's credential store or an OS keyring, restrict file
modes (`600`), and rotate anything that was ever world-readable. This audit changed nothing.

## Pinning floating execution — Phase 2

| Entry | Configured form | Resolved evidence | Proposed pinned form |
| --- | --- | --- | --- |
| `insomnia` | `npx -y mcp-insomnia` | Upstream 0.8.2 | **Applied:** `npx -y mcp-insomnia@0.8.2` |
| `teams-mcp` | `npx -y @floriscornel/teams-mcp@latest` | Upstream 1.0.1 | **Applied:** `npx -y @floriscornel/teams-mcp@1.0.1` |
| `oh-my-opencode-slim` | `"plugin": ["oh-my-opencode-slim"]` | Local cache 3.0.6 | **Left managed:** OpenCode resolves npm plugins through Bun; exact pin syntax is not documented. Resolved version recorded as 3.0.6. |
| `aas-core` | pinned 19.15.0 / 18.10.0 | Two harnesses disagree | Align both to one version |
| `codegraph` | `codegraph serve --mcp` | No package identity | Do not pin until upstream is verified |

Pinning does not guarantee safety, but it makes updates reviewable. Record the resolved version in
`inventory/mcps.yaml` after each change.

## Verify an MCP safely

```bash
# 1. Does the executable exist?
command -v codegraph || echo "missing"

# 2. Is a local HTTP service listening? (no MCP handshake, no code execution)
ss -ltn | grep ':9010' || echo "not listening"

# 3. Does the package exist upstream, and what is its license/repo?
npm view <package> version repository.url license
```

Do **not** run `npx <unknown-package>` or a harness "doctor"/"health" command that starts MCPs and
executes plugin hooks just to test configuration. The audit did not start any MCP server.

## Troubleshooting

| Symptom | Likely cause here | Check |
| --- | --- | --- |
| Server fails immediately | Command not on `PATH` | `command -v <cmd>` |
| Server starts then disconnects | Local companion app not running | `ss -ltn | grep <port>` |
| Server works in one harness, not another | Different config syntax | Compare with `configs/examples/` |
| Auth loop | OAuth cache/session | Harness auth cache; do not paste tokens into reports |
| Duplicate tools with different schemas | Same server configured in several harnesses at different versions | Compare versions in `inventory/mcps.yaml` |
| Windows path error on Linux | `C:\...` entry | Fix to a Linux path; do not run under Wine |

Notable local breakages: `gemini-notebook-mcp` points at a Windows `.EXE` although the Linux binary
exists at `~/.local/bin/notebooklm-mcp`; `codegraph` refers to an npm name with no upstream
repository metadata and no installed executable — do not `npx` it blindly.
