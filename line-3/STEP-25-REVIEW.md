# Step 25 — The Compared Trails

Added [Import Delta](tools/import-delta/README.md), a standard-library tool for
comparing two Python import roots without executing inspected code. It exposes
new cycles and lost dependencies during refactors and keeps both scans' parse
and dynamic-import warnings visible. GOAL.md and earlier tools and records are
unchanged. This needs no coin, price, payment, wallet or transaction.

## Tried locally

- New Import Delta suite: **9 tests passed**.
- Existing Import Map suite: **10 tests passed**.
- Existing Import Impact suite: **8 tests passed**.
- README example: exit 0; one added edge `helper -> main`, one new cycle group
  `helper, main`, no scan warnings.
- Source-only comparison of real `line-1/tools/deadline-sentry` with itself:
  `--json --check --strict` exited 0, no changes or warnings. Retained as
  `tools/import-delta/observed-delta.json`. Its runtime behavior was not tested.

The tool compares explicit static structure, not all source edits or runtime
behavior. Parse errors can remove apparent edges; both scans' issues remain
available in JSON. Source scanning has no total memory budget. Resolution limits
are inherited from Import Map and documented in the tool README.

## Image review

The required `artifacts/line-3/wall-v5.png` and alias `wall.png` are identical
**1254 × 1254 RGB PNGs**. The preview `dist/line-3/25.jpg` is **512 × 512 JPEG**,
72,194 bytes. `dist/line-3/25.json` is the only new numbered record, with the
specified three keys and six attributes; there were 24 inherited records.
The explicitly required JPEG beside the record follows the specific preview
requirement despite the general instruction about pictures outside artifacts.

Ancestor recovered through record 24 and verified against SHA-256
`f745d84ca9484eb9d228d1a1c152f828a4ac18882616686a5809499444cc2493`.
Final SHA-256:
`d8bf790f9a251dc7beeef8849118ba81ad20276cbbbfbd01794f2a2433f73747`.
The image tool produced the pigment addition; final artifact processing retained
only x=330..464, y=1120..1224, with a ten-pixel boundary blend. 13,269 pixels
changed inside; **zero pixels changed outside**. No ancestral marks occupy
this patch. Its stone texture may differ locally.

Explicit visual review: opened both the final PNG and the decoded JPEG.
Pepe retains the inherited wide mouth and heavy-lidded eyes. Counted five digits
on each inherited hand (four fingers and a thumb); no hands or handprints added.
The new ochre stones and charcoal/chalk trails are worn, uneven, small pigment
marks on the lower-left ledge. Rock, cracks, lighting, size and framing are
preserved. No letters, numbers, logos, signatures, border, or prohibited symbols
observed. **Unmet visual requirements observed: none.** This local review is
not independent certification; JPEG reduction loses fine texture.

## Image prompt

Installed image edit tool, high quality, automatic size, with the verified
ancestor as the edit target:

> Use case: precise-object-edit. Edit target: inherited square cave painting. Add ONLY one very small worn ochre and charcoal mark on unused rock in the bottom LEFT ledge, centered around x=390,y=1135 of the 1254 square image: two tiny ochre pebble shapes side by side, a short charcoal trail below one and a short chalk-white trail below the other, suggesting a comparison of paths before and after. Keep addition inside x=300..480,y=1095..1190. No arrows, letters, numbers, writing or symbols. Preserve ALL ancestral painting exactly: Pepe the frog with wide mouth and heavy-lidded eyes and both five-digit hands, every old dot and branch, same rock, cracks, torchlight, dimensions, framing. Never erase, move, repaint or redraw existing marks. Earth pigments only, rough handmade worn strokes and bare stone showing through. No new hands, no border, no logos, no watermark. Preserve the rest of image unchanged.

The generated mark was lower than requested; the actual retained rectangle is
recorded above and in `STEP-25-CHECKS.json`.
