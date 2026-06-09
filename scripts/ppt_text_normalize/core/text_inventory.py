from __future__ import annotations

from collections import defaultdict
from xml.etree import ElementTree as ET

from .model import StyleFingerprint, TextBlock, TextRunStyle
from .ooxml_package import NS, OoxmlPackage, SlideRef


def extract_text_blocks(pkg: OoxmlPackage) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    for slide in pkg.iter_slides():
        blocks.extend(_extract_slide_text_blocks(slide))
    return blocks


def index_blocks_by_slide(blocks: list[TextBlock]) -> dict[int, list[TextBlock]]:
    grouped: dict[int, list[TextBlock]] = defaultdict(list)
    for block in blocks:
        grouped[block.slide_index].append(block)
    return dict(grouped)


def _extract_slide_text_blocks(slide: SlideRef) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    sp_tree = slide.part.xml.find("p:cSld/p:spTree", NS)
    if sp_tree is None:
        return blocks
    shape_counter = 0
    table_counter = 0
    for child in list(sp_tree):
        tag = child.tag.rsplit("}", 1)[-1] if isinstance(child.tag, str) else ""
        if tag == "sp":
            shape_counter += 1
            block = _extract_shape_block(slide.index, shape_counter, child)
            if block is not None:
                blocks.append(block)
        elif tag == "graphicFrame":
            table = child.find("a:graphic/a:graphicData/a:tbl", NS)
            if table is None:
                continue
            table_counter += 1
            blocks.extend(_extract_table_blocks(slide.index, table_counter, child, table))
    return blocks


def _extract_shape_block(slide_index: int, shape_index: int, sp: ET.Element) -> TextBlock | None:
    tx_body = sp.find("p:txBody", NS)
    if tx_body is None:
        return None
    text = _collect_text(tx_body)
    if not text:
        return None
    placeholder = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
    xfrm = sp.find("p:spPr/a:xfrm", NS)
    left, top, width, height = _extract_geometry(xfrm)
    paragraphs = tx_body.findall("a:p", NS)
    runs: list[TextRunStyle] = []
    for para in paragraphs:
        runs.extend(_extract_runs(para))
    source_level = "run" if runs else "paragraph"
    style = _summarize_style(runs)
    return TextBlock(
        block_id=f"s{slide_index:02d}_sp{shape_index:02d}",
        slide_index=slide_index,
        container_type="placeholder" if placeholder is not None else "textbox",
        text=text,
        shape_name=None,
        placeholder_type=placeholder.attrib.get("type") if placeholder is not None else None,
        left=left,
        top=top,
        width=width,
        height=height,
        paragraphs=len(paragraphs),
        paragraph_count=len(paragraphs),
        run_count=len(runs),
        source_level=source_level,
        style=style,
        runs=tuple(runs),
    )


def _extract_table_blocks(slide_index: int, table_index: int, graphic_frame: ET.Element, table: ET.Element) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    xfrm = graphic_frame.find("p:xfrm", NS)
    left, top, width, height = _extract_geometry(xfrm)
    rows = table.findall("a:tr", NS)
    cell_boxes, unsupported_reason = _table_cell_boxes(left, top, width, height, table, rows)
    for r_idx, row in enumerate(rows, start=1):
        cells = row.findall("a:tc", NS)
        for c_idx, cell in enumerate(cells, start=1):
            text = _collect_text(cell)
            if not text:
                continue
            paragraphs = cell.findall("a:txBody/a:p", NS)
            runs: list[TextRunStyle] = []
            for para in paragraphs:
                runs.extend(_extract_runs(para))
            style = _summarize_style(runs)
            cell_left, cell_top, cell_width, cell_height = cell_boxes.get((r_idx, c_idx), (left, top, width, height))
            blocks.append(
                TextBlock(
                    block_id=f"s{slide_index:02d}_tbl{table_index:02d}_r{r_idx}_c{c_idx}",
                    slide_index=slide_index,
                    container_type="table_cell",
                    text=text,
                    left=cell_left,
                    top=cell_top,
                    width=cell_width,
                    height=cell_height,
                    paragraphs=len(paragraphs),
                    paragraph_count=len(paragraphs),
                    run_count=len(runs),
                    source_level="run" if runs else "paragraph",
                    unsupported_reason=unsupported_reason,
                    style=style,
                    runs=tuple(runs),
                )
            )
    return blocks


