from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .canonical_identity import canonical_key_for_block, canonical_key_for_rule_entry, canonical_variant_for_slot
from .model import StyleFingerprint, TextBlock, allowed_style_fields
from .mutation_policy import effective_allowed_fields

try:
    from pptx_to_svg.emu_units import emu_to_px
except ImportError:  # pragma: no cover
    def emu_to_px(value, default=0.0):
        try:
            return float(value) / 9525
        except (TypeError, ValueError):
            return default

MVP_DEFAULT_FIELD_ORDER = ("font_family", "bold")
MVP_OPTIONAL_FIELD_ORDER = ("color",)
MVP_DISABLED_FIELDS = ("font_size_pt",)
PALETTE = ("#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#06B6D4", "#EC4899")
STYLE_FIELDS = ("font_family", "east_asia_font_family", "color", "font_size_pt", "bold", "italic")


def build_review_model_payload(
    *,
    source_pptx: str,
    source_rules: str,
    source_scan_report: str,
    rules: dict[str, Any],
    text_blocks: list[TextBlock],
    slide_svg_map: dict[int, str],
    slide_background_map: dict[int, str],
    slide_size_map: dict[int, tuple[int | float, int | float]],
) -> dict[str, Any]:
    page_by_slide = {item.get("slide_index"): item for item in rules.get("page_rules", [])}
    slot_by_block = {item.get("block_id"): item for item in rules.get("slot_rules", [])}
    canonical_by_key = {canonical_key_for_rule_entry(item): item for item in rules.get("canonical_styles", [])}

    groups_by_id: dict[str, dict[str, Any]] = {}
    blocks_payload: list[dict[str, Any]] = []

    for block in text_blocks:
        slot_rule = slot_by_block.get(block.block_id)
        page_rule = page_by_slide.get(block.slide_index)
        canonical = _canonical_for_block(page_rule, slot_rule, canonical_by_key)
        group_id = _group_id(canonical) if canonical is not None else None
        if canonical is not None and group_id not in groups_by_id:
            groups_by_id[group_id] = _group_payload(group_id, canonical, len(groups_by_id))
        blocks_payload.append(_block_payload(block, page_rule, slot_rule, canonical, group_id))

    slides = []
    for slide_index in sorted(set(slide_svg_map) | set(slide_background_map) | set(slide_size_map)):
        width, height = slide_size_map.get(slide_index, (1280, 720))
        slides.append({
            "slide_index": slide_index,
            "slide_id": f"slide_{slide_index:02d}",
            "svg": slide_svg_map.get(slide_index, f"svg_output/slide_{slide_index:02d}.svg"),
            "background_svg": slide_background_map.get(slide_index, f"assets/flat_export/svg/slide_{slide_index:02d}.svg"),
            "width": _num(width),
            "height": _num(height),
        })

    return {
        "artifact_type": "ppt_text_normalize_visual_review_model",
        "schema_version": "0.1",
        "source_pptx": source_pptx,
        "source_rules": source_rules,
        "source_scan_report": source_scan_report,
        "background_mode": "svg_flat_preview",
        "slides": slides,
        "groups": list(groups_by_id.values()),
        "blocks": blocks_payload,
    }


def _canonical_for_block(page_rule, slot_rule, canonical_by_key):
    key = canonical_key_for_block(page_rule, slot_rule)
    if key is None:
        return None
    return canonical_by_key.get(key)


def _canonical_variant(slot_rule: dict[str, Any]) -> str:
    return canonical_variant_for_slot(slot_rule)


def _group_id(canonical: dict[str, Any]) -> str:
    page_type, object_slot, slot_variant, profile = canonical_key_for_rule_entry(canonical)
    return "|".join([page_type, object_slot, slot_variant, profile])


def _group_payload(group_id: str, canonical: dict[str, Any], index: int) -> dict[str, Any]:
    page_type, object_slot, slot_variant, profile = canonical_key_for_rule_entry(canonical)
    effective = effective_allowed_fields(allowed_style_fields(profile, object_slot), canonical)
    default_fields = [field for field in MVP_DEFAULT_FIELD_ORDER if field in effective]
    optional_fields = [field for field in MVP_OPTIONAL_FIELD_ORDER if field in effective]
    return {
        "group_id": group_id,
        "label": f"{page_type} / {object_slot} / {slot_variant}",
        "source": "auto_scan",
        "color": PALETTE[index % len(PALETTE)],
        "target_style": _style_dict(canonical.get("style") or {}),
        "allowed_fields": list(effective),
        "default_fields": default_fields,
        "optional_fields": optional_fields,
        "disabled_fields": list(MVP_DISABLED_FIELDS),
        "permission_profile": profile,
        "canonical_key": {
            "page_type": page_type,
            "object_slot": object_slot,
            "slot_variant": slot_variant,
        },
    }


