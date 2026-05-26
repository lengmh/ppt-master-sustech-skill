from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree as ET

from .model import LayoutRiskAssessment, StyleFingerprint, TextBlock
from .ooxml_package import NS


@dataclass(frozen=True)
class ApplyPlan:
    result: str
    steps: tuple[str, ...]
    applied_fields: tuple[str, ...]
    preserved_fields: tuple[str, ...]
    shrink_delta_pt: float = 0.0
    skip_reason: str | None = None


def choose_apply_plan(
    block: TextBlock,
    target: StyleFingerprint,
    risk: LayoutRiskAssessment,
    *,
    allowed_fields: tuple[str, ...],
    freeze_reason: str | None = None,
) -> ApplyPlan:
    if freeze_reason:
        return ApplyPlan("frozen", ("freeze_block",), (), ("font_family", "color", "font_size_pt", "bold", "italic"), 0.0, freeze_reason)
    if not allowed_fields:
        return ApplyPlan("skipped", ("skip_block",), (), ("font_family", "color", "font_size_pt", "bold", "italic"), 0.0, "permission_profile_all_fields_blocked")

    applied: list[str] = []
    preserved: list[str] = []
    steps = ["apply_allowed_fields"]
    if "font_family" in allowed_fields and (target.font_family or target.east_asia_font_family):
        applied.append("font_family")
    else:
        preserved.append("font_family")
    if "color" in allowed_fields and target.color:
        applied.append("color")
    else:
        preserved.append("color")
    if "font_size_pt" in allowed_fields and target.font_size_pt is not None and risk.level == "low":
        applied.append("font_size_pt")
    else:
        preserved.append("font_size_pt")
    if "bold" in allowed_fields and target.bold is not None:
        applied.append("bold")
    else:
        preserved.append("bold")
    if "italic" in allowed_fields and target.italic is not None:
        applied.append("italic")
    else:
        preserved.append("italic")

    if not applied:
        return ApplyPlan("skipped", tuple(steps + ["skip_block"]), (), tuple(preserved), 0.0, "no_allowed_target_fields")
    result = "applied" if risk.level != "high" else "applied_with_fallback"
    return ApplyPlan(result, tuple(steps), tuple(applied), tuple(preserved))


def apply_plan_to_slide_xml(slide_xml: ET.Element, block_id: str, target: StyleFingerprint, plan: ApplyPlan) -> bool:
    if not plan.applied_fields:
        return False
    if block_id.startswith("s") and "_sp" in block_id:
        return _apply_to_shape(slide_xml, block_id, target, plan)
    if "_tbl" in block_id:
        return _apply_to_table_cell(slide_xml, block_id, target, plan)
    return False


def _apply_to_shape(slide_xml: ET.Element, block_id: str, target: StyleFingerprint, plan: ApplyPlan) -> bool:
    sp_tree = slide_xml.find("p:cSld/p:spTree", NS)
    if sp_tree is None:
        return False
    shape_idx = int(block_id.split("_sp", 1)[1])
    current = 0
    for child in list(sp_tree):
        tag = child.tag.rsplit("}", 1)[-1] if isinstance(child.tag, str) else ""
        if tag != "sp":
            continue
        current += 1
        if current == shape_idx:
            _mutate_text_container(child.find("p:txBody", NS), target, plan)
            return True
    return False


def _apply_to_table_cell(slide_xml: ET.Element, block_id: str, target: StyleFingerprint, plan: ApplyPlan) -> bool:
    sp_tree = slide_xml.find("p:cSld/p:spTree", NS)
    if sp_tree is None:
        return False
    tail = block_id.split("_tbl", 1)[1]
    table_idx_str, rest = tail.split("_r", 1)
    row_idx_str, col_idx_str = rest.split("_c", 1)
    table_idx = int(table_idx_str)
    row_idx = int(row_idx_str)
    col_idx = int(col_idx_str)
    current = 0
    for child in list(sp_tree):
        tag = child.tag.rsplit("}", 1)[-1] if isinstance(child.tag, str) else ""
        if tag != "graphicFrame":
            continue
        table = child.find("a:graphic/a:graphicData/a:tbl", NS)
        if table is None:
            continue
        current += 1
        if current != table_idx:
            continue
        rows = table.findall("a:tr", NS)
        if row_idx - 1 >= len(rows):
            return False
        cells = rows[row_idx - 1].findall("a:tc", NS)
        if col_idx - 1 >= len(cells):
            return False
        _mutate_text_container(cells[col_idx - 1].find("a:txBody", NS), target, plan)
        return True
    return False


