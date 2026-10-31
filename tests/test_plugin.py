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
                     ".mcp.json", "mcp.json", "skills", "assets", "docs"):
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
            archive = self.root / "dist" / f"{data['name']}-{data['version']}.zip"
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


if __name__ == "__main__":
    unittest.main()
