# Gathering 25 — The Two Checked Stones

All 149 line tests, 30 shared tests and 21 offline demonstrations passed.
Three real swarm HTTP/TLS probes also passed. [REPORT.md](REPORT.md) covers
what each line can do, tested failures, remaining limits and the 21-worker
scope. [COINS.md](COINS.md) says none: no new asset or deployment is needed.

The new [Checked CSV Review](../shared/import-drift/CHECKED_REVIEW.md) combines
Line 2's key audit with exact comparison and offline HTML. It refuses to compare
ambiguous, empty or untested keys. Try the real retained ZTO-first/IMD-second
observation, entirely offline:

```sh
python3 -B shared/import-drift/checked_review.py shared/token-read-plan/observed.csv shared/token-read-plan/observed.csv --key chain_id --key token_address --key field
```

Observed exit 0: six unique nonempty keys per file and six unchanged rows.
The same wrapper accepts Line 3 import snapshots with `--key module`. Seven
new behavioral tests cover key refusal, exact values, inert HTML and errors.
Token Read Plan now uses Line 4's canonical `strict=True` decoder, with all ten
regressions passing and its historical CSV unchanged. No current-chain values
are asserted.

Open [the offline gallery](../dist/index.html): 125 records, 25 embedded previews
and 100 inherited reserved slots. All preview bytes and styles are in that
single 96,563-byte file. Paintings are newest first within each wall. Full-wall
links point to the artifact service. Current small previews trade detail for
the file-size budget; the 512-pixel JPEG links provide larger images.

The mark adds two ringed pigment stones joined by chalk dabs: check identities
before bringing records together. The PNG at `artifacts/gathering/wall-v5.png`
is 1254 × 1254, identical to the working `wall.png`. Its [record](../dist/gathering/25.json)
and [512-pixel JPEG](../dist/gathering/25.jpg) accompany it. All pixels outside
the small addition rectangle are identical to the verified ancestor. The
[visual review](VISUAL_REVIEW.md) records dimensions, format, hand count,
preservation evidence and visual limitations. Both final images were inspected.

Reproduce the offline suites and demonstrations from the repository root:

```sh
python3 -B gathering/run_checks.py
python3 -B gathering/try_tools.py
python3 -B gathering/check_delivery.py
```

The suite runner copies source and fixtures into authorized scratch space to
avoid changing line folders. The demonstration runner uses saved live reports
and retained Ethereum observations; it does not contact the network. These
runners write local evidence JSON under `gathering/`. The structural checker
validates image bytes, record traits/hash, goals, gallery, preserved placeholders
and reused source, but cannot certify art or real-chain truth.

Rebuild the gallery with `python3 -B gathering/build_gallery.py`. Python standard
library plus the installed Node runtime and the included JPEG encoder suffice;
no downloads or package installation. The generator preserves historical
embedded previews and derives missing current miniatures from supplied PNGs.
`finish_wall.js` is the one-time artwork export step and deliberately refuses
an input that is no longer the verified round-24 ancestor; do not rerun it on
the completed wall. It is not needed to view or verify delivered files.

No line folder or configuration was changed. Every new/modified file outside
`artifacts/` is under 100 KB. The inherited oversized Line 4 record-01 JPEG is
preserved and disclosed in the report. Required artifact PNGs are left
untracked for the uploader.
