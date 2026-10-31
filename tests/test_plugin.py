import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("plugin", REPOSITORY / "scripts/plugin.py")
plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        for name in ("plugin-source.json", "README.md", "LICENSE", ".claude-plugin", ".cursor-plugin",
                     ".mcp.json", "mcp.json", "skills", "assets", "docs", "exports"):
            source = REPOSITORY / name
            if source.is_dir():
                shutil.copytree(source, self.root / name)
            else:
                shutil.copy2(source, self.root / name)
        self.previous_root = plugin.ROOT
        plugin.ROOT = self.root
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(setattr, plugin, "ROOT", self.previous_root)

    def test_host_drift_fails_check(self):
        path = self.root / ".cursor-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["version"] = "0.0.0"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "stale"):
            plugin.check(plugin.source())

    def test_remote_connection_cannot_embed_credentials(self):
        data = json.loads((self.root / "plugin-source.json").read_text())
        data["servers"]["dealr"]["headers"] = {"Authorization": "Bearer test-value"}
        (self.root / "plugin-source.json").write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "only type and url"):
            plugin.source()

    def test_endpoint_rejects_credentials_queries_and_invalid_hosts(self):
        original = json.loads((self.root / "plugin-source.json").read_text())
        for url in ["https://user:password@example.com/mcp", "https://user@example.com/mcp",
                    "https://example.com/mcp?token=secret", "https://example.com/mcp#secret",
                    "https://", "http://example.com/mcp", "https://example.com:invalid/mcp"]:
            with self.subTest(url=url):
                data = json.loads(json.dumps(original))
                data["servers"]["dealr"]["url"] = url
                (self.root / "plugin-source.json").write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    plugin.source()

    def test_symlinked_skill_directory_fails_before_archiving(self):
        shutil.move(self.root / "skills/get-started", self.root / "skill-backup")
        (self.root / "skills/get-started").symlink_to(self.root / "skill-backup", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            plugin.build(plugin.source())
        self.assertFalse((self.root / "dist").exists())

    def test_symlinked_bundle_root_is_rejected(self):
        shutil.move(self.root / "skills", self.root / "skills-backup")
        (self.root / "skills").symlink_to(self.root / "skills-backup", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            plugin.build(plugin.source())

    def test_missing_asset_fails_check(self):
        (self.root / "assets/logo.png").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            plugin.source()

    def test_build_is_repeatable_and_excludes_development_files(self):
        (self.root / ".env").write_text("NOT_FOR_DISTRIBUTION=test\n")
        (self.root / ".git").mkdir()
        (self.root / ".git/config").write_text("private git config\n")
        data = plugin.source()
        with contextlib.redirect_stdout(io.StringIO()):
            plugin.build(data)
            archive = self.root / "dist/shared" / f"{data['name']}-{data['version']}.zip"
            first = archive.read_bytes()
            plugin.build(data)
        self.assertEqual(first, archive.read_bytes())
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
            self.assertIn(".claude-plugin/plugin.json", names)
            self.assertIn(".cursor-plugin/plugin.json", names)
            self.assertEqual(json.loads(bundle.read(".mcp.json")), json.loads(bundle.read("mcp.json")))
            self.assertNotIn(".env", names)
            self.assertNotIn(".git/config", names)
            self.assertFalse(any(name.startswith(("scripts/", ".github/")) for name in names))
            self.assertFalse(any(name.endswith("marketplace.json") for name in names))

    def test_bundle_refuses_symlinked_content(self):
        target = self.root / "docs/linked.md"
        target.symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            plugin.check(plugin.source())

    def test_chatgpt_export_preserves_existing_identity_connection_and_review(self):
        data = plugin.source()
        baseline = json.loads((self.root / data["openai"]["baseline"]).read_text())
        before = (self.root / "mcp.json").read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            plugin.build(data, "chatgpt")
        archive = self.root / "dist/chatgpt" / f"{baseline['manifest']['name']}-{data['version']}.zip"
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
            manifest = json.loads(bundle.read(".codex-plugin/plugin.json"))
            connection = json.loads(bundle.read(manifest["mcpServers"].removeprefix("./")))
            self.assertEqual(connection, baseline["mcp"])
            self.assertEqual(manifest["name"], baseline["manifest"]["name"])
            self.assertEqual(manifest["version"], data["version"])
            self.assertEqual(manifest["interface"], baseline["manifest"]["interface"])
            self.assertEqual(manifest["author"], baseline["manifest"]["author"])
            ext = manifest["extensions"]["com.openai"]
            previous = baseline["manifest"]["extensions"]["com.openai"]
            self.assertEqual(ext["review"], previous["review"])
            self.assertEqual(ext["publication"]["countries"], previous["publication"]["countries"])
            self.assertEqual(ext["publication"]["release_notes"], data["openai"]["updateNotes"])
            self.assertEqual(bundle.read("assets/icon.png"), (self.root / data["openai"]["asset"]).read_bytes())
            self.assertIn("skills/accounting-fundamentals/references/guide.md", names)
            self.assertIn("skills/bank-reconciliation/references/guide.md", names)
            self.assertIn(manifest["interface"]["logo"].removeprefix("./"), names)
            self.assertIn(manifest["extensions"]["com.openai"]["onboardingSkill"].removeprefix("./"), names)
            self.assertNotIn("mcp.json", names)
            self.assertNotIn(".claude-plugin/plugin.json", names)
            self.assertNotIn(".cursor-plugin/plugin.json", names)
            self.assertFalse(any(name.startswith("docs/") for name in names))
        self.assertEqual(before, (self.root / "mcp.json").read_bytes())

    def test_chatgpt_export_rejects_invalid_listing_and_missing_onboarding(self):
        path = self.root / plugin.source()["openai"]["baseline"]
        original = path.read_text()
        for change in [{"shortDescription": "x" * 31}, {"onboardingSkill": "./README.md"}]:
            with self.subTest(change=change):
                data = plugin.source()
                baseline = json.loads(original)
                if "shortDescription" in change:
                    baseline["manifest"]["interface"].update(change)
                else:
                    baseline["manifest"]["extensions"]["com.openai"].update(change)
                path.write_text(json.dumps(baseline))
                with self.assertRaises(ValueError):
                    plugin.chatgpt_metadata(data)

    def test_chatgpt_export_rejects_endpoint_drift(self):
        data = plugin.source()
        data["servers"]["dealr"]["url"] = "https://other.example.com/mcp"
        with self.assertRaisesRegex(ValueError, "endpoints differ"):
            plugin.chatgpt_metadata(data)

    def test_chatgpt_export_rejects_unchanged_version_and_private_credentials(self):
        data = plugin.source()
        path = self.root / data["openai"]["baseline"]
        baseline = json.loads(path.read_text())
        data["version"] = baseline["manifest"]["version"]
        with self.assertRaisesRegex(ValueError, "newer"):
            plugin.chatgpt_metadata(data)
        baseline["manifest"]["extensions"]["com.openai"]["review"]["test_credentials"] = "synthetic-private-value"
        path.write_text(json.dumps(baseline))
        with self.assertRaisesRegex(ValueError, "Private credentials"):
            plugin.chatgpt_metadata(plugin.source())


if __name__ == "__main__":
    unittest.main()
