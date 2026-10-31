import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location('version_gate', Path(__file__).resolve().parents[1] / 'scripts/version_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class VersionGateTests(unittest.TestCase):
    def test_version_bump_selects_a_delivery(self):
        self.assertEqual(gate.decide('1.1.0', '1.0.0', False), ('v1.1.0', True))

    def test_first_package_can_be_delivered(self):
        self.assertEqual(gate.decide('1.1.0', None, False), ('v1.1.0', True))

    def test_ordinary_commit_skips_even_when_tag_exists(self):
        self.assertEqual(gate.decide('1.1.0', '1.1.0', True), ('v1.1.0', False))

    def test_version_cannot_go_backwards(self):
        with self.assertRaisesRegex(ValueError, 'increase'):
            gate.decide('1.0.0', '1.1.0', False)

    def test_new_delivery_cannot_reuse_a_tag(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            gate.decide('1.1.0', '1.0.0', True)

    def test_workflow_output_injection_and_unstable_versions_are_rejected(self):
        for value in ['1.1.0\npublish=true', 'v1.1.0', '1.1.0-beta', '', '../main']:
            with self.subTest(version=value), self.assertRaises(ValueError):
                gate.decide(value, None, False)


if __name__ == '__main__':
    unittest.main()
