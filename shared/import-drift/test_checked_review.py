"""Behavioral checks for the key-audit to comparison handoff."""
import contextlib
import csv
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import tempfile
import unittest

import checked_review as tool


class CheckedReviewTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def save(self, name, text):
        path = self.root / name
        path.write_text(text, encoding='utf-8')
        return path

    def test_real_token_snapshot_is_ready_and_exact(self):
        path = Path('shared/token-read-plan/observed.csv')
        result = tool.compare(path, path, ['chain_id', 'token_address', 'field'])
        self.assertTrue(result['ready'])
        self.assertEqual(result['comparison']['summary']['unchanged_on_common_columns'], 6)

    def test_duplicate_empty_and_header_only_block_comparison(self):
        a = self.save('a.csv', 'id,v\na,1\n')
        for content, issue in [('id,v\na,1\na,1\n', 'duplicate_key'),
                               ('id,v\n,1\n', 'empty_key_component'),
                               ('id,v\n', 'no_data_records')]:
            with self.subTest(issue=issue):
                b = self.save('b.csv', content)
                result = tool.compare(a, b, ['id'])
                self.assertFalse(result['ready'])
                self.assertIsNone(result['comparison'])
                self.assertIn(issue, result['key_audit']['datasets'][1]['issues'])

    def test_composite_keys_and_exact_change(self):
        a = self.save('a.csv', 'id,part,v\nx,a,01\nx,b,2\n')
        b = self.save('b.csv', 'part,v,id\nb,2,x\na,1,x\n')
        result = tool.compare(a, b, ['id', 'part'])
        self.assertTrue(result['ready'])
        self.assertEqual(result['comparison']['changed'][0]['fields']['v'], {'before': '01', 'after': '1'})
        self.assertFalse(tool.compare(a, b, ['id'])['ready'])

    def test_ignore_block_keeps_exact_base_units(self):
        a = self.save('a.csv', 'id,raw_value,block\nzto,1000000000000000001,1\n')
        b = self.save('b.csv', 'id,raw_value,block\nzto,1000000000000000002,2\n')
        result = tool.compare(a, b, ['id'], ['block'])
        fields = result['comparison']['changed'][0]['fields']
        self.assertEqual(fields, {'raw_value': {'before': '1000000000000000001', 'after': '1000000000000000002'}})

    def test_html_inert_for_both_ready_and_blocked_inputs(self):
        payload = '</pre><script>alert(1)</script>'
        a = self.save('a.csv', 'id,v\n' + payload + ',1\n')
        b = self.save('b.csv', 'id,v\n' + payload + ',2\n')
        class Tags(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = []
            def handle_starttag(self, tag, attrs):
                self.tags.append(tag)
        for candidate in (b, self.save('duplicate.csv', a.read_text() + payload + ',1\n')):
            document = tool.render_html(tool.compare(a, candidate, ['id']))
            parsed = Tags()
            parsed.feed(document)
            self.assertNotIn('script', parsed.tags)
            self.assertIn('Content-Security-Policy', document)
            self.assertIn('Key readiness:', document)
            self.assertIn('&lt;/pre&gt;&lt;script&gt;', document)

    def test_cli_statuses_and_no_partial_output_on_bad_input(self):
        a = self.save('a.csv', 'id,v\na,1\n')
        for text, code in [('id,v\na,1\n', 0), ('id,v\na,2\n', 1),
                           ('id,v\na,1\na,1\n', 1), ('id,v\na\n', 2)]:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(tool.main([str(a), str(self.save('b.csv', text)), '--key', 'id']), code)
            if code == 2:
                self.assertEqual(out.getvalue(), '')
                self.assertIn('error', json.loads(err.getvalue()))
            else:
                self.assertEqual(err.getvalue(), '')
                self.assertEqual(json.loads(out.getvalue())['schema'], 'checked-csv-review/v1')

    def test_outside_input_rejected(self):
        a = self.save('a.csv', 'id\na\n')
        with self.assertRaisesRegex(ValueError, 'inside the current working directory'):
            tool.compare(a, Path.cwd().parent / 'not-opened.csv', ['id'])


if __name__ == '__main__':
    unittest.main()
