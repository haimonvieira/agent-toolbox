# Testing Patterns

## 1) Test Stack and Commands

- Primary test framework: Python `unittest` (stdlib); CI specifies Python 3.12.
- Assertion/mocking tools: `unittest.TestCase` assertions and lightweight monkeypatching of module functions; no separate mocking library is declared.
- Commands:

```bash
python -m unittest discover -s tests -v
./scripts/verify.sh
bash -n scripts/*.sh
```

No separate unit/integration/e2e or coverage commands are declared. Evidence: `.github/workflows/validate-toolbox.yml`.

## 2) Test Layout

- Test files live in `tests/` and use `test_*.py` names.
- Test modules import scripts by adding `scripts/` to `sys.path`.
- Setup files: [TODO] no global unittest setup file identified.
- Representative coverage targets include path normalization, credential redaction, skill tree hashing, drift findings, profile schema/reference evaluation, inheritance, and reproducibility. Evidence: `tests/test_audit.py`, `tests/test_profiles.py`.

## 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|---|---|---|---|
| Unit | Yes | Audit utilities and profile engine | Uses synthetic objects and temporary directories |
| Integration | Partial | Repository profile/schema validation | Runs against files in this repository |
| E2E | No evidence | Full agent/tool runtime workflows | Third-party MCPs/plugins/hooks are intentionally not run |

## 4) Mocking and Isolation Strategy

- Main approach: temporary directories for filesystem cases and direct replacement of selected functions such as `shutil.which`; synthetic catalog/state fixtures for profile tests.
- Isolation guarantees: test data is generally temporary or in-memory; repository validation reads actual repository files. Evidence: `tests/test_audit.py`, `tests/test_profiles.py`.
- Common failure mode: [TODO] no historical flaky/failure catalog found.

## 5) Coverage and Quality Signals

- Coverage tool + threshold: [TODO] none configured.
- Current reported coverage: [TODO] no coverage report found.
- CI also validates generated profile artifacts are up-to-date and checks shell syntax. Evidence: `.github/workflows/validate-toolbox.yml`.
- Runtime integration checks for harnesses/MCPs are outside the test suite by design, as described in `docs/security.md`.

## 6) Evidence

- `tests/test_audit.py`
- `tests/test_profiles.py`
- `.github/workflows/validate-toolbox.yml`
- `scripts/verify.sh`
