# Approval gates — Phase 2

Nothing in this document was executed. Machine-level changes require explicit approval per gate.
Repository-level documentation changes are the only changes made in Phase 2.

| Gate | Scope | Status |
| --- | --- | --- |
| A | Security permissions | **Ready — no change required** |
| B | MCP repair | **Completed for verified packages; unknown upstreams preserved** |
| C | Hook/plugin remediation | **Completed (C1)** |
| D | Skill consolidation | **Completed (333 symlinks)** |
| E | Orphaned config cleanup | **Needs more evidence** |
| F | Repository publication | **Ready — feature branch; `main` untouched** |

---

## Gate A — Security permissions

**Evidence:** all four reviewed files are mode `600`; none is tracked by Git or a symlink.

| File | Mode | Target | Action |
| --- | ---: | ---: | --- |
| `~/.config/opencode/opencode.json` | 600 | 600 | none |
| `~/.omp/agent/mcp.json` | 600 | 600 | none |
| `~/.kiro/settings/mcp.json` | 600 | 600 | none |
| `~/.oleafly/config.json` | 600 | 600 | none |

Optional hardening (not required, not executed):

```bash
chmod 700 ~/.config/opencode ~/.kiro ~/.oleafly
```

**Rotation:** not recommended without exposure evidence. None of the four is tracked by Git, synced,
or known to be logged/transmitted.

---

## Gate B — MCP repair

### B1 — Repairable (verified packages)

```bash
# Not executed. Verify before installing.
npm install -g codebase-memory-mcp@0.12.1
npm install -g hostinger-api-mcp@3.8.1
```

Alternatively remove the two entries from `~/.omp/agent/mcp.json` and
`~/.config/opencode/opencode.json`.

### B2 — Stale path (high confidence)

In `~/.omp/agent/mcp.json`, replace:

```json
"gemini-notebook-mcp": {
  "command": "C:\\Users\\<user>\\.local\\bin\\notebooklm-mcp.EXE"
}
```

with:

```json
"gemini-notebook-mcp": {
  "type": "stdio",
  "command": "/home/<user>/.local/bin/notebooklm-mcp",
  "args": []
}
```

The Linux binary exists (uv tool `notebooklm-mcp-cli` 0.15.7).

### B3 — Pin floating MCPs

| Config | Current | Proposed |
| --- | --- | --- |
| OpenCode + OMP | `npx -y mcp-insomnia` | `npx -y mcp-insomnia@0.8.2` |
| OpenCode + OMP | `npx -y @floriscornel/teams-mcp@latest` | `npx -y @floriscornel/teams-mcp@1.0.1` |
| OpenCode | `"oh-my-opencode-slim"` | pin to resolved `3.0.6` if syntax is supported |
| OpenCode vs OMP | `aas-core` 19.15.0 vs 18.10.0 | choose one version |

### B4 — Unknown upstream (needs evidence first)

- `codegraph`: npm `codegraph@1.0.0` is unrelated. Identify the intended project; keep disabled.
- `openagents`: npm `agn@0.1.2` is unrelated. Identify the CLI; keep disabled.

### B5 — Local services

Start BrowserOS (`:9010`), the Obsidian connector (`:27200`), and confirm the Starry consumer
(`:7600`) before changing config.

---

## Gate C — Hook/plugin remediation (C1 completed)

**Status:** **Gate C1 completed.** `claude-agent-sdk==0.2.174` is pre-installed in
`~/.claude/security/agent-sdk-venv` and imports successfully. A healthy venv returns `NOOP_VENV`, so
the normal SessionStart path does not run pip. The failure path remains unpinned.

### Option C1 — Pre-provision a pinned dependency (COMPLETED)

Executed by the owner before Phase 3:

```bash
python3 -m venv ~/.claude/security/agent-sdk-venv
~/.claude/security/agent-sdk-venv/bin/python -m pip install --upgrade pip
~/.claude/security/agent-sdk-venv/bin/python -m pip install "claude-agent-sdk==0.2.174"
```

Phase 3 verified `importlib.metadata.version('claude-agent-sdk') == '0.2.174'` and a successful import.

Verify after approval:

```bash
~/.claude/security/agent-sdk-venv/bin/python -c "import claude_agent_sdk; print('ok')"
```

Why: the hook checks for an importable SDK first; a pre-built venv avoids the unpinned runtime
install. Version `0.2.174` is the latest PyPI release verified on 2026-10-25.

### Option C2 — Disable pending review

Set `SECURITY_GUIDANCE_DISABLE=1` in the harness environment or disable the plugin in OMP. This is
reversible and executes nothing.

### Option C3 — Update

Update the plugin 2.0.15 → 2.0.16, then review the hook diff. Updating does not pin the SDK by
itself.

### Other plugin cleanup (separate approval)

- Remove `superpowers` 6.3.0 and `security-guidance` 2.0.7 stale caches after confirming 7.0.0 /
  2.0.15 work.
- Reinstall or remove the empty `github` plugin.
- Align `aas-core` versions.

---

## Gate D — Skill consolidation

**Status: Completed.** 342 full-tree-identical; 333 converted; 9 `pm-*` excluded (no top-level
`SKILL.md`); 3 divergent + `synced`/`.trash` kept as directories. Rollback backup exists.

Prerequisites before any symlink:

1. Full-directory hashes for the 343 identical candidates (only `SKILL.md` was hashed).
2. Manual decision on `code-review`, `graphify`, `find-docs`.
3. Confirm Claude Code picks up a symlinked skill in this version.
4. Backup of `~/.claude/skills` metadata (not content copy).

Proposed pilot (not executed):

```bash
rm -r ~/.claude/skills/<verified-identical-skill>
ln -s ~/.agents/skills/<verified-identical-skill> ~/.claude/skills/<verified-identical-skill>
```

**Requires explicit approval** and is destructive on the Claude copy. Do not bulk-run.

---

## Gate E — Orphaned config cleanup

**Status: Needs more evidence.** See `audit/orphaned-configs.md`.

Blockers:

- Kiro config was written on 2026-10-25; the writer is unknown.
- Copilot `~/.copilot/ide` may be used by the VS Code extension even though the CLI is absent.
- Gemini/Antigravity may be managed by an IDE not installed on PATH.

Cleanup requires: backup, credential review, revocation decision, removal, verification — all
approved per tool.

---

## Gate F — Repository publication

**Status: Ready.** Branch `docs/toolbox-audit` is based on `origin/main`; private names sanitized;
MIT license/NOTICE preserved; README collision resolved by appending an audit section. Push the
feature branch only; never force push or touch `main`.

---

## Next gate

Gate C1 is complete. The next meaningful gate is **B4** (verify `codegraph`/`openagents` upstreams)
and **D** (skill consolidation), in that order.
