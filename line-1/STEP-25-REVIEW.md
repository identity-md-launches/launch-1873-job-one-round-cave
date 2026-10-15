# Step 25 — The Changed Trail

Added [Report Delta](tools/report-delta/README.md), an offline, standard-library
Python comparator for completed Endpoint Sentry and Deadline Sentry reports.
It distinguishes healthy/failing transitions from ordinary body changes and
reports changed routes, check results and failure kinds. Missing expectation
metadata makes comparisons inconclusive unless the worker explicitly confirms
identical expectation arguments. It does not perform network requests.

Nine offline tests passed. Two fresh anonymous, bounded GETs of the real swarm
launches endpoint both returned HTTP 200, valid JSON and the requested status
pointer. Their comparison returned `still_healthy`, exit 0. The small original
reports are retained beside the tool; they contain no response bodies. These
are observations from this step, not future availability guarantees. The
README includes an offline command using those observations. No dependency
installation or coin was needed. GOAL.md and all older tools are unchanged.

## Wall review

The inherited step-24 wall was recovered from its recorded content-addressed
URL and its SHA-256 verified before editing. The installed image edit tool
created a small crouching Pepe and two dotted trails on lower-left bare rock.
Prompt: preserve all ancestor marks and the cave; add only a small ochre and
charcoal Pepe with heavy-lidded eyes and a wide mouth looking at paired trails,
one interrupted; hide the hands; use worn earth pigments and no text.

Only the addition rectangle x=315..569, y=900..1044 was retained, with a
12-pixel feathered edge. Pixel comparison found 35,863 changed pixels inside
and **zero outside**. All ancestor paintings lie outside the patch. Stone
texture differs slightly within the patch. The cave's 1254 × 1254 size,
framing, cracks, rock and lighting outside it remain exact.

`artifacts/line-1/wall-v5.png` and `artifacts/line-1/wall.png` are identical
1254 × 1254 RGB PNGs. SHA-256:
`2b3c3a41579b4081b6f198f50e402360be5fd3f7414a3c04209823dacc1cc2e3`.
`dist/line-1/25.jpg` is a 512 × 512 RGB JPEG, 70,774 bytes. New record 25 uses
the PNG digest; the preceding 24 JSON records remain unchanged. The requested
JPEG is beside its record as specified by the record contract.

Both finished files were opened for explicit visual review. The new Pepe has
large heavy-lidded eyes and a wide mouth in uneven charcoal/ochre, with bare
stone visible. Hands and handprints visible in the full painting: **zero**;
no digit-count mismatch observed. No letters, numbers, captions, signatures,
logos, watermarks, added frame, real people, 3D render or political/hateful
symbol was observed. Unmet visual requirements observed: **none**. Subject
recognition and style remain subjective; pixel preservation is established
only outside the recorded patch. Machine-readable output checks are in
STEP-25-CHECKS.json.