def _mutate_text_container(tx_body: ET.Element | None, target: StyleFingerprint, plan: ApplyPlan) -> None:
    if tx_body is None:
        return
    for para in tx_body.findall("a:p", NS):
        runs = para.findall("a:r", NS)
        if runs:
            for run in runs:
                rpr = run.find("a:rPr", NS)
                if rpr is None:
                    rpr = ET.SubElement(run, f"{{{NS['a']}}}rPr")
                _apply_target_to_rpr(rpr, target, plan)
        else:
            end = para.find("a:endParaRPr", NS)
            if end is None:
                end = ET.SubElement(para, f"{{{NS['a']}}}endParaRPr")
            _apply_target_to_rpr(end, target, plan)


def _apply_target_to_rpr(rpr: ET.Element, target: StyleFingerprint, plan: ApplyPlan) -> None:
    if "color" in plan.applied_fields and target.color:
        solid = rpr.find("a:solidFill", NS)
        if solid is None:
            solid = ET.SubElement(rpr, f"{{{NS['a']}}}solidFill")
        srgb = solid.find("a:srgbClr", NS)
        if srgb is None:
            srgb = ET.SubElement(solid, f"{{{NS['a']}}}srgbClr")
        srgb.set("val", target.color.lstrip("#"))
    if "font_family" in plan.applied_fields:
        if target.font_family:
            latin = _find_or_insert_rpr_child(rpr, "latin")
            latin.set("typeface", target.font_family)
        if target.east_asia_font_family:
            ea = _find_or_insert_rpr_child(rpr, "ea")
            ea.set("typeface", target.east_asia_font_family)
    if "font_size_pt" in plan.applied_fields and target.font_size_pt is not None:
        size_pt = max(target.font_size_pt - plan.shrink_delta_pt, 1)
        rpr.set("sz", str(int(round(size_pt * 100))))
    if target.bold is not None and "bold" in plan.applied_fields:
        rpr.set("b", "1" if target.bold else "0")
    if target.italic is not None and "italic" in plan.applied_fields:
        rpr.set("i", "1" if target.italic else "0")

_RPR_CHILD_ORDER = {
    "ln": 0,
    "noFill": 1,
    "solidFill": 2,
    "gradFill": 3,
    "blipFill": 4,
    "pattFill": 5,
    "grpFill": 6,
    "effectLst": 7,
    "effectDag": 8,
    "highlight": 9,
    "uLnTx": 10,
    "uLn": 11,
    "uFillTx": 12,
    "uFill": 13,
    "latin": 14,
    "ea": 15,
    "cs": 16,
    "sym": 17,
    "hlinkClick": 18,
    "hlinkMouseOver": 19,
    "rtl": 20,
    "extLst": 21,
}


def _find_or_insert_rpr_child(rpr: ET.Element, local_name: str) -> ET.Element:
    existing = rpr.find(f"a:{local_name}", NS)
    if existing is not None:
        return existing
    child = ET.Element(f"{{{NS['a']}}}{local_name}")
    desired_order = _RPR_CHILD_ORDER[local_name]
    for index, current in enumerate(list(rpr)):
        current_name = current.tag.rsplit("}", 1)[-1] if isinstance(current.tag, str) else ""
        if _RPR_CHILD_ORDER.get(current_name, 999) > desired_order:
            rpr.insert(index, child)
            return child
    rpr.append(child)
    return child
