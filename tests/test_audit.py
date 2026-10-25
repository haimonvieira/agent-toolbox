import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit  # noqa: E402


class PathNormalizationTests(unittest.TestCase):
    def test_home_and_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "alice"
            repo = home / "agent-toolbox"
            self.assertEqual(audit.norm_path(home / ".agents/skills", home, repo), "~/.agents/skills")
            self.assertEqual(audit.norm_path(repo / "docs", home, repo), "<repo-root>/docs")

    def test_external_volume_is_redacted(self):
        value = "/media/alice/Some Volume/project/.agents/skills/x"
        self.assertEqual(audit.norm_path(value), "<external-volume>/<project>")


class CredentialRedactionTests(unittest.TestCase):
    def test_only_field_paths_are_returned(self):
        data = {
            "mcp": {"servers": {"x": {"headers": {"Authorization": "secret-value"}}}},
            "safe": True,
            "api_key": "never-print-me",
        }
        fields = audit.credential_fields(data)
        self.assertIn("api_key", fields)
        self.assertIn("mcp.servers.x.headers.Authorization", fields)
        self.assertNotIn("never-print-me", " ".join(fields))

    def test_secret_categories_are_masked(self):
        line = "token: " + "sk-" + "a" * 20
        self.assertIn("openai-key", audit.secret_categories(line))
        self.assertNotIn("sk-", str(audit.secret_categories(line)))


class FingerprintTests(unittest.TestCase):
    def _make_skill(self, root: Path, content: str = "hello") -> Path:
        skill = root / "demo"
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text(content, encoding="utf-8")
        (skill / "references" / "a.md").write_text("data", encoding="utf-8")
        return skill

    def test_identical_trees_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self._make_skill(Path(tmp) / "a")
            b = self._make_skill(Path(tmp) / "b")
            fa = audit.fingerprint_skill(a)
            fb = audit.fingerprint_skill(b)
            self.assertEqual(fa["tree_hash"], fb["tree_hash"])
            self.assertEqual(fa["file_count"], 2)
            self.assertTrue(fa["top_level_skill_md"])

    def test_content_change_changes_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self._make_skill(Path(tmp) / "a")
            before = audit.fingerprint_skill(a)["tree_hash"]
            (a / "references" / "a.md").write_text("changed", encoding="utf-8")
            after = audit.fingerprint_skill(a)["tree_hash"]
            self.assertNotEqual(before, after)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self._make_skill(Path(tmp) / "target")
            link = Path(tmp) / "link"
            os.symlink(target, link)
            result = audit.fingerprint_skill(link)
            self.assertTrue(result["symlink"])
            self.assertIsNone(result["tree_hash"])
            self.assertTrue(result["target_exists"])


class DriftTests(unittest.TestCase):
    def test_version_changed(self):
        policy = {"severity": {"version_changed": "medium"}}
        findings = audit.compare_named(
            [{"name": "opencode", "version": "1"}],
            [{"name": "opencode", "version": "2"}],
            ["name"], "harness", policy, set(),
        )
        self.assertTrue(any(f["type"] == "VERSION_CHANGED" for f in findings))

    def test_expected_dynamic(self):
        policy = {"severity": {"new": "low"}}
        findings = audit.compare_named(
            [], [{"name": "context7"}], ["name"], "mcp", policy, {"context7"}
        )
        self.assertEqual(findings[0]["type"], "EXPECTED_DYNAMIC")
        self.assertTrue(findings[0]["expected_dynamic"])

    def test_missing_executable(self):
        original = audit.shutil.which
        audit.shutil.which = lambda _: None
        try:
            self.assertEqual(audit.safe_version("definitely-not-installed"), (None, None))
        finally:
            audit.shutil.which = original

    def test_duplicate_names(self):
        dupes = audit.duplicate_names(["a", "b", "a"])
        self.assertEqual(dupes, [("a", 2)])


class StaticFindingTests(unittest.TestCase):
    def test_floating_plugin_and_credential_mode(self):
        state = {
            "mcps": [{"name": "x", "harness": "opencode", "transport": "stdio",
                      "package": "x", "version_pin": None, "enabled": True}],
            "plugins": [{"name": "demo@latest", "harness": "opencode", "version": None}],
            "configs": [{"path": "~/.config/x", "mode": "644", "credential_fields": ["token"]}],
            "external_dependencies": [],
        }
        policy = {"severity": {"floating_version": "medium", "credential_mode": "critical"}}
        found = audit.static_findings(state, policy)
        self.assertTrue(any(f["category"] == "mcp" for f in found))
        self.assertTrue(any(f["category"] == "plugin" for f in found))
        self.assertTrue(any(f["severity"] == "critical" for f in found))


class PrivacyAndSchemaTests(unittest.TestCase):
    def test_absolute_home_path(self):
        bad = "/home/" + "alice" + "/agent"
        text = f"ok ~/x\n{bad}\nplaceholder /home/<user>/x\n"
        self.assertEqual(audit.absolute_home_paths(text), [2])

    def test_schemas_parse(self):
        for name in ("inventory", "snapshot"):
            data = json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
            self.assertIn("$schema", data)
            self.assertIn("properties", data)

    def test_mini_schema_rejects_missing_required(self):
        schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
        self.assertTrue(audit._mini_validate({}, schema, schema))
        self.assertEqual(audit._mini_validate({"name": "ok"}, schema, schema), [])

    def test_actionable_by_severity(self):
        policy = {"exit_on": ["high", "critical"]}
        self.assertTrue(audit.actionable([{"severity": "high"}], policy))
        self.assertFalse(audit.actionable([{"severity": "medium"}], policy))

    def test_package_parsing(self):
        pkg, ver, display = audit.package_from_command(
            ["npx", "-y", "@scope/tool@1.2.3"]
        )
        self.assertEqual((pkg, ver), ("@scope/tool", "1.2.3"))
        self.assertIn("@scope/tool@1.2.3", display)
        self.assertEqual(audit.package_from_command(["codegraph", "serve"])[0], None)


if __name__ == "__main__":
    unittest.main()
