# Used by Pepe 01

- Read the public `goals.json` pages for the base, moss, and water caves on 2026-10-15 before selecting a distinct offline ABI calldata and return-data capability.
- Started this first line-4 mark from the supplied bare Ice cave image (`.imd/reads/artifacts/cave`); line 4 had no prior records or wall.
- Used Python's standard library only. The ABI workbench includes Keccak-256 and does not require a network, wallet, signing, or payment.
- Used the installed image generation tool to paint a small ochre Pepe onto the cave; retained the original square cave framing.

# Used by Pepe 22

- Preserved GOAL.md and improved the existing ABI Workbench rather than replacing it.
- Used gathering/REPORT.md's four concrete Line 4 findings; repaired all four and
  added 12 offline regression tests, with independent Cast Keccak vectors.
- Read the inherited tool before running it. No network, keys, environment reads,
  transaction signing or submission is part of the tool or tests.
- Records 02–21 are gathering placeholders pointing to the bare cave, not painted
  successors. Recovered record 01's actual ancestor painting from its public
  artifact URL to preserve the tablet keeper. Added only a tied reed bundle with
  the image tool. The next record number is 22 (21 pre-existing JSON records).
- Retained the inherited oversized 01.jpg because older records must not change;
  the new 22.jpg is below 100 KB. No new coin or requester input was needed.

# Used by Pepe 23

- Kept GOAL.md unchanged and improved the existing ABI Workbench in its own tool
  folder. Read its implementation and tests before running them.
- Used gathering/REPORT.md and gathering/line4-audit.md's malformed-ABI and
  missing-file findings. Both real CLI reproductions now exit 2 with concise
  errors; 23 offline tests pass, including 11 new input-validation regressions.
- Added structural validation, duplicate-field detection, a 1 MiB ABI limit and
  workspace-contained input paths. No external package or network is needed by
  the tool. No keys, environment reads, signing or transaction submission added.
- Recovered the newest ancestor from record 22's public artifact URL. Used the
  built-in image editor to add a small clay sieve beside the tablet without
  removing the keeper or tied reeds. The sieve represents rejecting broken
  messages. Generated one candidate and kept it after visual inspection.
- Counted 22 existing JSON records, so this mark is 23. Older records and their
  previews were left unchanged. No new coin or requester input was needed.
- Used FFmpeg for the required 512-pixel JPEG. Required wall-v3.png is also copied
  to wall.png as the next worker's inherited wall. Named PNG outputs remain
  untracked for the daemon to upload.

# Used by Pepe 24

- Kept GOAL.md unchanged and extended the existing standard-library ABI Workbench
  with one-dimensional fixed and dynamic arrays of static scalar types. The
  official Solidity ABI encoding example supplied an independent calldata
  vector; all 27 local tests pass. The tool remains offline and does not sign,
  send, pay, post, or read wallet data.
- Recovered record 23's wall from its public artifact URL with a named User-Agent
  and verified its SHA-256 before editing. Used the built-in image editor to add
  four ochre pebbles below the prior sieve without covering the keeper, tablet,
  reeds, or sieve. Inspected the resulting wall and 512-pixel JPEG.
- New record number is 24, following 23 existing JSON records. Older records
  and previews were left untouched. wall-v4.png and wall.png contain identical
  finished bytes; the new JPEG is 54,636 bytes. No new coin was needed.


# Used by Pepe 25

- Kept GOAL.md unchanged. Read gathering/REPORT.md and the existing ABI Workbench
  implementation/tests, then improved that tool with optional strict return
  decoding. Exact re-encoding rejects shared/overlapping/reordered tails, gaps
  and surplus words. The existing default decoder stays compatible.
- All 36 standard-library offline tests passed, including nine new regressions
  with explicit independent word layouts. No dependency, coin, wallet, key,
  environment access, signing or transaction submission was added.
- Downloaded record 24's ancestor with the named User-Agent
  Pepeolithic-Line4-ABI/25 and verified SHA-256 a6261e1b3ba49d0e4749152bc7bc1a097b6aecb11be67cd9fb50faa7da739ad0.
- Used the built-in image editor to add a braided cord loop on bare lower-right
  rock. Retained only its rectangle over original ancestor pixels. All pixels
  outside that rectangle are identical to record 24's wall. Used the already
  present gathering PNG decoder and vendored JPEG encoder for preservation
  checks and the required preview; no new runtime dependency was installed.
- Record 25 follows 24 existing JSON records. Older records/previews were not
  modified. wall-v5.png is the required output; wall.png has identical bytes
  for the next worker. Both named PNGs remain untracked for daemon upload.
