# PPT Text Normalize

Built-in Safe MVP tool for automation-first PPT text style normalization.

## Current contents

- `CONTEXT.md` — local vocabulary aligned with the root `CONTEXT.md`
- `design.md` — current Safe MVP design and validation rationale

## Current built-in pipeline

1. `scan` — inspect PPTX, resolve page types / text roles, generate reports and `rules.json`
2. `apply` — consume `rules.json`, normalize text styles conservatively, emit a new PPTX and reports

## Scope v1

Included:
- text boxes
- title/body placeholders
- table cell text

Excluded:
- SmartArt text
- chart text
- notes text
- master/layout source text

## Automation goal

The default operating mode is end-to-end automatic processing:
- `scan` auto-generates `rules.json`
- `apply` auto-consumes it
- manual edits remain optional, not required

## Current command surface

Current built-in commands:

- `scan.py`
- `apply.py`

Not part of the current built-in command surface:

- browser visual review gate
- review workspace builders
- reviewed-rules compilation flow

## Safe MVP behavior

The first safe MVP targets multi-author PPT text-style drift without redesigning slides.

Defaults:
- canonical styles are inferred automatically from `majority_real_slide`
- matching is by `Page Type + Object Slot`
- `content_body`, `content_label`, `content_stat`, and `table_text` keep `font_size` and `color` stable by default
- hero-like pages and hero-like slots are frozen and reported
- low-confidence or ambiguous blocks are skipped with normalized reasons
- TOC/chapter pages receive only minimal repeated-evidence normalization in this MVP
- TOC grids with clear numbered chapter items use `toc@uniform_grid`: title items may normalize font family / weight, while size and color are preserved
- TOC secondary labels such as `Contents` use conservative treatment and do not receive automatic bold/color changes
- Chapter opener pages with a large numeric marker plus adjacent large title use `chapter@uniform_series`: marker and title may normalize font family / weight while size and color are preserved
- Footer variants are split into organization name, page number, and note; color is never voted across those variants
- Weak canonical styles may apply font family only
- Font-family normalization keeps DrawingML Latin and East Asian channels separate, writing both `a:latin` and `a:ea` when canonical values exist

## Next implementation targets

- `scan.py` emits `scan_report.json`, `scan_report.md`, and `rules.json`
- `apply.py` emits a new normalized PPTX plus `apply_report.json` / `apply_report.md`
- runtime artifacts stay under the task work directory, for example `<workdir>/ppt_text_normalize/<task_name>/`

## Runtime artifact location

Test PPTX files, reports, logs, and generated outputs should live under a task work directory outside the source tree:

`<workdir>/ppt_text_normalize/<task_name>/`

## Commands

```bash
python3 scripts/ppt_text_normalize/scan.py <input.pptx> --task demo
python3 scripts/ppt_text_normalize/apply.py <input.pptx> --rules <rules.json> --task demo
```


## Example run

```bash
python3 scripts/ppt_text_normalize/scan.py \
  /path/to/input.pptx \
  --task normalize_demo \
  --workdir <workdir>/ppt_text_normalize/normalize_demo

python3 scripts/ppt_text_normalize/apply.py \
  /path/to/input.pptx \
  --rules <workdir>/ppt_text_normalize/normalize_demo/rules.json \
  --task normalize_demo \
  --output <workdir>/ppt_text_normalize/normalize_demo/output/normalized.pptx
```

## Anti-overfitting rule

Tests may encode a defect pattern, but production code must not encode a sample deck name,
slide number, institution name, or specific font as a success condition. Font-family
normalization is data-driven: the canonical font comes from the deck's eligible majority
cluster, not from a built-in preferred font list.

## OOXML namespace preservation rule

PowerPoint slide XML may contain markup-compatibility nodes such as `mc:AlternateContent` with `Requires="p14"`. The `Requires` value depends on a matching namespace declaration like `xmlns:p14`. Raw `ElementTree.tostring(...)` can rewrite the declaration to an unstable `ns*` prefix while leaving `Requires="p14"` unchanged, causing PowerPoint to report that the PPTX needs repair and to delete repaired content.

Rules for this tool:
- Never write slide XML with raw `ET.tostring(...)`.
- Always write modified slide XML through `serialize_xml_preserving_prefixes()`.
- Always validate generated PPTX files with `validate_markup_compatibility_prefixes()` before reporting apply success.
- Regression tests must keep `Requires="p14"` paired with `xmlns:p14` and reject leaked `xmlns:ns*` prefixes.
