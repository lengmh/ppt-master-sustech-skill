# PPT Text Normalize

Safe MVP tool for automatic PPTX text-style normalization.

It targets multi-author font-family and font-weight drift while preserving slide content, geometry, hero compositions, and content-area hierarchy.

Public command surface for `r3.1.0-v0.4.0`:

- included: `scan.py`, `apply.py`, reports, conservative normalization rules
- additional review-workspace flows remain source assets and require separate revalidation before being documented as active release capabilities

## Commands

Scan a deck and generate v0.2 rules:

```bash
python3 scripts/ppt_text_normalize/scan.py <input.pptx> \
  --task <task_name> \
  --workdir <workdir>/ppt_text_normalize/<task_name>
```

Apply rules to a new PPTX:

```bash
python3 scripts/ppt_text_normalize/apply.py <input.pptx> \
  --rules <workdir>/ppt_text_normalize/<task_name>/rules.json \
  --task <task_name> \
  --output <workdir>/ppt_text_normalize/<task_name>/output/normalized.pptx
```

## Safety defaults

- Canonical styles are inferred automatically from `majority_real_slide`.
- Matching is by `Page Type + Object Slot`.
- `content_body`, `content_label`, `content_stat`, and `table_text` keep `font_size` and `color` stable by default.
- Hero-like pages and hero-like slots are frozen and reported.
- Low-confidence or ambiguous blocks are skipped with normalized reasons.
- The source PPTX is never overwritten.

## TOC grid handling

- `toc@uniform_grid` is used only when a TOC context marker is present and numbered chapter items form a stable grid.
- TOC grid title items use `toc_item@uniform_grid_title` and can normalize `font_family` / `bold` only.
- TOC grid descriptions stay conservative and do not change size or color.
- Ordinary numbered question grids, timeline years, and footer page numbers are excluded from TOC grid voting.
- `font_family` permission covers both DrawingML channels: `a:latin` and `a:ea` are written separately from canonical `font_family` and `east_asia_font_family`.

## Chapter opener handling

- `chapter@uniform_series` can be detected from structure even when no text says “chapter”.
- The supported opener pattern is a large numeric marker plus adjacent large bold title, with optional subtitle or summary bullets.
- The marker resolves to `chapter_marker@large_number`; the title resolves to `chapter_title@standard`.
- Series normalization for these slots applies font family / bold only; size and color stay unchanged by default.

## TOC and footer safety

- A TOC secondary label such as `Contents` is `toc_title@secondary`, not the same object as the primary TOC title.
- `toc_title@secondary` is conservative and does not receive bold/color changes automatically.
- Footer text is split into `footer@org_name`, `footer@page_num`, and `footer@note`.
- Organization names and page numbers do not share one color canonical.
- Weak canonical styles may apply font family only.

## Outputs

`scan.py` writes:

- `rules.json`
- `scan_report.json`
- `scan_report.md`

`apply.py` writes:

- normalized PPTX at `--output` or under `<workdir>/output/`
- `apply_report.json`
- `apply_report.md`

## OOXML namespace preservation rule

PowerPoint slide XML may contain markup-compatibility nodes such as `mc:AlternateContent` with `Requires="p14"`. The `Requires` value depends on a matching namespace declaration like `xmlns:p14`. Raw `ElementTree.tostring(...)` can rewrite the declaration to an unstable `ns*` prefix while leaving `Requires="p14"` unchanged, causing PowerPoint to report that the PPTX needs repair and to delete repaired content.

Rules for this tool:
- Never write slide XML with raw `ET.tostring(...)`.
- Always write modified slide XML through `serialize_xml_preserving_prefixes()`.
- Always validate generated PPTX files with `validate_markup_compatibility_prefixes()` before reporting apply success.
- Regression tests must keep `Requires="p14"` paired with `xmlns:p14` and reject leaked `xmlns:ns*` prefixes.
