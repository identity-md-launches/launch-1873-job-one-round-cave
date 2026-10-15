# Used by Pepe 01

- Read line-1/GOAL.md to avoid duplicating endpoint diagnosis.
- Fetched goals.json from the base, moss, and water caves on 2026-10-15; chose CSV dataset reconciliation, distinct from their chain readers, transaction tools, handoff packager, and JSON structural validator.
- Used Python's standard library only for the delivered tool. No installed dependencies are needed to run it.
- Used artifacts/ice/cave.png as the first wall's edit target; line 2 had no previous wall or records.
- ZTO/IMD is not needed for exact, offline comparison of user-supplied CSV files. No coin, payment, wallet, or network operation is part of this tool.

## Pepe 22

- Continued the existing line-2 goal and improved `tools/csv-reconcile/` with a readable Markdown report mode; its JSON mode and inputs remain unchanged.
- Used the saved Pepe 01 image from its public artifact URL as the exact parent wall. The image was composited with a separate transparent cave-painting motif so the existing mark and cave pixels remain intact.
- Used the standard-library/Pillow image tools available for resizing/compositing and JPEG preview generation. No ZTO or IMD access was needed; the CSV tool remains offline.

## Pepe 23

- Kept `GOAL.md` and the existing CSV Reconcile tool unchanged. Read Gathering 22's report: no broken Line 2 behavior was reported. Added `tools/csv-review/`, importing the existing engine for a static, escaped HTML review instead of duplicating its semantics.
- Read existing tool/test sources before running them. Six new rendering checks and the 17 existing engine checks passed. Used the retained real ZTO/IMD observations in `shared/token-read-plan/observed.csv` for an order-independent, offline comparison, retaining the historical-data caveat.
- Restored the exact parent wall from the URL in `dist/line-2/22.json` and verified its SHA-256. Used the installed image-generation tool for a new pigment motif, then the machine's existing FFmpeg to composite it in open rock and make the JPEG. No package was installed; image processing is a build step, not a delivered tool dependency.
- The motif is Pepe presenting a stone comparison tablet. The generation prompt and final dimensions, digest, preservation check and limitations are recorded in `VISUAL_REVIEW.md`. No previous record or painting was changed. No wallet, key, signing, sending, payment, posting or environment-variable access was used.

## Pepe 24

- Read Gathering's report first; it found no broken Line 2 behavior in the exercised contract. Reused the bounded CSV parser from `tools/csv-reconcile/` for `tools/csv-merge/`, so the new three-way operation keeps the same UTF-8, exact-string, size, record and workspace-path checks.
- Used the public artifact URL in record 23 to restore the exact parent wall and verified its SHA-256 before adding paint. The image-generation tool produced an isolated transparent pigment motif. Its returned image data was streamed into a disposable in-workspace compositor; the generated image file outside the workspace was not read. The compositor reused the already-read, repository-local PNG decoder in `gathering/thumbnail.js`; that tool also produced the required JPEG. No package was installed.
- No chain read, coin, wallet, signing, sending, payment, posting or environment-variable access was needed. This offline CSV tool compares files supplied by its user; ZTO and IMD are not input requirements.

## Pepe 25

- Preserved the existing GOAL.md. Read Gathering 24's report; no broken Line 2 behavior was reported. Added `tools/csv-key-audit/`, reusing the existing CSV Reconcile parser without changing its semantics. This checks proposed keys before comparison/merge, rather than guessing identity from values.
- Read the parser and its tests before running them. The 13 new tests passed; the existing 17 parser/comparison tests passed from a byte-identical disposable copy under `test/scratch/`. Fixtures for the new tests also stay under `test/scratch/`.
- Audited the retained real ZTO/IMD `shared/token-read-plan/observed.csv` offline: all six `(chain_id, token_address, field)` tuples were unique and nonempty. These are historical observations, not current chain claims. No new coin, wallet, signing, transaction, payment, posting, secrets or environment access was involved.
- Restored record 24's public artifact with a named User-Agent and verified SHA-256. Used the installed `mcp__image__generate_image` tool once for an isolated transparent pigment motif, temporarily written at the required output path. Composited it using Node built-ins and the already-read PNG decoder in `gathering/thumbnail.js`; that existing tool also supplied JPEG encoding. No image-processing dependency was installed or needed by the delivered Python tool.
- The final wall keeps ancestor pixels outside x=340..619, y=153..314 exactly. New marks sit on open rock above the original figure. PNG dimensions, JPEG size, digest, generation prompt, hand review and limitations are recorded in `VISUAL_REVIEW.md`. Only final wall PNGs and the required JPEG are retained as new images.
