# Token read plan

Turn Line 4's offline ABI workbench into exact CSV snapshots that Line 2 can
reconcile. The tool prepares six read-only `eth_call` requests for Ethereum's
real ZTO token first, then IMD: `symbol()`, `decimals()`, and `totalSupply()`.
It decodes supplied result bytes without floating point, signing, network
access, accounts, installation, or a new coin. Python 3.9+; standard library only.

One command from the repository root shows the actual bundled observation:

```sh
python3 -B shared/token-read-plan/token_read_plan.py demo
```

It prints six CSV rows. At Ethereum block `0x18fc1e6` (26,198,502), the public
RPC returned ZTO / 18 decimals / 1,000,000,000 whole tokens, then IMD / 18
decimals / 4,164,418.598629 whole tokens. These are observed total supplies,
not balances, prices, available liquidity, or current-value claims.
`observed-responses.json` preserves the six raw return values; the sequential
RPC request IDs were normalized to batch IDs 1–6. `observed-provenance.json`
records the endpoint, observation date, chain ID, block and read methods.
`observed.csv` is the exact demo output. The decoder itself makes no RPC calls.

## New read plans and CSV handoffs

Generate a plan pinned to an explicit, canonical hexadecimal block number:

```sh
python3 -B shared/token-read-plan/token_read_plan.py plan --block 0x18fc1e6
```

The output's `requests` array is a JSON-RPC batch, not a transaction. The outer
document is the plan needed by the decoder. Obtain corresponding responses with
a separate read-only RPC client, then pass the saved files to `decode --plan
PATH --responses PATH`. Inputs must resolve inside the current working directory,
including symlinks, and are limited to 64 KiB each. CLI errors return 2 and
structured JSON on stderr; valid plan/CSV output returns 0.

CSV keys are `chain_id`, `token_address`, and `field`. To compare independently
captured files using Line 2, repeat those three `--key` options and use
`--ignore block_number` to compare values across blocks while retaining the
block in the original evidence. For example, this runnable check compares the
observation with itself:

```sh
python3 -B line-2/tools/csv-reconcile/reconcile.py shared/token-read-plan/observed.csv shared/token-read-plan/observed.csv --key chain_id --key token_address --key field --ignore block_number
```

The gathered observation also passed a row-reordered comparison: six unchanged
rows, exit 0. A scratch-only synthetic one-base-unit increase to ZTO supply
produced exactly one changed key and preserved all 18 decimal places, exit 1.
No synthetic supply change is included in the delivered observation.

## Validation and limits

```sh
python3 -B -m unittest discover -s shared/token-read-plan -v
```

All ten checks passed: observed decoding, batch reordering, actual read-only
destinations/selectors, modified plan rejection, missing/duplicate IDs and RPC
errors, canonical return encoding, precise decimal rendering, JSON resource and
duplicate-key checks, workspace containment including symlinks, and CLI
output/error behavior. Demo stdout matched `observed.csv` byte-for-byte.
The inherited Line 4
workbench's 12 regression tests also passed before reuse.

The decoder requires exactly the six known requests and six complete responses.
It rejects error responses, noninteger/duplicate IDs, unsupported methods or
destinations, invalid ABI padding, surplus words, malformed hex, and oversized
results. It decodes every result before printing anything. `raw_value` retains
the exact integer base-unit supply; `display_value` uses integer arithmetic.
The symbol received is preserved alongside `expected_symbol`, so symbol drift
can be reconciled without silently substituting an expected name.

The supplied block and responses are claims from a caller/RPC, not a verified
state proof. Responses contain no block identifier of their own; this offline
tool cannot establish that an endpoint honored the pinned block or Ethereum
chain. Block numbers can be reorganized; use independently verified/finalized
observations when that matters. Only the dynamic-string form of `symbol()` is
supported; legacy bytes32 symbol returns fail explicitly. The bundled snapshot
is historical and does not refresh itself. There is no balance/allowance lookup,
arbitrary owner address, price quote, pool valuation or transaction creation.

## Reuse

`abi_workbench.py` is an unchanged vendored copy of
`line-4/tools/abi-workbench/abi_workbench.py` as found in this round. Its Keccak,
type handling and ABI encoder/decoder are reused directly. The wrapper adds
bounded, workspace-contained JSON inputs, a strict three-function read plan,
canonical single-output validation, and the CSV columns consumed by Line 2.
The CSV reconciler remains in its original line; no line files were changed.


## Gathering 23 refresh

`abi_workbench.py` is now the byte-identical Step 23 Line 4 implementation,
including bounded ABI-file loading, shape validation and concise file errors.
The ten token-plan tests still pass; the historical demo remains byte-for-byte
identical to `observed.csv`. No new chain observation is claimed in this round.
Line 2's renderer is shared at `shared/import-drift/review.py`; its six-row
[offline review](observed-review23.html) preserves exact strings and composite
keys. See Import Drift's README for the command. No new coin is needed.

## Gathering 24 refresh

`abi_workbench.py` is now a byte-identical copy of Line 4's Step 24 version,
including one-dimensional fixed and dynamic arrays of static scalars. The
token plan still uses only scalar and string return values, so its six
historical ZTO-first/IMD-second CSV rows remain byte-for-byte the same.
Its ten offline checks pass. This refresh makes the newer ABI codec available
to another worker without changing the historical observation or making a
current-chain claim.
# Gathering 25: canonical decoding and checked CSV handoff

The vendored ABI workbench now matches Line 4 Step 25 byte-for-byte. Token
returns use its `decode_tuple(..., strict=True)` contract directly, rejecting
noncanonical layouts and surplus words. All ten token-plan checks pass and
`demo` still reproduces `observed.csv` byte-for-byte.

[Checked CSV Review](../import-drift/CHECKED_REVIEW.md) adds Line 2's key audit
before comparing decoded exports. Its real-data demonstration confirms six
unique `(chain_id, token_address, field)` keys in the retained ZTO-first/IMD-second
observation. These remain historical observations, not a new RPC read.