def _block_payload(block: TextBlock, page_rule, slot_rule, canonical, group_id: str | None) -> dict[str, Any]:
    unsupported_reason = getattr(block, "unsupported_reason", None)
    freeze_reason = _freeze_reason(page_rule, slot_rule)
    current_style = _style_dict(block.style)
    target_style = _style_dict(canonical.get("style") if canonical else {})
    allowed: tuple[str, ...] = ()
    if slot_rule:
        object_slot = str(slot_rule.get("resolved_object_slot") or "unknown")
        profile = str(slot_rule.get("mutation_permission_profile") or "conservative_text")
        allowed = effective_allowed_fields(allowed_style_fields(profile, object_slot), canonical or {}, slot_rule)
    planned_fields = [field for field in MVP_DEFAULT_FIELD_ORDER if field in allowed]
    planned_diff = _planned_diff(current_style, target_style, planned_fields)
    status = _status(unsupported_reason, freeze_reason, slot_rule, canonical, planned_diff)
    if status in {"unsupported", "skipped"}:
        planned_group_id = None
        planned_fields = []
        planned_diff = {}
    else:
        planned_group_id = group_id
    return {
        "block_id": block.block_id,
        "slide_index": block.slide_index,
        "container_type": block.container_type,
        "text_preview": _text_preview(block.text),
        "geometry": {
            "x": _num(emu_to_px(block.left)),
            "y": _num(emu_to_px(block.top)),
            "width": _num(emu_to_px(block.width)),
            "height": _num(emu_to_px(block.height)),
        },
        "current_style": current_style,
        "auto_group_id": group_id,
        "planned_group_id": planned_group_id,
        "planned_fields": planned_fields,
        "allowed_fields": list(allowed),
        "planned_diff": planned_diff,
        "status": status,
        "frozen": status == "frozen",
        "skip_reason": (slot_rule or {}).get("skip_reason") if slot_rule else None,
        "permission_profile": (slot_rule or {}).get("mutation_permission_profile"),
        "unsupported_reason": unsupported_reason,
    }


def _status(unsupported_reason, freeze_reason, slot_rule, canonical, planned_diff) -> str:
    if unsupported_reason:
        return "unsupported"
    if freeze_reason:
        return "frozen"
    if not slot_rule or slot_rule.get("skip_reason") or canonical is None:
        return "skipped"
    if planned_diff:
        return "planned_change"
    return "unchanged_selectable"


def _freeze_reason(page_rule, slot_rule) -> str | None:
    if not slot_rule:
        return None
    if slot_rule.get("mutation_permission_profile") == "frozen":
        return str(slot_rule.get("skip_reason") or "frozen")
    try:
        hero_confidence = float(slot_rule.get("hero_slot_confidence") or 0)
    except (TypeError, ValueError):
        hero_confidence = 0.0
    if hero_confidence >= 0.72:
        return "hero_frozen"
    if page_rule and page_rule.get("page_normalization_mode") == "frozen" and slot_rule.get("resolved_object_slot") == "hero":
        return "hero_frozen"
    return None


def _planned_diff(current: dict[str, Any], target: dict[str, Any], fields: list[str]) -> dict[str, dict[str, Any]]:
    diff: dict[str, dict[str, Any]] = {}
    if "font_family" in fields:
        for field in ("font_family", "east_asia_font_family"):
            if target.get(field) is not None and current.get(field) != target.get(field):
                diff[field] = {"from": current.get(field), "to": target.get(field)}
    for field in fields:
        if field == "font_family":
            continue
        if target.get(field) is not None and current.get(field) != target.get(field):
            diff[field] = {"from": current.get(field), "to": target.get(field)}
    return diff


def _style_dict(style: StyleFingerprint | dict[str, Any] | None) -> dict[str, Any]:
    if style is None:
        data: dict[str, Any] = {}
    elif isinstance(style, StyleFingerprint):
        data = asdict(style)
    else:
        data = dict(style)
    return {field: data.get(field) for field in STYLE_FIELDS}


def _text_preview(text: str) -> str:
    one_line = " ".join(str(text or "").split())
    return one_line[:80] + ("…" if len(one_line) > 80 else "")


def _num(value: Any) -> int | float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0.0
    if abs(f - round(f)) < 1e-9:
        return int(round(f))
    return round(f, 2)
