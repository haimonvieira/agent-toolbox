# Drift report

- Generated: 2026-10-25T17:11:46+00:00
- Baseline: `local-state/baseline.yaml`
- Current: `local-state/current.yaml`
- Findings: 2

| Severity | Count |
| --- | ---: |
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 0 |
| Info / expected dynamic | 0 |

## Changes

### Medium

| Type | Item | Detail |
| --- | --- | --- |
| UNKNOWN | `opencode:envsitter-guard@latest` | floating plugin version |
| UNKNOWN | `opencode:opencode-mem@latest` | floating plugin version |

## Recommended actions

- Review `High` and `Critical` findings before acting.
- Do not auto-update or auto-remove anything.
- Update the baseline only after reviewing changes: `./scripts/audit.sh --accept-baseline --yes`.

## Limitations

- Runtime MCP handshakes, hook execution, and plugin behaviour are not tested.
- Plugin-injected tools are only observed statically; `EXPECTED_DYNAMIC` policy covers known cases.
- Quick mode does not hash skill contents.
