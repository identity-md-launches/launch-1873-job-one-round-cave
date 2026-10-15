# Import Delta

Compare two Python source trees before reviewing a refactor. Import Delta shows
added and removed modules, explicit local import edges, `__main__` entry points,
and strongly connected cycle groups, plus source-path changes for surviving
module names. It reads source through the sibling Import Map and never imports
or executes the inspected project. Python 3.9+ and only the standard library
are needed, offline. Keep `import-map/` alongside this folder when copying it.

Run from the repository root:

```sh
python3 -B line-3/tools/import-delta/delta.py line-3/tools/import-delta/examples/before line-3/tools/import-delta/examples/after
```

Observed: one added edge, `helper -> main`, creates the cycle group
`helper, main`; neither scan has issues or recognized dynamic imports. Exit 0.
Reversing the roots reports the edge and group removed. This makes a new cycle
visible before anyone runs the refactored source.

Pass two explicit import roots, for example `old/src new/src`. Both must be
inside the current working directory. `--json` emits deterministic JSON with
all scan warnings from both sides, including parse errors and dynamic-call
locations. Text output shows warning counts; use JSON for their details.
`--check` returns 1 for structural differences. `--strict` returns 1 for scan
issues or recognized dynamic imports, independently of differences. The flags
combine. Cycles are compared structure, not scan warnings: an unchanged cycle
alone does not fail either flag. Missing/outside roots or caught scan errors
return 2 without a partial success report. Default success returns 0 even if
there are differences. No output file is written by the CLI.

Reproduce the checks:

```sh
python3 -B -m unittest discover -s line-3/tools/import-delta -v
```

Tried locally: **9 tests passed**, along with all **18 existing Import Map and
Import Impact tests**. Checks include both comparison directions, cycle-group
merging, source relocation from module to package, module and entry-point
changes, deterministic JSON and CLI statuses, invalid roots, source execution
traps, UTF-8 BOM and Latin-1 source, namespace-relative imports, and parse-error
edge loss with retained warnings. An unchanged real-source scan of
`line-1/tools/deadline-sentry` returned no changes or warnings, exit 0 with
`--check --strict`; [retained JSON](observed-delta.json).

Limits: these are sets of explicit static local edges, not runtime behavior or
all source edits. Changes to constants, comments, import line numbers, import
spelling that resolves to the same edge, or external imports alone do not count
as structural differences. Warning details remain visible even when
`has_changes` is false. A parse error can make an edge appear removed; inspect
warnings before interpreting the diff. Cycle groups are compared as whole
sorted member sets, so merging two groups removes two and adds one. This is
not a comparison of individual cycle paths. Module renames appear as removed
and added modules, not inferred renames.

Resolution inherits Import Map's conservative attribute/submodule choices and
its limits for implicit package-initializer execution, dynamic imports, hooks,
plugins, and packaging entry points. Source-path checks reject selected files
resolving outside the workspace; this is not a sandbox against concurrently
modified source. Whole-tree scanning and output have no total memory budget.
No coin, network, wallet, signing or transaction is needed.
