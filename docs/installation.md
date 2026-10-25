# Installation

How to rebuild this setup on a new Linux machine. Commands are labelled by evidence:

- **Verified locally** — the package/version is installed this way on this machine.
- **Verified upstream** — checked against the public registry/repository during the audit.
- **Not verified** — plausible from local evidence, but not tested here.

Never run downloaded install scripts from this document blindly. Prefer the package manager
command, then verify the binary and version.

## Prerequisites

| Requirement | Local evidence | Install |
| --- | --- | --- |
| Git | `/usr/bin/git` 2.43.0 | distro package |
| Node.js 24.22.0 via nvm | `~/.nvm/versions/node/v24.22.0` | nvm (upstream: <https://github.com/nvm-sh/nvm>) |
| npm 11.19.1 | bundled with Node | — |
| uv 0.13.5 | `~/.local/bin/uv` | <https://docs.astral.sh/uv/> |
| `~/.local/bin` on `PATH` | Claude, OMP, uv, graphify, zed live there | shell profile |

`pipx` is **not** installed. Python CLI tools here use `uv tool` or a dedicated venv.

## Harnesses

### OpenCode — recommended installation: npm global

Why: this is how it is installed locally; it keeps the binary under the active Node version.

```bash
npm install -g @opencode/cli        # Verified locally (@opencode/cli 2.1.4)
opencode --version                  # expect 2.1.4 or newer
```

- Config: `~/.config/opencode/opencode.json`, `cli.json`, `AGENTS.md`.
- Skills: `~/.agents/skills` (shared layout).
- Update: `npm install -g @opencode/cli@latest`.
- Remove: `npm uninstall -g @opencode/cli`.
- Official docs: <https://opencode.ai/docs>.
- Not verified: the official standalone installer; this setup does not use it.

### Claude Code — recommended installation: official native installer

Why: the local install is native (`installMethod: native`) at `~/.local/share/claude/versions/`,
with auto-updates disabled.

```bash
# Use the official procedure at:
# https://docs.claude.com/en/docs/claude-code/overview
claude --version                    # Verified locally: 2.1.309
```

- Config: `~/.claude/settings.json`, `~/.claude.json`.
- Skills: `~/.claude/skills` (or symlink to `~/.agents/skills`).
- Update: re-run the official installer; auto-update is disabled locally.
- Remove: official uninstall procedure (not verified locally).

### Codex CLI — recommended installation: npm global

```bash
npm install -g @openai/codex        # Verified locally (@openai/codex 0.164.0)
codex --version                     # expect codex-cli 0.164.0 or newer
```

- Config: `~/.codex/config.toml` (mode should be `600`).
- Update: `npm install -g @openai/codex@latest`.
- Remove: `npm uninstall -g @openai/codex`.
- Docs: <https://developers.openai.com/codex>.

### OMP — installation: standalone binary

```bash
# There is no package-manager metadata next to the local binary.
# Obtain the release from the upstream project and place it on PATH:
# https://github.com/can1357/oh-my-pi
install -m 755 ./omp ~/.local/bin/omp
omp --version                       # Verified locally: omp/18.12.6
```

- Config: `~/.omp/agent/` (`config.yml`, `mcp.json`), `~/.omp/plugins/`.
- Update: upstream release process (not verified).
- Remove: delete the binary and `~/.omp` (manual).

### freebuff

```bash
npm install -g freebuff             # Verified locally: 0.2.34
```

Upstream repository is private; only the public site (<https://freebuff.com>) is reachable.

### Editors

| Tool | Installation | Verification |
| --- | --- | --- |
| Zed 1.25.3 | vendor app bundle in `~/.local/zed.app`, symlink `~/.local/bin/zed` | `zed --version` |
| Delta 0.20.1 | vendor app bundle in `~/.local/delta.app`, symlink `~/.local/bin/delta` | `delta --version` |
| pen.dev desktop / CLI | desktop app in `~/Applications/pen` + npm `@pen.dev/cli` 0.3.12 | `pen` (TUI; do not run with `--version` expecting a quick exit) |
| VS Code ChatGPT | `code --install-extension openai.chatgpt` (standard VS Code CLI; not run) | Extensions view |

## Skills

Full guide: [skills.md](skills.md). Recommended installation is the `skills` CLI because it writes
provenance to `~/.agents/.skill-lock.json`:

```bash
npx skills add <owner>/<repo>
```

Manual alternative: copy only the desired skill directory into `~/.agents/skills/<name>/` after
checking out a known commit. Do not copy `node_modules`, `.git`, or caches.

To reuse the same store in Claude Code, symlink rather than duplicate:

```bash
ln -s ~/.agents/skills/<name> ~/.claude/skills/<name>
```

## MCP servers

Syntax per harness: [mcps.md](mcps.md). Sanitized examples: `configs/examples/`.

### Local stdio servers that need a package

| Server | Install | Pin |
| --- | --- | --- |
| `insomnia` | `npm install -g mcp-insomnia@0.8.2` (or keep `npx`) | pin `0.8.2` |
| `teams-mcp` | `npm install -g @floriscornel/teams-mcp@1.0.1` | replace `@latest` |
| `aas-core` | `npm install -g agentic-awesome-skills@19.15.0` | align both harnesses |
| `codebase-memory` | `npm install -g codebase-memory-mcp@0.12.1` | pin |
| `hostinger-api` | `npm install -g hostinger-api-mcp@3.8.1` | pin |

All packages above were verified on the public npm registry during the audit. Installing them is a
user action; none were installed by this audit.

`codegraph` is **not** installable from the name alone: the npm package `codegraph@1.0.0` has no
repository metadata and the intended project is unverified. Leave it disabled until the correct
upstream is identified.

### Local companion servers

| Server | Companion | Verification |
| --- | --- | --- |
| `pencil` | pen.dev desktop app | binary exists at `~/Applications/pen/resources/app.asar.unpacked/out/mcp-server-linux-x64` |
| `browseros-neo` | BrowserOS relay on `127.0.0.1:9010` | `ss -ltn | grep 9010` |
| `obsidian-mcp-connector` | Obsidian plugin on `127.0.0.1:27200` | `ss -ltn | grep 27200` |
| `starry` | Starry app on `127.0.0.1:7600` | not installed here |

### Remote servers

`cloudflare-api`, `figma`, `graphify`, `doop` need network access and possibly OAuth. Add the entry
in the harness config and complete the harness's auth flow. Do not paste tokens into this repo.

### Fix the known broken entry

`gemini-notebook-mcp` in `~/.omp/agent/mcp.json` points to a Windows path. On Linux use:

```json
"gemini-notebook-mcp": {
  "type": "stdio",
  "command": "~/.local/bin/notebooklm-mcp",
  "args": []
}
```

The binary comes from `uv tool install notebooklm-mcp-cli` (verified locally, 0.15.7).

## Plugins

| Harness | Command | Evidence |
| --- | --- | --- |
| Claude Code | `claude plugin marketplace add <owner>/<repo>` then `claude plugin install <plugin>@<marketplace>` | Locally installed; exact CLI flags not re-verified |
| Codex | add `[marketplaces.*]` and `[plugins."name@marketplace"]` to `config.toml` | Verified locally |
| OMP | use the plugin/marketplace UI or CLI; state in `~/.omp/plugins/installed_plugins.json` | Exact command not verified |
| OpenCode | add `"plugin": ["<package>"]` to `opencode.json` and configure its JSON file | Verified locally |
| VS Code | `code --install-extension openai.chatgpt` | Standard CLI; not run |

Recommended pinning: avoid `@latest` for plugins and npm MCPs; record the resolved version in
`inventory/` after each update.

## Hooks

Reproduce hooks by installing the plugin that ships them; do not hand-copy hook scripts.

| Hook set | Comes from | Caution |
| --- | --- | --- |
| Ponytail lifecycle | `ponytail` plugin | Node scripts at session start |
| Security review | `security-guidance` 2.0.15 (Apache-2.0) | May `pip install claude-agent-sdk` at session start; no venv exists yet |
| SonarQube setup | `sonarqube` plugin | Source-available license |
| Superpowers session start | `superpowers` plugin | Bash wrapper |
| Lethe index refresh | `lethe` plugin | Background index writes |
| Orca status/prefill | Orca app | Local HTTP only |
| PR template guard | locally authored extension | Contains a private org reference |

After installing, inspect the hook manifest before the first session (see
[hooks.md](hooks.md#security-review-checklist-for-any-new-hook)).

For `security-guidance`, pre-provision the dependency at a pinned version **before** the first
session if you keep the plugin (Gate C, requires approval):

```bash
python3 -m venv ~/.claude/security/agent-sdk-venv
~/.claude/security/agent-sdk-venv/bin/python -m pip install "claude-agent-sdk==0.2.174"
```

The hook checks for an importable SDK first; a pre-built venv avoids the unpinned runtime install.

## Configuration examples

Copy and edit, never copy live configs verbatim (they contain tokens):

- `configs/examples/opencode.mcp.json`
- `configs/examples/claude.mcp.json`
- `configs/examples/codex.config.toml`
- `configs/examples/omp.mcp.json`
- `configs/examples/zed.context_servers.jsonc`
- `configs/examples/gemini.mcp.json`
- `configs/examples/kiro.mcp.json`

## Post-install verification

```bash
bash scripts/verify.sh          # paths, YAML/JSON syntax, secret patterns
bash scripts/audit.sh           # read-only environment snapshot
for c in opencode claude codex omp; do command -v "$c" && "$c" --version; done
```