def _table_cell_boxes(
    left: int,
    top: int,
    width: int,
    height: int,
    table: ET.Element,
    rows: list[ET.Element],
) -> tuple[dict[tuple[int, int], tuple[int, int, int, int]], str | None]:
    """Return per-cell EMU boxes for simple non-merged tables.

    Merged cells are intentionally fail-closed for visual review: the text is
    still reported, but the review layer must not pretend a reliable
    independent cell box exists.
    """
    cells_by_key: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    grid_cols = table.findall("a:tblGrid/a:gridCol", NS)
    col_widths = [_safe_int(col.attrib.get("w"), 0) for col in grid_cols]
    row_heights = [_safe_int(row.attrib.get("h"), 0) for row in rows]
    unsupported = None
    if not col_widths or not row_heights or width <= 0 or height <= 0:
        unsupported = "table_cell_unresolved_geometry"
    for row in rows:
        for cell in row.findall("a:tc", NS):
            if any(cell.attrib.get(attr) not in {None, "0", "false"} for attr in ("gridSpan", "rowSpan", "hMerge", "vMerge")):
                unsupported = "table_cell_unresolved_geometry"

    if unsupported:
        return cells_by_key, unsupported

    intrinsic_w = sum(col_widths)
    intrinsic_h = sum(row_heights)
    if intrinsic_w <= 0 or intrinsic_h <= 0:
        return cells_by_key, "table_cell_unresolved_geometry"
    scaled_cols = _scale_lengths(col_widths, width)
    scaled_rows = _scale_lengths(row_heights, height)
    col_starts = _starts(left, scaled_cols)
    row_starts = _starts(top, scaled_rows)
    for r_idx, row in enumerate(rows, start=1):
        cells = row.findall("a:tc", NS)
        if len(cells) != len(scaled_cols):
            return {}, "table_cell_unresolved_geometry"
        for c_idx, _cell in enumerate(cells, start=1):
            cells_by_key[(r_idx, c_idx)] = (col_starts[c_idx - 1], row_starts[r_idx - 1], scaled_cols[c_idx - 1], scaled_rows[r_idx - 1])
    return cells_by_key, None


def _scale_lengths(lengths: list[int], target_total: int) -> list[int]:
    total = sum(lengths)
    if total <= 0:
        return [0 for _ in lengths]
    scaled = [int(round(value * target_total / total)) for value in lengths]
    if scaled:
        scaled[-1] += target_total - sum(scaled)
    return scaled


def _starts(origin: int, lengths: list[int]) -> list[int]:
    starts: list[int] = []
    current = origin
    for length in lengths:
        starts.append(current)
        current += length
    return starts


def _collect_text(root: ET.Element) -> str:
    parts = []
    for node in root.findall(".//a:t", NS):
        if node.text:
            value = node.text.strip()
            if value:
                parts.append(value)
    return "\n".join(parts)


def _extract_geometry(xfrm: ET.Element | None) -> tuple[int, int, int, int]:
    if xfrm is None:
        return 0, 0, 0, 0
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return 0, 0, 0, 0
    return (
        int(off.attrib.get("x", "0") or 0),
        int(off.attrib.get("y", "0") or 0),
        int(ext.attrib.get("cx", "0") or 0),
        int(ext.attrib.get("cy", "0") or 0),
    )


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def _extract_runs(paragraph: ET.Element) -> list[TextRunStyle]:
    runs: list[TextRunStyle] = []
    for run in paragraph.findall("a:r", NS):
        rpr = run.find("a:rPr", NS)
        runs.append(_run_style_from_rpr(rpr))
    if not runs:
        end = paragraph.find("a:endParaRPr", NS)
        if end is not None:
            runs.append(_run_style_from_rpr(end))
    return runs


def _run_style_from_rpr(rpr: ET.Element | None) -> TextRunStyle:
    if rpr is None:
        return TextRunStyle()
    latin = rpr.find("a:latin", NS)
    ea = rpr.find("a:ea", NS)
    color = rpr.find("a:solidFill/a:srgbClr", NS)
    size = rpr.attrib.get("sz")
    font_size_pt = round(int(size) / 100, 2) if size and size.isdigit() else None
    return TextRunStyle(
        font_family=latin.attrib.get("typeface") if latin is not None else None,
        east_asia_font=ea.attrib.get("typeface") if ea is not None else None,
        color=f"#{color.attrib['val']}" if color is not None and color.attrib.get("val") else None,
        font_size_pt=font_size_pt,
        bold=rpr.attrib.get("b") == "1" if "b" in rpr.attrib else None,
        italic=rpr.attrib.get("i") == "1" if "i" in rpr.attrib else None,
    )


def _summarize_style(runs: list[TextRunStyle]) -> StyleFingerprint:
    for run in runs:
        if any([
            run.font_family is not None,
            run.color is not None,
            run.font_size_pt is not None,
            run.bold is not None,
            run.italic is not None,
        ]):
            return StyleFingerprint(
                font_family=run.font_family or run.east_asia_font,
                east_asia_font_family=run.east_asia_font,
                color=run.color,
                font_size_pt=run.font_size_pt,
                bold=run.bold,
                italic=run.italic,
                source_level="run",
            )
    return StyleFingerprint(source_level="paragraph")
