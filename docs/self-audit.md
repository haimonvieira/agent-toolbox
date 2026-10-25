# Self-audit

`agent-toolbox` can compare its documented inventory with the real local agent environment and
produce deterministic drift reports. The default mode is **READ ONLY**.

> The audit never installs, removes, updates, or executes unknown agent tooling. It never starts MCP
> servers, runs hooks, loads plugins, or executes skill scripts.

## Local audit vs repository validation

| Mode | Runs where | Sees the local machine? | Purpose |
| --- | --- | --- | --- |
| **Local audit** | your workstation | yes | collect sanitized state, fingerprint skills, detect drift |
| **Repository CI** | GitHub Actions | **no** | schema, YAML/JSON/TOML, links, secrets, inventory consistency |

CI cannot inspect `~/.agents/skills`, local MCP configs, installed harnesses, or private paths. It
validates only committed, sanitized data.

## Commands

```bash
./scripts/audit.sh                  # full: validate + collect + drift + reports
./scripts/audit.sh --quick          # fast: versions/configs/symlinks, no content hashing
./scripts/audit.sh --report-only    # regenerate reports from existing baseline/current
./scripts/audit.sh --accept-baseline --yes
./scripts/audit.sh --check-upstreams # optional public registry check
./scripts/verify.sh                 # repository-only checks (fast, no local scan)
./scripts/check-links.sh            # public external links (network)
```

Exit codes:

| Code | Meaning |
| ---: | --- |
| 0 | no actionable drift / validation passed |
| 1 | repository validation failed |
| 2 | actionable drift according to `config/drift-policy.yaml` |
| 3 | usage/config error (missing baseline, refused baseline overwrite) |

## How it works

1. **Collector** (`scripts/audit.py collect`) reads allowlisted harness, skill, MCP, plugin, hook,
   and config paths. It records versions, modes, credential **field names**, symlink targets, and
   full-tree skill fingerprints. Values are never written.
2. **Snapshot** (`local-state/current.yaml`) is sanitized: `~`, `<repo-root>`,
   `<external-volume>/<project>`; managed-skill names are redacted.
3. **Baseline** (`local-state/baseline.yaml`) is the reviewed snapshot committed to the repository.
4. **Drift detector** compares baseline vs current and writes `audit/drift-report.md` +
   `audit/drift-report.yaml`.
5. **Repository validator** checks schemas, YAML/JSON/TOML, links, duplicates, absolute paths,
   secret patterns, and freshness.
6. **Reports** add `audit/backlog.md` and `audit/update-suggestions.md`. Nothing is applied.

## Skill fingerprinting

Every regular file is hashed with its normalized relative path. Symlinked skill directories are
recorded as links, not followed. The cache at `.local-state/skill-cache.json` stores metadata
signatures and tree hashes only; redacted managed-skill paths are never cached by name. Quick mode skips content hashes.

## Drift policy

Edit `config/drift-policy.yaml` to change severity, expected plugin-injected tools, or exit
behavior. Expected dynamic entries are reported as `EXPECTED_DYNAMIC` and do not fail the audit.

## Baseline workflow

Never accept a baseline automatically after drift.

1. Run `./scripts/audit.sh` and review `audit/drift-report.md`.
2. Confirm the changes are understood and contain no private identifiers.
3. Run `./scripts/audit.sh --accept-baseline --yes`.
4. Commit the updated `local-state/baseline.yaml` with a review note.

`local-state/current.yaml` and `.local-state/` are gitignored.

## Optional pre-commit hook

Do **not** install it automatically. To opt in:

```bash
cat > .git/hooks/pre-commit <<'SH'
#!/usr/bin/env bash
set -euo pipefail
./scripts/verify.sh
SH
chmod +x .git/hooks/pre-commit
```

This runs repository-only checks, not the full local audit.

## CI

`.github/workflows/validate-toolbox.yml` validates repository content on push/PR and weekly. The
scheduled job also checks public links, non-blocking. CI uses no personal credentials and never
probes a local machine.

## Limitations

- MCP runtime health is **not** tested; executable/package presence only.
- Hooks are inspected statically; none is executed.
- Plugin-injected tools are known only from policy and static config.
- Private-name scanning in CI needs a local `.local-state/private-terms.txt`; CI cannot see it.
- `last_verified` age is a warning signal, not proof of staleness.
