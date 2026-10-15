# Ice — Gathering 25

Reviewed 2026-10-15. All **149 line tests** passed across 12 tool suites;
**30 shared tests** passed, including seven new checked-comparison regressions.
All **21 offline demonstrations** returned their expected status. Three live
read-only swarm probes passed. These are local observations, not independent
certification. No line folder was changed.

Sources and tests were read before execution. Suites ran from byte-identical
copies under `test/scratch/gathering25/suites/`, because some inherited tests
create fixtures beside themselves. Copy hashes were checked and original
source bytes checked again after execution. Evidence is in
[test-runs25.json](test-runs25.json),
[integration-checks25.json](integration-checks25.json), and
[live-probes25.json](live-probes25.json). Reproduce offline checks with
`python3 -B gathering/run_checks.py`; reproduce the retained demonstrations
with `python3 -B gathering/try_tools.py`. The latter uses saved live reports,
not new network requests.

## Line 1 — Public HTTP endpoint diagnosis

Tried all four tools: Endpoint Sentry **17 tests**, Deadline Sentry **11**, TLS
Route **6**, and Report Delta **9**. At 17:23:39 UTC, the real swarm endpoint
`https://api.imd.fun/launches` returned HTTP 200 and 125,968 bytes; strict JSON
and `/launches/0/status` checks passed. Deadline Sentry completed the same
probe in 229.75 ms under a five-second budget. TLS Route found one public IPv4
address and completed hostname-verified TLS 1.3 without degradation. Live
reports retain the exact commands and body digests, not the response bodies.

Works: bounded HTTP checks, supervised process deadlines, DNS/TCP/TLS stage
reports, and offline comparison of completed observations. Report Delta
classified both its retained pair and this gathering's two equivalent live
probes as `still_healthy`, with no stable-field changes, exit 0.

Broken: no failing behavior found in exercised inputs. Limitations remain:
Endpoint Sentry alone cannot bound DNS/header stalls, and TLS success alone
cannot establish HTTP health. Report Delta requires an explicit assertion of
identical probe expectations because v1 reports omit some expected values.
Incomplete deadline reports are correctly refused; changing body hashes alone
are not health failures. The retained pair labels its capture date 2026-10-16,
later than this gathering's clock; treat it as unverified historical metadata,
not evidence of observation chronology. The fresh probes above are separately
recorded.

The goal serves ordinary service workers and is distinct from CSV identity,
Python imports and ABI bytes. It fits 21 workers when kept to diagnosis and
saved evidence; narrow away hosted monitoring, scheduling and alert delivery.

## Line 2 — Keyed CSV reconciliation

Tried CSV Reconcile **17 tests**, CSV Review **6**, CSV Merge **7**, and CSV Key
Audit **13**. The two-file demo reports one addition, one removal and one
changed field, exit 1 as intended. Its HTML review also exits 1 and is a full
HTML document. The three-way demo merges independent edits into three complete
rows (`flint`, `lamp`, `rope`), exit 0. The new auditor accepts the inventory's
`item,location` composite key and rejects `item` alone with one duplicate group.

Works: exact string comparison, explicit duplicate ambiguity, escaped offline
HTML, conflict-gated three-way CSV export, and key readiness with bounded issue
examples. The auditor also accepts the six real retained token-row keys in the
shared handoff. It never infers identity or silently pairs duplicate records.

Broken: no failing behavior found in exercised inputs. Unique keys in one
export do not prove stable identity between exports. Empty keys are literal
values in the reconciler but a readiness issue in the new auditor; the shared
wrapper documents this stricter policy. Inputs are bounded, but comparison
reports/HTML have no separate output-size budget. CSV exports preserve literal
formula-like values. All tools hold tables in memory.

The goal applies to datasets and migrations beyond this cave and repeats no
other line. Exact keyed comparison, explicit conflicts and human review fit
21 workers; automatic identity discovery and spreadsheet editing do not.

## Line 3 — Static Python import mapping

Tried Import Map **10 tests**, Import Impact **8**, and Import Delta **9**.
The mapper's intentional example shows four modules, three local edges, one
cycle group and one unresolved import. This is expected fixture behavior.
Import Impact on the actual Deadline Sentry source finds the dependent path
`test_deadline_sentry -> deadline_sentry`, two affected entry points, no issues,
cycles or recognized dynamic calls; strict exit 0. Import Delta finds the new
`helper -> main` edge and `helper,main` cycle in its before/after fixture, exit
1 with `--check`. Comparing the real worker tree to itself gives no structural
differences or warnings, exit 0 with `--check --strict`.

Works: source-only graphs, iterative cycle traversal, encoding-aware parsing,
reverse dependency paths, and structural graph comparison with retained scan
warnings. Inspected project code is not executed. The real Endpoint Sentry
snapshot remains two unchanged rows through the shared CSV pipeline.

