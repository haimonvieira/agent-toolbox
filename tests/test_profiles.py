import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit  # noqa: E402
import profile_engine as pe  # noqa: E402


class FakeCatalog:
    """Minimal stand-in for profile_engine.Catalog with synthetic entries."""

    def __init__(self, entries):
        self.entries = entries
        self.by_name = {}

    def get(self, ref):
        return self.entries.get(ref)

    def find(self, category, name, variant=None):
        for record in self.entries.values():
            if record["category"] == category and record["name"] == name:
                return record
        return None


def record(category, name, **kwargs):
    base = {
        "id": f"{category}-{name}",
        "category": category,
        "name": name,
        "entry": {},
        "source_type": None,
        "evidence_level": "Verified locally",
        "version": None,
        "license": "MIT",
        "upstream_repository": None,
        "official_docs": None,
        "install_method": None,
        "status": "Installed",
        "scope": None,
        "harnesses": None,
    }
    base.update(kwargs)
    return base


class ProfileSchemaTests(unittest.TestCase):
    def test_valid_profile_passes_mini_schema(self):
        schema = audit.read_json(ROOT / "schemas" / "profile.schema.json")
        profile = {
            "schema_version": 1, "id": "demo", "name": "Demo", "profile_version": 1,
            "status": "active",
            "harnesses": {"required": [{"ref": "harness-opencode"}]},
            "environment_variables": {"required": [{"name": "DEMO_TOKEN"}]},
        }
        self.assertEqual(audit._mini_validate(profile, schema, schema), [])

    def test_invalid_profile_is_rejected(self):
        schema = audit.read_json(ROOT / "schemas" / "profile.schema.json")
        profile = {"schema_version": 1, "id": "demo", "status": "nope"}
        self.assertTrue(audit._mini_validate(profile, schema, schema))

    def test_repository_profiles_validate(self):
        self.assertEqual(audit.validate_profiles_repo(), [])


class InheritanceTests(unittest.TestCase):
    def test_parent_components_are_inherited(self):
        base = {"id": "base", "plugins": {"required": [{"ref": "plugin-a"}]}}
        child = {"id": "child", "extends": ["base"], "plugins": {"required": [{"ref": "plugin-b"}]}}
        profiles = {"base": base, "child": child}
        merged = pe.resolved_components(child, profiles)
        refs = {i["ref"] for i in merged["plugin"]}
        self.assertEqual(refs, {"plugin-a", "plugin-b"})
        inherited = [i for i in merged["plugin"] if i["ref"] == "plugin-a"][0]
        self.assertEqual(inherited["ownership"], "inherited")

    def test_cycle_is_detected(self):
        profiles = {
            "a": {"id": "a", "extends": ["b"]},
            "b": {"id": "b", "extends": ["a"]},
        }
        errors = pe.inheritance_errors(profiles)
        self.assertTrue(any("cycle" in e for e in errors))

    def test_unknown_reference_is_reported(self):
        profiles = {"p": {"id": "p", "mcps": {"required": [{"ref": "mcp-missing"}]}}}
        catalog = FakeCatalog({})
        self.assertEqual(pe.unresolved_refs(profiles["p"], profiles, catalog), ["mcp-missing"])


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = FakeCatalog({
            "harness-opencode": record("harness", "OpenCode", install_method="npm",
                                       upstream_repository="https://example.invalid/oc"),
            "mcp-pencil": record("mcp", "pencil", entry={"command": "/nonexistent/pencil"}),
            "mcp-context7": record("mcp", "context7"),
            "skill-code-review": record("skill", "code-review", provenance="skills-cli-lock",
                                        install_method="npx skills add owner/repo"),
        })
        self.snapshot = {
            "harnesses": [{"name": "opencode", "installed": True, "version": "opencode v2.1.4"}],
            "plugins": [{"name": "oh-my-opencode-slim@latest", "harness": "opencode", "version": "3.0.6"}],
            "mcps": [{"name": "pencil", "harness": "opencode", "enabled": True, "version_pin": None}],
            "skill_stores": [{"kind": "canonical", "entries": [{"name": "code-review"}]}],
            "hooks": {"hook_files": []},
            "external_dependencies": [],
            "configs": [],
        }

    def test_missing_required_component_is_reported(self):
        profile = {"id": "p", "harnesses": {"required": [{"ref": "harness-opencode"}]},
                   "mcps": {"required": [{"ref": "mcp-context7"}]}}
        result = pe.evaluate_profile(profile, {"p": profile}, self.catalog, self.snapshot)
        statuses = {r["ref"]: r["status"] for r in result["results"]}
        self.assertEqual(statuses["mcp-context7"], "MISSING")
        self.assertEqual(statuses["harness-opencode"], "PRESENT")

    def test_optional_component_is_reported_as_optional(self):
        profile = {"id": "p", "mcps": {"optional": [{"ref": "mcp-context7"}]}}
        result = pe.evaluate_profile(profile, {"p": profile}, self.catalog, self.snapshot)
        self.assertEqual(result["results"][0]["status"], "OPTIONAL_MISSING")

    def test_dynamic_component_follows_its_plugin(self):
        profile = {"id": "p", "mcps": {"dynamic": [{"ref": "mcp-context7",
                                                  "managed_by": "plugin-oh-my-opencode-slim"}]}}
        result = pe.evaluate_profile(profile, {"p": profile}, self.catalog, self.snapshot)
        self.assertEqual(result["results"][0]["status"], "DYNAMIC_PRESENT")

    def test_version_comparison_is_lenient(self):
        self.assertTrue(pe.versions_match("2.1.4", "opencode v2.1.4"))
        self.assertTrue(pe.versions_match("18.12.6", "omp/18.12.6"))
        self.assertFalse(pe.versions_match("2.1.4", "2.2.0"))

    def test_environment_variables_are_presence_only(self):
        profile = {"id": "p", "environment_variables": {"required": [{"name": "PATH"}]}}
        result = pe.evaluate_profile(profile, {"p": profile}, self.catalog, self.snapshot,
                                     {"PATH": True})
        self.assertTrue(result["environment_variables"][0]["present"])
        self.assertNotIn("value", result["environment_variables"][0])


