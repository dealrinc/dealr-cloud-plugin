import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        shutil.copytree(REPOSITORY, self.root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('.git', 'dist', 'delivery', '__pycache__'))
        self.data = json.loads((self.root / 'plugin-source.json').read_text())
        for target in ['shared', 'chatgpt']:
            subprocess.run([sys.executable, 'scripts/plugin.py', 'build', '--target', target],
                           cwd=self.root, check=True, capture_output=True)

    def prepare(self, tag=None):
        return subprocess.run([sys.executable, 'scripts/prepare_delivery.py',
                               '--tag', tag or 'v' + self.data['version'], '--commit', 'a' * 40],
                              cwd=self.root, capture_output=True, text=True)

    def test_delivery_contains_verified_platform_artifacts(self):
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads((self.root / 'delivery/manifest.json').read_text())
        self.assertEqual(metadata['commit'], 'a' * 40)
        self.assertEqual({a['target'] for a in metadata['artifacts']}, {'shared', 'chatgpt'})
        sums = (self.root / 'delivery/SHA256SUMS').read_text()
        for artifact in metadata['artifacts']:
            payload = (self.root / 'delivery' / artifact['file']).read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            self.assertEqual(digest, artifact['sha256'])
            self.assertIn(f"{digest}  {artifact['file']}\n", sums)
        self.assertNotEqual(self.prepare().returncode, 0)

    def test_wrong_tag_cannot_prepare_a_delivery(self):
        result = self.prepare('v0.0.0')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'delivery').exists())

    def test_tampered_archive_is_rejected_before_staging(self):
        archive = next((self.root / 'dist/shared').glob('*.zip'))
        archive.write_bytes(archive.read_bytes() + b'changed')
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Checksum mismatch', result.stderr)
        self.assertFalse((self.root / 'delivery').exists())

    def test_wrong_package_with_a_fresh_checksum_is_rejected(self):
        archive = next((self.root / 'dist/shared').glob('*.zip'))
        with zipfile.ZipFile(archive) as bundle:
            files = {name: bundle.read(name) for name in bundle.namelist()}
        manifest = json.loads(files['.claude-plugin/plugin.json'])
        manifest['version'] = '0.0.0'
        files['.claude-plugin/plugin.json'] = json.dumps(manifest).encode()
        with zipfile.ZipFile(archive, 'w') as bundle:
            for name, content in files.items():
                bundle.writestr(name, content)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (archive.parent / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Wrong metadata', result.stderr)
        self.assertFalse((self.root / 'delivery').exists())


if __name__ == '__main__':
    unittest.main()