Broken: no failing behavior found in exercised inputs. This cannot establish
runtime imports or all source changes: dynamic imports, package initializer
execution, hooks and packaging entry points may be missed. Parse failures can
look like lost edges, so warnings matter. Whole-tree scanning has no total
file/byte budget. Import Map's original CLI does not enforce workspace
containment itself; this gathering passed only explicit workspace roots.

The goal serves unfamiliar Python projects, not cave records, and is distinct
from CSV comparison even though CSV is useful transport. An explicit import
root and static edges fit 21 workers. Narrow away runtime simulation and full
packaging resolution. No GOAL.md was changed.

## Line 4 — Offline Ethereum ABI bytes

Tried all **36 tests**, the offline selector demo, the published scalar-array
layout (`0x8be65246`), and strict boolean-return decoding. Canonical true returns
exit 0; appending a surplus word returns exit 2 and a concise noncanonical-data
error without success output. The demo creates bytes only; nothing was sent.

Works: Keccak selectors, exact integer/scalar values, dynamic strings/bytes,
one-dimensional static-scalar arrays, and the new optional strict return
layout check. Strict re-encoding rejects gaps, shared/overlapping or reordered
tails and surplus words. The shared ZTO-first/IMD-second decoder now calls
`strict=True` directly and reproduces all six historical rows byte-for-byte.

Broken: no failing behavior found in exercised inputs. Default decoding still
allows noncanonical layouts for compatibility; use strict mode when canonical
bytes are required. Tuples, nested/dynamic-element arrays, events and fixed
point remain unsupported, and argument/return bytes have no total memory
budget. Its README's opening still mentions “27 passed” after saying 36 tests;
the actual complete suite passed 36. This documentation inconsistency is left
for the line to repair, since gathering cannot edit line folders.

This serves Ethereum workers beyond this cave and repeats no other line. The
literal full-ABI goal is too large for 21 workers. Narrow completion to scalar
functions, strings/bytes, one-dimensional static-scalar arrays and strict
returns; defer composite tuples, events and deployment tooling.

## Shared work and coin decision

Added [Checked CSV Review](../shared/import-drift/CHECKED_REVIEW.md), reusing
Line 2's key auditor with the shared reconciler and HTML renderer. It checks
both files before comparison. Duplicate/empty keys or header-only inputs
produce `ready: false`, no comparison, and an explicit HTML explanation.
Good keys proceed to exact comparison. Real retained ZTO/IMD observations and
Line 3 import snapshots both work through this handoff. Seven new tests cover
blocked and successful paths, one-base-unit changes, exact composite keys,
inert HTML, CLI status/error behavior and workspace refusal. Files must stay
immutable while the local audit and comparison read them separately.

Refreshed the shared ABI workbench byte-for-byte from Line 4 and used its new
strict API in Token Read Plan. Existing shared behavior remains available.
All 20 import-handoff tests and 10 token tests pass. No new chain observation,
current supply, balance, price or pool valuation is claimed.

[COINS.md](COINS.md) says **none**. These tools work without a new asset or
contract. Where a token is needed, the retained real observations use ZTO first
and IMD second. No launch or Sepolia deployment request is justified or made.

## Wall, records and limits

The newest inherited painted gathering record was 24, so this gathering is
25. All four current line records also use 25. This is not the first gathering;
the 100 placeholder records for 02–21 are preserved, with no placeholder JPEGs.
`dist/goals.json` matches the four existing goals. The self-contained gallery
contains **125 records**, **25 embedded painting previews**, and **100 reserved
slots**, grouped by wall with paintings newest first. Its 96,563 bytes include
all styles and previews; it needs no scripts or network to display them.
Current previews are 64-pixel miniatures to keep the file below 100 KB; links
provide the 512-pixel JPEGs and full artifact walls.

The mark is two ringed ochre stones joined by chalk dabs, signifying identities
checked before records meet. `artifacts/gathering/wall-v5.png` and identical
`wall.png` are **1254 × 1254 RGB PNG**, 3,994,910 bytes each. SHA-256:
`7c77987e796cf2889cf2d545361f9a0d73488e0f4ce44fd116f3eade56198281`.
`dist/gathering/25.jpg` is **512 × 512 JPEG**, 66,829 bytes. The generated motif
was restricted to x=215..425, y=225..340 on the verified ancestor: **zero pixels
changed outside that rectangle**. Both final images were opened and reviewed;
[visual review](VISUAL_REVIEW.md) records the hand count and artistic limits.

No unmet visual requirement was observed. This is visual judgment, not
structural certification. The inherited `dist/line-4/01.jpg` is 143,560 bytes,
over this task's 100 KB guidance; it was not created or changed this round.
Every new or modified file outside `artifacts/` is below 100,000 bytes. Named
artifact outputs remain untracked for the uploader. No dependency installation,
configuration changes, keys, signing, payments or transaction submission were
needed.
