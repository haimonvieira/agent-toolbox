# Drift report

- Baseline: `local-state/baseline.yaml`
- Current: `local-state/current.yaml`
- Findings: 11

| Severity | Count |
| --- | ---: |
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 0 |
| Info / expected dynamic | 9 |

## Changes

### Medium

| Type | Item | Detail |
| --- | --- | --- |
| UNKNOWN | `opencode:envsitter-guard@latest` | floating plugin version |
| UNKNOWN | `opencode:opencode-mem@latest` | floating plugin version |

### Info / expected dynamic

| Type | Item | Detail |
| --- | --- | --- |
| PROFILE_COMPONENT_EXTRA | `claude-code` | 9 component(s) installed but not part of the profile (harness=7, mcp=1, plugin=1) |
| PROFILE_OPTIONAL_MISSING | `codex` | 5 optional component(s) not installed: hook-codex-project-hooks-team-lead, skill-imagegen, skill-openai-docs, skill-review-agent, skill-skill-installer |
| PROFILE_COMPONENT_EXTRA | `codex` | 9 component(s) installed but not part of the profile (harness=7, mcp=1, plugin=1) |
| PROFILE_OPTIONAL_MISSING | `full` | 9 optional component(s) not installed: hook-codex-project-hooks-team-lead, hook-lethe-refresh-index, hook-orca-agent-status-extension, hook-orca-prefill-extension, hook-pr-template-guard-extension, skill-imagegen, skill-openai-docs, skill-review-agent... |
| PROFILE_COMPONENT_EXTRA | `full` | 6 component(s) installed but not part of the profile (harness=4, mcp=1, plugin=1) |
| PROFILE_COMPONENT_EXTRA | `minimal` | 8 component(s) installed but not part of the profile (harness=6, mcp=1, plugin=1) |
| PROFILE_OPTIONAL_MISSING | `omp` | 8 optional component(s) not installed: hook-lethe-refresh-index, hook-orca-agent-status-extension, hook-orca-prefill-extension, hook-pr-template-guard-extension, plugin-orca-agent-status, plugin-orca-prefill, plugin-orca-titlebar-spinner, plugin-pr-template-guard |
| PROFILE_COMPONENT_EXTRA | `omp` | 9 component(s) installed but not part of the profile (harness=7, mcp=1, plugin=1) |
| PROFILE_COMPONENT_EXTRA | `opencode-go` | 8 component(s) installed but not part of the profile (harness=6, mcp=1, plugin=1) |

## Recommended actions

- Review `High` and `Critical` findings before acting.
- Do not auto-update or auto-remove anything.
- Update the baseline only after reviewing changes: `./scripts/audit.sh --accept-baseline --yes`.

## Limitations

- Runtime MCP handshakes, hook execution, and plugin behaviour are not tested.
- Plugin-injected tools are only observed statically; `EXPECTED_DYNAMIC` policy covers known cases.
- Quick mode does not hash skill contents.
