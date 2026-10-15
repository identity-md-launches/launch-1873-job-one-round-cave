"""Offline behavioral checks; temporary sources stay under test/scratch."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tested_delta', HERE / 'delta.py')
delta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delta)


class DeltaTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.before = self.root / 'before'
        self.after = self.root / 'after'
        self.before.mkdir()
        self.after.mkdir()
        self.mapper = delta.load_mapper()

    def put(self, root, name, source):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source if isinstance(source, bytes) else source.encode())

    def result(self):
        return delta.compare(self.mapper.inspect(self.before), self.mapper.inspect(self.after))

    def cli(self, *options):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = delta.main([str(self.before), str(self.after), *options])
        return status, output.getvalue(), errors.getvalue()

    def test_cycle_and_edge_creation_then_removal(self):
        for root in (self.before, self.after):
            self.put(root, 'main.py', 'import helper\n')
        self.put(self.before, 'helper.py', '')
        self.put(self.after, 'helper.py', 'import main\n')
        result = self.result()
        self.assertEqual(result['changes']['edges'], {'added': [{'from': 'helper', 'to': 'main'}], 'removed': []})
        self.assertEqual(result['changes']['cycle_groups']['added'], [['helper', 'main']])
        reverse = delta.compare(self.mapper.inspect(self.after), self.mapper.inspect(self.before))
        self.assertEqual(reverse['changes']['edges']['removed'], result['changes']['edges']['added'])
        self.assertEqual(reverse['changes']['cycle_groups']['removed'], [['helper', 'main']])

    def test_modules_entrypoints_and_source_relocation(self):
        self.put(self.before, 'a.py', "if __name__ == '__main__': pass\n")
        self.put(self.before, 'gone.py', '')
        self.put(self.after, 'a/__init__.py', '')
        self.put(self.after, 'new.py', "if '__main__' == __name__: pass\n")
        changes = self.result()['changes']
        self.assertEqual(changes['modules'], {'added': ['new'], 'removed': ['gone']})
        self.assertEqual(changes['entrypoints'], {'added': ['new'], 'removed': ['a']})
        self.assertEqual(changes['source_paths'], [{'module': 'a', 'before': 'a.py', 'after': 'a/__init__.py'}])

    def test_nonstructural_changes_and_inert_source(self):
        trap = "raise AssertionError('inspected source was executed')\n"
        self.put(self.before, 'a.py', trap + 'VALUE = 1\nimport json\n')
        self.put(self.after, 'a.py', trap + '# comment\nVALUE = 2\nimport csv\n')
        result = self.result()
        self.assertFalse(result['has_changes'])
        self.assertFalse(result['has_warnings'])
        self.assertEqual(self.cli('--check', '--strict')[0], 0)

    def test_parse_and_dynamic_warnings_survive_identical_graph(self):
        for root in (self.before, self.after):
            self.put(root, 'broken.py', 'if :\n')
            self.put(root, 'dynamic.py', "__import__('unknown')\n")
        result = self.result()
        self.assertFalse(result['has_changes'])
        self.assertTrue(result['has_warnings'])
        for side in ('before', 'after'):
            self.assertEqual(result['scans'][side]['issues'][0]['type'], 'parse_error')
            self.assertEqual(result['scans'][side]['dynamic_imports'][0]['module'], 'dynamic')
        self.assertEqual(self.cli('--check')[0], 0)
        self.assertEqual(self.cli('--strict')[0], 1)

    def test_parse_failure_does_not_hide_warning_behind_edge_removal(self):
        for root in (self.before, self.after):
            self.put(root, 'b.py', '')
        self.put(self.before, 'a.py', 'import b\n')
        self.put(self.after, 'a.py', 'import b\nif :\n')
        result = self.result()
        self.assertEqual(result['changes']['edges']['removed'], [{'from': 'a', 'to': 'b'}])
        self.assertTrue(result['has_warnings'])
        self.assertEqual(result['scans']['after']['issues'][0]['type'], 'parse_error')

    def test_cli_determinism_and_statuses(self):
        self.put(self.after, 'new.py', '')
        code, output, errors = self.cli('--json')
        self.assertEqual((code, errors), (0, ''))
        self.assertEqual(output, self.cli('--json')[1])
        self.assertEqual(json.loads(output), self.result())
        self.assertEqual(self.cli('--check')[0], 1)
        self.assertEqual(self.cli('--strict')[0], 0)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(delta.main([str(self.root / 'absent'), str(self.before)]), 2)

    def test_reject_outside_root_without_reading_it(self):
        with self.assertRaisesRegex(ValueError, 'inside the current workspace'):
            delta.scan(self.mapper, Path('/outside-workspace-not-opened'), Path.cwd().resolve())

    def test_encoding_namespace_and_relative_imports(self):
        for root in (self.before, self.after):
            self.put(root, 'ns/a.py', b'\xef\xbb\xbffrom . import b\n')
            self.put(root, 'ns/b.py', b'# coding: latin-1\nLABEL="caf\xe9"\n')
        self.put(self.after, 'ns/b.py', 'from . import a\n')
        result = self.result()
        self.assertFalse(result['has_warnings'])
        self.assertEqual(result['changes']['edges']['added'], [{'from': 'ns.b', 'to': 'ns.a'}])
        self.assertEqual(result['changes']['cycle_groups']['added'], [['ns.a', 'ns.b']])

    def test_cycle_group_merge_is_reported_as_groups(self):
        before = {'modules': [], 'edges': [], 'cycles': [['a', 'b'], ['c', 'd']], 'issues': [],
                  'summary': {'entrypoints': []}}
        after = dict(before, cycles=[['a', 'b', 'c', 'd']])
        change = delta.compare(before, after)['changes']['cycle_groups']
        self.assertEqual(change['removed'], [['a', 'b'], ['c', 'd']])
        self.assertEqual(change['added'], [['a', 'b', 'c', 'd']])


if __name__ == '__main__':
    unittest.main()
