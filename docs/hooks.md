# Hooks

Hooks are commands a harness runs around agent events (session start, prompt submit, tool use,
stop). They are the **highest-risk** part of an agent setup: they execute automatically and often
have network and filesystem access.

No hook was executed during this audit. Everything below comes from static reading.

Full metadata: [inventory/hooks.yaml](../inventory/hooks.yaml).

## Git hooks

| Check | Result |
| --- | --- |
| `core.hooksPath` | unset |
| Inspected repository (`~/TeleDrive`) | only sample hooks, none active |
| Other repositories | not recursively scanned (out of scope) |

No Git-hook manager (Husky, Lefthook, pre-commit) was found in the inspected repository.

## Agent hooks

### Ponytail (Claude Code, Codex)

Source: `~/.claude/plugins/cache/ponytail/ponytail/5.3.2/hooks/claude-codex-hooks.json`

| Trigger | Executes | Notes |
| --- | --- | --- |
| `SessionStart` (startup/resume/clear/compact) | `node hooks/ponytail-activate.js` | 15 s timeout |
| `SubagentStart` | `node hooks/ponytail-subagent.js` | Injects mode into subagents |
| `UserPromptSubmit` | `node hooks/ponytail-mode-tracker.js` | Tracks mode changes |

Codex trusts the same hook set through `hooks.state` SHA-256 hashes in `~/.codex/config.toml`.
Ponytail also ships `copilot-hooks.json`, `cursor-hooks.json`, `qoder-hooks.json`, and
`claude-band.json`; those harnesses are not active here.

### Security-guidance (OMP)

Source: `~/.omp/plugins/cache/plugins/claude-plugins-official___security-guidance___2.0.15/hooks/hooks.json`

| Trigger | Executes | Risk |
| --- | --- | --- |
| `SessionStart` | `ensure_agent_sdk.py` | **Creates a venv and `pip install`s `claude_agent_sdk` if missing** — network + mutation |
| `UserPromptSubmit` | `security_reminder_hook.py` | Adds security reminders |
| `PostToolUse` (`Edit|Write|MultiEdit|NotebookEdit`, `git commit`) | `security_reminder_hook.py` | Pattern warnings |
| `Stop` | Git-diff based LLM review | Network access to the model provider |

This is the most consequential hook locally. It can install a dependency on first session start and
send diffs for review. Review it before enabling on a new machine. No integrity pin was observed in
the script header.

Phase 2 detail:

- **Version:** installed 2.0.15; marketplace catalog 2.0.16; Apache-2.0.
- **Command:** `python -m pip install --quiet --disable-pip-version-check --prefer-binary --no-cache-dir claude-agent-sdk`
  inside `~/.claude/security/agent-sdk-venv` (or a `--target` fallback).
- **Every session?** Yes — `SessionStart` has no matcher, 180 s timeout.
- **State (Phase 3):** `~/.claude/security/agent-sdk-venv` exists with `claude-agent-sdk==0.2.174`
  and imports successfully, so the bootstrap returns `NOOP_VENV` and does not run pip.
- **Gate C1:** **Completed / Mitigated** — the normal install path is closed; the failure path remains.
- **Network:** yes (PyPI).
- **Kill switches:** `SECURITY_GUIDANCE_DISABLE=1` (whole plugin) or
  `ENABLE_CODE_SECURITY_REVIEW=0` (LLM review only).
- **Activation:** inferred from installation and the hook manifest; no runtime verification.
- **Upstream:** active (`anthropics/claude-plugins-official`, last plugin commit 2026-10-21).

### SonarQube (OMP)

`SessionStart` runs `node scripts/setup.js` (30 s timeout). The plugin uses the Sonar
Source-Available License; hooks were not executed.

### Superpowers (OMP)

`SessionStart` runs `hooks/run-hook.cmd session-start` under bash. It also provides a Cursor
variant. The plugin is installed at 7.0.0; a 6.3.0 cache remains on disk.

### Lethe (OMP)

`before_agent_start` runs `hooks/refresh-index.sh`, a detached, throttled (`LETHE_REFRESH_INTERVAL`,
default 900 s) `lethe index --all`. It writes a local search index and exits immediately.

### OMP extensions

Four TypeScript extensions load directly from `~/.omp/agent/extensions`:

| File | Behaviour | Provenance |
| --- | --- | --- |
| `orca-agent-status.ts` | POSTs agent status to a local Orca receiver (1 s timeout, latest-only queue) | Orca-managed (`@orca-managed-pi-extension`) |
| `orca-prefill.ts` | Reads `ORCA_OMP_PREFILL` on `session_start` and sets editor text | Orca-managed |
| `orca-titlebar-spinner.ts` | Braille spinner in the titlebar | Orca-managed |
| `pr-template-guard.ts` | Blocks `gh pr create` until a PR template and a private coordination skill are read | **Locally authored**; contains a private organization reference |

### Orphaned project hooks (Codex)

`~/.codex/config.toml` contains trusted hashes for
`<external-volume>/<project>/.codex/hooks.json` (`session_end`, `user_prompt_submit`,
`stop`). The volume was mounted later in the audit, so the file became inspectable: it runs a local
`state_freshness.py` (3 s timeout) on prompt, stop, and session end, and fails open when its checks
cannot complete. When the volume is unmounted the hooks are inoperative while the trusted hashes
remain.

## Security review checklist for any new hook

1. Read the command and every script it calls; resolve `${PLUGIN_ROOT}` paths.
2. Check for network access (`curl`, `wget`, HTTP clients, `pip/npm install`).
3. Check for writes outside the repository (home config, venv, state files).
4. Check for destructive commands (`rm -rf`, `git reset --hard`, `sudo`).
5. Confirm whether it needs secrets and how they are supplied.
6. Prefer hooks with pinned versions and review diffs on plugin update.
7. Disable a hook if you cannot explain what it does.

## Safe inspection commands

```bash
# List hook manifests in installed plugin caches (read-only)
find ~/.claude/plugins/cache ~/.omp/plugins/cache -maxdepth 4 -name '*hooks*.json' -o -name 'hooks.json'

# Show a hook config without executing it
sed -n '1,80p' <path-to-hooks.json>

# Git hook status
git config --global --get core.hooksPath || echo "unset"
ls -l <repo>/.git/hooks | grep -v '\.sample$'
```

Never run a hook manually just to see what it does. If you must test one, run it in a disposable
container or VM with no credentials.
