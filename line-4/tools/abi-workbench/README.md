# ABI Workbench

A Python standard-library CLI that computes Ethereum selectors with Keccak-256,
encodes unsigned function calldata, and decodes supplied return bytes offline.
It never connects to RPC, signs, sends, pays, or reads keys or environment values.
ABI paths are explicit inputs; keep them inside your workspace.

## Run it

From the repository root:

```sh
python3 -B -m unittest discover -s line-4/tools/abi-workbench -v
```

This runs 36 regression tests, including the gathering's defect reports,
all 32 integer widths, malformed output checks, and eight Keccak vectors
independently obtained using `cast keccak` (Cast is not needed to run the tests).
All 27 passed locally, including 11 input-boundary tests and four scalar-array
tests. The original demo also passed:

```sh
python3 -B line-4/tools/abi-workbench/abi_workbench.py --demo
```

The demo's transfer **argument** is the real ZTO address; it is only a formatting
example, not a destination envelope or an executed token transfer. Its amount is
illustrative, not a balance or price. It prints `0xa9059cbb` and complete calldata.

Pepe 24 added one-dimensional arrays of static scalar types, both fixed
(`uint8[2]`) and dynamic (`uint8[]`). The included `array-example.json`
reproduces the published Solidity ABI example without connecting to a chain:

```sh
python3 -B line-4/tools/abi-workbench/abi_workbench.py encode --abi line-4/tools/abi-workbench/array-example.json --function f --args '[291,[1110,1929],"0x31323334353637383930","0x48656c6c6f2c20776f726c6421"]'
```

Tried locally: this prints selector `0x8be65246` and the calldata bytes from
the [Solidity ABI specification](https://docs.soliditylang.org/en/latest/abi-spec.html#use-of-dynamic-types).
The new tests also check a fixed array followed by a dynamic array using ZTO
and IMD addresses, empty arrays, invalid counts, truncated return arrays, and
invalid element words. The output of `decode` represents arrays as JSON arrays.

An included ABI exercises canonical alias handling:

```sh
python3 -B line-4/tools/abi-workbench/abi_workbench.py encode --abi line-4/tools/abi-workbench/alias-example.json --function transfer --args '["0xd782bdea4ef02a0bd391eb9089470c8080f0a68e",12]'
```

For your ABI use `encode --abi PATH --function NAME --args '[...]'`, or
`decode --abi PATH --function NAME --data 0x...`. Run from your workspace root; resolved ABI paths must stay inside that directory.
ABI files are UTF-8 JSON arrays of entry objects (a UTF-8 BOM is accepted). Integer inputs must be exact JSON integers or decimal strings
(e.g. `"1000000000000000000"`); floats, booleans, exponent strings and whitespace
are rejected. JSON numeric exponents parse as floats and are rejected too.

## Supported scope and repairs

Supports `address`, `bool`, `int`/`uint` (canonicalized to 256 bits), widths
8 through 256 in steps of 8, `bytes1` through `bytes32`, `string`, and `bytes`.
One-dimensional fixed and dynamic arrays of `address`, `bool`, `int`/`uint`
and fixed bytes are supported, with a 4,096-item maximum. Fixed arrays occupy
their full number of head words; dynamic arrays use a length-prefixed tail.
The new repair combines Keccak's padding bits at the 135-byte boundary, avoids
lossy integer conversion, canonicalizes aliases before selector hashing, and
rejects signed words with invalid sign extension. Additional checks reject
nonzero address/bytes padding, dynamic offsets into the head, missing tail
padding, and nonzero dynamic padding. Direct `encode_value` calls now use the
same type validation as the CLI.

Tuples, nested arrays, arrays of `string` or dynamic `bytes`, events, fixed
point and ambiguous overloaded names are explicitly unsupported. The default decoder permits noncanonical tail layouts and surplus words for
compatibility. Use `decode --strict` to require exact canonical re-encoding for
the supported types; unsupported ABI types remain unsupported. ABI files are limited to 1 MiB before parsing. Argument JSON and return bytes
are still held in memory without a total size budget. This is a
local byte interpreter, not proof of an on-chain value or transaction success.
The tests are regressions, not an independent audit or full ABI conformance suite.

## Checked inputs (Pepe 23)

The gathering's malformed-object ABI and missing-file reproductions now return
exit 2 with a concise `error:` on stderr and no success output or traceback.
The reader checks the ABI container, entry kinds/names, input/output arrays,
parameter objects, type strings and optional parameter names. Unsupported types
in the selected function's inputs and outputs fail explicitly; unrelated valid
entries can contain types the workbench does not implement. This is structural
validation for this interpreter, not complete Solidity ABI schema validation.

Malformed JSON/UTF-8, duplicate JSON fields, excessive JSON nesting and files
over 1 MiB are rejected. File I/O failures are handled at the CLI boundary.
Paths outside the current workspace, including resolved symlinks, are rejected
before opening. This path check is for trusted local CLI use, not isolation
against concurrent malicious filesystem changes or special files.

At Pepe 23, 23 tests passed; the demo and alias `transfer` example still
produce selector `0xa9059cbb`. Real CLI calls with an object-shaped ABI and a
missing ABI both produced exit 2 and one error line. No RPC was needed for this
repair, and no signing or transaction submission capability was added. Pepe 24's
array extension brings the passing total to 27.


## Strict return decoding (Pepe 25)

Add `--strict` when interpreting bytes from an untrusted source. After normal
value and padding checks, the decoder encodes the decoded values again and
requires byte-for-byte equality. This rejects shared or overlapping dynamic
tails, reordered tails, gaps and unused suffix words. Empty outputs require
empty bytes. The Python API is `decode_tuple(params, data, strict=True)`; the
existing two-argument API and default CLI behavior stay compatible.

One command anyone can run from the repository root:

```sh
python3 -B line-4/tools/abi-workbench/abi_workbench.py decode --abi line-4/tools/abi-workbench/alias-example.json --function transfer --strict --data 0x0000000000000000000000000000000000000000000000000000000000000001
```

Tried locally: exits 0 and prints the boolean output `ok: true`. This is an
offline return-byte fixture, not a transfer, receipt or on-chain observation.
Appending another 32-byte word exits 2 with `error: noncanonical return data`
and no success output. The complete suite passes 36 tests, including nine new
strict-mode regressions with independently laid-out ABI words. They cover mixed
fixed arrays, ZTO's real address, signed values, strings, dynamic arrays, empty
values, padding and CLI success/error behavior.

Strict decoding validates byte layout for the supported type subset; it does
not authenticate the source of those bytes. It holds decoded values and a
second encoded copy in memory. Existing argument/return input size limits are
unchanged; do not feed unbounded data to this local CLI.
