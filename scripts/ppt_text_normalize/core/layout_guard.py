from __future__ import annotations

from .model import LayoutRiskAssessment, StyleFingerprint, TextBlock


def assess_layout_risk(block: TextBlock, target: StyleFingerprint) -> LayoutRiskAssessment:
    reasons: list[str] = []
    current_size = block.style.font_size_pt or 0
    target_size = target.font_size_pt or current_size
    if target.font_family and block.style.font_family and target.font_family != block.style.font_family:
        reasons.append("font_family_width_risk")
    if target_size > current_size and block.width and len(block.text) * target_size > block.width * 0.9:
        reasons.append("near_capacity_risk")
    if (block.paragraph_count or block.paragraphs) > 1:
        reasons.append("multi_paragraph_height_risk")
    level = "low"
    if len(reasons) >= 2:
        level = "high"
    elif reasons:
        level = "medium"
    return LayoutRiskAssessment(level=level, reasons=tuple(reasons))
