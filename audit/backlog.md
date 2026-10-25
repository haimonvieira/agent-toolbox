# Backlog

Unresolved items requiring human judgment. No automatic remediation.

## High

- [ ] **Identify the intended upstream for the codegraph MCP** — npm codegraph@1.0.0 is unrelated; entry is disabled and preserved.
- [ ] **Identify the intended upstream for the openagents MCP** — npm agn@0.1.2 is unrelated; entry is disabled and preserved.

## Medium

- [ ] **Review code-review skill variants** — Shared copy is newer than the Claude copy; different references.
- [ ] **Review graphify skill variants** — Claude copy uses Agent/CLAUDE.md; shared copy uses Task/AGENTS.md.
- [ ] **Establish provenance for the GSD skill cluster** — Exact upstream/version unproven; original project is archived.
- [ ] **Identify the writer/consumer of the Kiro config** — Config is modified but no executable was found.
- [ ] **Pin the security-guidance failure-path dependency** — Healthy venv is pinned; failed import triggers an unpinned install.
- [ ] **Decide how divergent skill variants are represented per profile** — code-review, graphify and find-docs have harness-specific variants; profiles currently reference the canonical copy.
- [ ] **UNKNOWN: opencode:envsitter-guard@latest** — floating plugin version (`drift`)
- [ ] **UNKNOWN: opencode:opencode-mem@latest** — floating plugin version (`drift`)

## Low

- [ ] **Review find-docs skill variants** — Shared copy adds a Codex-specific sandbox note; Claude copy is tailored.
- [ ] **Confirm whether Gemini/Antigravity and Copilot configs are active** — Preserve until an owner/consumer is identified.
- [ ] **Confirm pinning support for oh-my-opencode-slim** — Resolved 3.0.6 but left managed by OpenCode.
- [ ] **Decide whether to decouple the global skill symlink from the external volume** — Symlink breaks when the volume is unmounted.
- [ ] **Decide whether plugin-managed versions may float in profiles** — oh-my-opencode-slim and the OpenCode npm plugins resolve their own versions.
- [ ] **Add an editor-only profile if the Zed/VS Code setup stays supported** — Only the full profile currently covers editor harnesses.
