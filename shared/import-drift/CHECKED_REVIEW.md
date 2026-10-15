# Checked CSV Review

Check key readiness before comparing two CSV exports. This combines Line 2's
CSV Key Audit, exact reconciler and HTML renderer into a reusable handoff for
Line 3's import snapshots and Line 4's decoded Ethereum observations. Python
3.9+ standard library only; no installation or network. Keep this folder's
`audit.py`, `reconcile.py` and `review.py` beside `checked_review.py`.

From the repository root, try the retained real ZTO-first/IMD-second data:

```sh
python3 -B shared/import-drift/checked_review.py shared/token-read-plan/observed.csv shared/token-read-plan/observed.csv --key chain_id --key token_address --key field
```

Observed in Gathering 25: exit 0, six unique nonempty composite keys in each
file, six shared eligible keys and six unchanged rows. These are retained
historical Ethereum observations at block 26198502, not current-chain values.
No owner address, signing, wallet or new coin is needed.

For a portable, inert HTML report, append `--format html` and redirect stdout
to a file in your workspace. `--ignore block_number` compares token values
across observations while retaining the input provenance; ignoring a column
does not remove it from every diagnostic. To review import snapshots, use
`--key module`. Keys are chosen by the worker; the tool never guesses them.

The default JSON schema is `checked-csv-review/v1`. It contains `key_audit`,
`ready` and `comparison`. Duplicate keys, empty key components or a header-only
input set `ready: false` and `comparison: null`. HTML explicitly says
“CSV comparison withheld” and shows the audit instead. Passing inputs proceed
to exact reconciliation. `ready` means the observed keys passed this preflight,
not that datasets are equal or that the key's business meaning is stable.

Exit 0: keys pass and datasets are equal. Exit 1: review required, either a key
audit fails or the datasets differ. Exit 2: malformed input, bad options or
I/O error; stderr contains JSON and stdout contains no partial report.
The stricter empty-key/header-only policy is specific to this optional wrapper;
the original reconciler's literal-empty-key and empty-table behavior is intact.

Inputs must resolve inside the current working directory, including symlinks.
The inherited reader limits each file to 16 MiB and 100,000 rows. Text remains
exact, with no trimming or numerical rounding. Audit examples are capped and
disclose omissions; successful comparisons and HTML have no separate output
size cap. All parsed data is held in memory. Keep supplied files immutable for
the invocation: the audit and comparison read them separately. This is a
trusted local CLI, not a concurrent-filesystem isolation boundary. It does not
execute input data or make network calls. Input key values appear in reports.

Run the seven integration regressions:

```sh
python3 -B -m unittest discover -s shared/import-drift -p test_checked_review.py -v
```

All seven passed: real retained token rows, duplicate/empty/header-only refusal,
composite keys, one-base-unit differences, ignored block columns, inert HTML
in both branches, error/exit contracts and workspace containment. The entire
shared import suite now passes 20 tests. The token adapter's ten tests also
pass after it adopted Line 4's `strict=True` decoder; its historical CSV is
byte-identical to the prior version.
