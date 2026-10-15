"""Independent word-level malformed layouts for canonical return validation."""
import contextlib
import io
import json
import unittest
from unittest.mock import patch

import abi_workbench as abi


def w(n):
    return n.to_bytes(32, 'big')


def params(*types):
    return [{'type': t} for t in types]


class StrictDecodeTests(unittest.TestCase):
    def reject_noncanonical(self, types, data):
        # Compatibility decoding still permits the historically accepted layout.
        abi.decode_tuple(params(*types), data)
        with self.assertRaisesRegex(ValueError, 'noncanonical return data'):
            abi.decode_tuple(params(*types), data, strict=True)

    def test_shared_tail(self):
        self.reject_noncanonical(('bytes', 'bytes'), w(64) + w(64) + w(1) + b'a'.ljust(32, b'\0'))

    def test_reordered_tails(self):
        self.reject_noncanonical(('bytes', 'bytes'), w(128) + w(64) + w(1) + b'b'.ljust(32, b'\0') + w(1) + b'a'.ljust(32, b'\0'))

    def test_gap_before_tail(self):
        self.reject_noncanonical(('bytes',), w(64) + w(0) + w(0))

    def test_surplus_words(self):
        for types, data in [(('uint256',), w(7) + w(0)),
                            (('bytes',), w(32) + w(0) + w(0)),
                            ((), w(0))]:
            with self.subTest(types=types):
                self.reject_noncanonical(types, data)

    def test_overlapping_array_tails(self):
        # The second array's length aliases the first array's sole element.
        self.reject_noncanonical(('uint8[]', 'uint8[]'), w(64) + w(96) + w(1) + w(0))

    def test_canonical_mixed_layout(self):
        # A fixed array expands the head. Independent literal offsets are 160,224.
        p = params('int8[2]', 'address', 'string', 'bool[]')
        zto = '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'
        data = w((1 << 256)-1) + w(2) + bytes.fromhex(zto[2:]).rjust(32, b'\0') + w(160) + w(224) + w(3) + b'ZTO'.ljust(32, b'\0') + w(2) + w(1) + w(0)
        self.assertEqual([x['value'] for x in abi.decode_tuple(p, data, strict=True)],
                         [[-1, 2], zto, 'ZTO', [True, False]])

    def test_canonical_empty_values(self):
        self.assertEqual(abi.decode_tuple([], b'', strict=True), [])
        p = params('string', 'bytes', 'uint8[]')
        data = w(96) + w(128) + w(160) + w(0) + w(0) + w(0)
        self.assertEqual([x['value'] for x in abi.decode_tuple(p, data, strict=True)], ['', '0x', []])

    def test_bad_padding_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'padding'):
            abi.decode_tuple(params('bytes'), w(32) + w(1) + b'a' + b'\0'*30 + b'X', strict=True)

    def test_cli_success_and_failure(self):
        raw = b'[{"type":"function","name":"totalSupply","outputs":[{"type":"uint256"}]}]'
        for data, expected in [(w(7), 0), (w(7) + w(0), 2)]:
            out, err = io.StringIO(), io.StringIO()
            with patch.object(abi.Path, 'open', return_value=io.BytesIO(raw)), \
                 patch('sys.argv', ['abi_workbench', 'decode', '--abi', 'fixture.json', '--function', 'totalSupply', '--data', '0x'+data.hex(), '--strict']), \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(abi.main(), expected)
            if expected == 0:
                self.assertEqual(json.loads(out.getvalue())['outputs'][0]['value'], 7)
                self.assertEqual(err.getvalue(), '')
            else:
                self.assertEqual(out.getvalue(), '')
                self.assertTrue(err.getvalue().startswith('error: noncanonical return data'))


if __name__ == '__main__':
    unittest.main()
