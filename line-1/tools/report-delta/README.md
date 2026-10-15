# Report Delta

Compare two saved Endpoint Sentry reports without sending another request.
This Python 3.9+ standard-library CLI reports changed redirect/status chains,
check outcomes, failure stages, limits and body SHA-256. It ignores volatile
observation times and latency. A changed body digest alone is informational:
a changing API response does not establish an application failure.

One command from the repository root shows it working offline on the real
swarm observations retained with this tool:

```sh
python3 -B line-1/tools/report-delta/report_delta.py line-1/tools/report-delta/observed-before.json line-1/tools/report-delta/observed-after.json --same-expectations
```

The two inputs were captured with the same command, in sequence, on 2026-10-16:

```sh
python3 -B line-1/tools/deadline-sentry/deadline_sentry.py --deadline 5 https://api.imd.fun/launches --timeout 4 --json --expect-path /launches/0/status
```

Both anonymous GETs returned HTTP 200 and passed the JSON/pointer checks.
Comparison returned `still_healthy`, exit 0, with no stable-field changes.
These are historical observations, not an offline substitute for current health.
No response bodies are retained. No coin, price or balance is needed.

Use the command with your own explicitly supplied `before.json` and
`after.json`. Inputs must resolve inside the current working directory tree,
be UTF-8 JSON and be at most 256 KiB each. Duplicate keys, non-finite numbers,
unknown schemas and contradictory outcomes are refused. Completed
`deadline-sentry/v1` wrappers are unwrapped; an interrupted/deadline-expired
wrapper has no completed endpoint evidence and is refused with exit 2.
No directory scanning, network, environment access or writes occur.

`--same-expectations` asserts that both invocations used identical HTTP status
and JSON expectation arguments. Endpoint Sentry v1 omits some expectations
from its report, especially the expected JSON value and checks not reached
before failure. Without this assertion the verdict is `inconclusive`. Even
with the assertion, different requested URLs, limits or recorded expectations
produce `inconclusive`; URL matching is exact, with no normalization.
Keep the actual probe commands together with saved reports.

Verdicts: `regressed` (passing to failing), `recovered` (failing to passing),
`still_healthy`, `still_failing`, or `inconclusive`. Exit 0 means comparable and
the after observation passed; 1 means comparable and it failed; 2 means invalid
input or inconclusive. Still-failing observations can have different causes;
inspect `changes`. This identifies observed differences, not their root cause.
Reports are untrusted data, not attestations, and may contain URLs or other
application values; use only public, non-secret report files. File-size bounds
do not prevent every deeply nested JSON parser resource limit. A directory
containment check is not a defense against concurrent filesystem replacement.

Verification:

```sh
python3 -B -m unittest discover -s line-1/tools/report-delta -v
```

Nine tests passed, including health transitions, changing bodies, incomplete
probes, mismatched arguments, strict JSON, invalid evidence, real CLI exit
status, byte bounds and refusing paths outside the current workspace.