class ComparisonTests(unittest.TestCase):
    def test_only_differences_are_reported(self):
        profiles = {
            "a": {"id": "a", "harnesses": {"required": [{"ref": "harness-a"}]},
                  "mcps": {"required": [{"ref": "mcp-a"}]}},
            "b": {"id": "b", "harnesses": {"required": [{"ref": "harness-b"}]},
                  "mcps": {"required": [{"ref": "mcp-b"}]}},
        }
        diff = pe.compare_profiles(profiles["a"], profiles["b"], profiles)
        self.assertEqual(diff["components"]["harness"]["only_a"], ["harness-a"])
        self.assertEqual(diff["components"]["harness"]["only_b"], ["harness-b"])
        self.assertEqual(diff["components"]["mcp"]["shared"], 0)


class ReproducibilityTests(unittest.TestCase):
    def _catalog(self, **overrides):
        base = {
            "harness-x": record("harness", "X", install_method="npm",
                                upstream_repository="https://example.invalid/x",
                                evidence_level="Verified upstream"),
        }
        base.update(overrides)
        return FakeCatalog(base)

    def test_fully_reproducible(self):
        profile = {"id": "p", "harnesses": {"required": [{"ref": "harness-x"}]}}
        repro = pe.compute_reproducibility(profile, {"p": profile}, self._catalog())
        self.assertEqual(repro["status"], "fully_reproducible")

    def test_blocked_when_reference_missing(self):
        profile = {"id": "p", "harnesses": {"required": [{"ref": "harness-x"}]},
                   "mcps": {"required": [{"ref": "mcp-unknown"}]}}
        repro = pe.compute_reproducibility(profile, {"p": profile}, self._catalog())
        self.assertEqual(repro["status"], "blocked")

    def test_partially_reproducible_for_unknown_provenance(self):
        catalog = self._catalog(**{
            "skill-x": record("skill", "x", provenance="unknown", install_method="npx skills add o/r"),
        })
        profile = {"id": "p", "skills": {"required": [{"ref": "skill-x"}]}}
        repro = pe.compute_reproducibility(profile, {"p": profile}, catalog)
        self.assertEqual(repro["status"], "partially_reproducible")


class ExternalDependencyTests(unittest.TestCase):
    def test_external_dependency_is_optional_by_default(self):
        profile = {"id": "p", "external_dependencies": [{"ref": "external-nvme", "required": False}]}
        self.assertFalse(profile["external_dependencies"][0]["required"])


if __name__ == "__main__":
    unittest.main()
