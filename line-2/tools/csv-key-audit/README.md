# CSV Key Audit

Check proposed key columns before using [CSV Reconcile](../csv-reconcile/README.md) or [CSV Merge](../csv-merge/README.md). This read-only tool reports duplicate key groups, records with empty key components, and whether adding another column makes a key unique. It never selects a key or pairs duplicate records for you.

Python 3.9+, standard library only; no installation. Keep the sibling `csv-reconcile/reconcile.py`: this tool imports its existing bounded CSV parser. Run from the workspace root. It reads only the supplied CSV files inside the current working directory, prints to stdout/stderr, and makes no network requests or file changes.

## One command to see it working

```sh
python3 -B line-2/tools/csv-key-audit/audit.py line-2/tools/csv-key-audit/demo.csv --key item --key location --format text
```

Observed: **PASS**, 3 records, 3 unique nonempty composite keys, no duplicate groups or empty key components; exit **0**. These are synthetic inventory fixtures. Try only `--key item` on the same file: it reports the repeated `lamp` at logical records 2 and 3 and exits **1**. Adding `location` distinguishes those rows without changing any input.

For a failure demonstration:

```sh
python3 -B line-2/tools/csv-key-audit/audit.py line-2/tools/csv-key-audit/demo-issues.csv --key item --key location --format text
```

Observed: **REVIEW**, one duplicate group (records 2 and 3), one record with an empty key component (record 4), and exit **1**. Each duplicate occurrence counts even if all its fields are identical. Duplicate and empty-key counts can overlap.

Supply multiple files to audit all of them and see eligible-key overlap with the first input. A key is eligible in an input only when it occurs exactly once and has no empty component. Overlap reports count those exact tuples shared by the two inputs, plus tuples only on each side; duplicates and empty keys are excluded separately in each input. Low overlap may be legitimate additions/removals. High overlap does not prove identity stayed stable.

## Output and limits

- `--format json` is the default (`csv-key-audit/v1`); `--format text` is a readable report of the same findings. JSON indexes inputs starting at 0. Record numbers count logical CSV records, with the header as record 1; multiline quoted fields do not inflate those numbers.
- Exit **0** means every file has at least one data record and its proposed keys are unique and nonempty. Exit **1** means review is needed: duplicate keys, empty key components, or a header-only file without evidence to evaluate the key. Exit **2** means invalid input or I/O failure; no partial successful report is printed. Parser usage errors also exit 2.
- All values are exact strings. `01` and `1` differ; spaces and Unicode are preserved. An empty component means exactly `""`; a whitespace-only string is not classified as empty. This is a stricter readiness policy than Reconcile, which permits a literal empty key. No values are normalized, trimmed, inferred or rewritten.
- Composite keys are tuples, so `(ab, c)` and `(a, bc)` are distinct. Column order and row order do not determine key identity. Example groups use deterministic tuple ordering; record numbers retain the source order.
- `--examples N` limits groups per issue category and record numbers per group (default 5, range 0–20). Counts cover every row even when examples are omitted. `omitted_*_groups` and `omitted_records` disclose truncation. A key component's preview is limited to 160 characters and includes its full character count and an explicit `truncated` flag. Use the record numbers to inspect full values in the source. Non-key cell contents are not included. This is not a redaction service: keys and paths may be sensitive.
- At most 8 files, 16 MiB and 100,000 data records per file, using the existing parser's UTF-8/BOM, strict quoting, unique nonempty header, ragged-record and resolved-workspace-path checks. Symlinks resolving outside the workspace are refused before opening the target. Reports and parsing still use memory proportional to the input; no streaming guarantee or automatic dialect repair.
- Passing proves only observed uniqueness and nonemptiness in these particular exports. A mutable display name or renumbered ID can pass and still be the wrong key. Choose keys from the source system's identity contract. This tool does not search candidate combinations or certify semantic stability.

## What happened when tried

All **13 behavioral tests** passed, including tuple collisions, identical duplicates, empty/duplicate overlap, Unicode and multiline record numbers, sample truncation, empty tables, later-file failure with no partial report, CLI statuses and workspace/symlink refusal. The reused parser's existing **17 tests** also passed from a disposable copy under `test/scratch/`.

```sh
python3 -B -m unittest discover -s line-2/tools/csv-key-audit -v
```

Tests create and remove fixtures only under `test/scratch/`. No packages or network are needed.

Also tried on retained real ZTO-first/IMD-second observations:

```sh
python3 -B line-2/tools/csv-key-audit/audit.py shared/token-read-plan/observed.csv --key chain_id --key token_address --key field --format text
```

Observed: **PASS**, six records and six unique nonempty keys, exit 0. Using only `token_address` correctly requires review because each token has three observed fields. These are historical observations retained by earlier contributors, not a live balance, supply or price claim. The tool's normal operation needs no coin, wallet or chain access.
