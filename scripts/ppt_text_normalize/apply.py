from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ppt_text_normalize.core.apply_engine import apply_plan_to_slide_xml, choose_apply_plan
from ppt_text_normalize.core.canonical_identity import canonical_key_for_block, canonical_key_for_rule_entry
from ppt_text_normalize.core.layout_guard import assess_layout_risk
from ppt_text_normalize.core.model import StyleFingerprint, allowed_style_fields
from ppt_text_normalize.core.mutation_policy import effective_allowed_fields
from ppt_text_normalize.core.ooxml_package import OoxmlPackage, serialize_xml_preserving_prefixes, validate_markup_compatibility_prefixes
from ppt_text_normalize.core.report_writer import write_json, write_markdown
from ppt_text_normalize.core.text_inventory import extract_text_blocks, index_blocks_by_slide


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply text normalization rules to a PPTX.")
    parser.add_argument("input_pptx")
    parser.add_argument("--rules", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_pptx = Path(args.input_pptx).expanduser().resolve()
    rules_path = Path(args.rules).expanduser().resolve()
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    workdir = rules_path.parent
    output_path = Path(args.output).expanduser().resolve() if args.output else workdir / "output" / f"{input_pptx.stem}_normalized.pptx"

    canonical_map = _build_canonical_map(rules)
    slot_map = {entry["block_id"]: entry for entry in rules.get("slot_rules", [])}
    page_map = {entry["slide_index"]: entry for entry in rules.get("page_rules", [])}
    reviewed_overrides = rules.get("reviewed_overrides") or {}
    excluded_block_ids = set(reviewed_overrides.get("excluded_block_ids") or [])
    override_frozen_skip_block_ids = set(reviewed_overrides.get("override_frozen_skip_block_ids") or [])

    xml_overrides: dict[str, bytes] = {}
    block_reports = []
    applied_count = 0
    applied_with_fallback_count = 0
    skipped_count = 0
    frozen_count = 0

    with OoxmlPackage(input_pptx) as pkg:
        slides = list(pkg.iter_slides())
        blocks = extract_text_blocks(pkg)
        blocks_by_slide = index_blocks_by_slide(blocks)
        slide_xml_map = {slide.index: ET.fromstring(ET.tostring(slide.part.xml, encoding="utf-8")) for slide in slides}
        for slide in slides:
            slide_index = slide.index
            for block in blocks_by_slide.get(slide_index, []):
                slot_rule = slot_map.get(block.block_id)
                page_rule = page_map.get(slide_index)
                if block.block_id in excluded_block_ids:
                    empty = StyleFingerprint()
                    base = choose_apply_plan(block, empty, assess_layout_risk(block, empty), allowed_fields=(), freeze_reason=None)
                    plan = type(base)("skipped", base.steps, base.applied_fields, base.preserved_fields, 0.0, "review_excluded")
                    skipped_count += 1
                    block_reports.append(_build_block_report(block, page_rule, slot_rule, None, plan, "high"))
                    continue
                if slot_rule is None or page_rule is None:
                    empty = StyleFingerprint()
                    base = choose_apply_plan(block, empty, assess_layout_risk(block, empty), allowed_fields=(), freeze_reason=None)
                    plan = type(base)("skipped", base.steps, base.applied_fields, base.preserved_fields, 0.0, "missing_rule")
                    skipped_count += 1
                    block_reports.append(_build_block_report(block, page_rule, slot_rule, None, plan, "high"))
                    continue

                freeze_reason = slot_rule.get("skip_reason") if slot_rule.get("mutation_permission_profile") == "frozen" else None
                if slot_rule.get("hero_slot_confidence", 0.0) >= rules.get("hero_policy", {}).get("slot_threshold", 0.72):
                    freeze_reason = "hero_frozen"
                if page_rule.get("page_normalization_mode") == "frozen" and slot_rule.get("resolved_object_slot") == "hero":
                    freeze_reason = freeze_reason or "hero_frozen"
                if block.block_id in override_frozen_skip_block_ids:
                    freeze_reason = None

                object_slot = slot_rule.get("resolved_object_slot", "unknown")
                canonical_key = canonical_key_for_block(page_rule, slot_rule)
                canonical_entry = _reviewed_canonical_for_block(block.block_id, canonical_map.get(canonical_key), reviewed_overrides, canonical_map)
                if canonical_entry is None:
                    empty = StyleFingerprint()
                    plan = choose_apply_plan(block, empty, assess_layout_risk(block, empty), allowed_fields=(), freeze_reason=freeze_reason)
                    if plan.result != "frozen":
                        plan = type(plan)("skipped", plan.steps, plan.applied_fields, plan.preserved_fields, 0.0, "style_source_weak_canonical")
                    skipped_count += 1 if plan.result == "skipped" else 0
                    frozen_count += 1 if plan.result == "frozen" else 0
                    block_reports.append(_build_block_report(block, page_rule, slot_rule, None, plan, "high"))
                    continue

                target_style = StyleFingerprint(
                    font_family=canonical_entry["style"].get("font_family"),
                    east_asia_font_family=canonical_entry["style"].get("east_asia_font_family"),
                    color=canonical_entry["style"].get("color"),
                    font_size_pt=canonical_entry["style"].get("font_size_pt"),
                    bold=canonical_entry["style"].get("bold"),
                    italic=canonical_entry["style"].get("italic"),
                    source_level="canonical",
                )
                allowed_fields = _effective_allowed_fields(
                    allowed_style_fields(slot_rule.get("mutation_permission_profile", "conservative_text"), object_slot),
                    canonical_entry,
                    slot_rule,
                )
                allowed_fields = _reviewed_fields_for_block(block.block_id, allowed_fields, reviewed_overrides)
                risk = assess_layout_risk(block, target_style)
                plan = choose_apply_plan(block, target_style, risk, allowed_fields=allowed_fields, freeze_reason=freeze_reason)

                if plan.result == "applied":
                    applied_count += 1
                elif plan.result == "applied_with_fallback":
                    applied_with_fallback_count += 1
                elif plan.result == "frozen":
                    frozen_count += 1
                else:
                    skipped_count += 1
                if plan.result in {"applied", "applied_with_fallback"}:
                    apply_plan_to_slide_xml(slide_xml_map[slide_index], block.block_id, target_style, plan)
                block_reports.append(_build_block_report(block, page_rule, slot_rule, canonical_entry, plan, risk.level))
        for slide in slides:
            xml_overrides[slide.part.path] = serialize_xml_preserving_prefixes(slide_xml_map[slide.index])
        pkg.save_as(output_path, xml_overrides)

    namespace_errors = validate_markup_compatibility_prefixes(output_path)
    if namespace_errors:
        raise RuntimeError("Generated PPTX has invalid OOXML namespace prefixes: " + "; ".join(namespace_errors[:5]))

    summary = {
        "candidate_block_count": len(block_reports),
        "applied_count": applied_count,
        "applied_with_fallback_count": applied_with_fallback_count,
        "skipped_count": skipped_count,
        "frozen_count": frozen_count,
    }
    report = {
        "input_fingerprint": {
            "filename": input_pptx.name,
            "rules": str(rules_path),
        },
        "summary": summary,
        "blocks": block_reports,
    }
    write_json(workdir / "apply_report.json", report)
    write_markdown(workdir / "apply_report.md", [
        "# Apply Report",
        "",
        f"- Candidate blocks: {summary['candidate_block_count']}",
        f"- Applied: {summary['applied_count']}",
        f"- Applied with fallback: {summary['applied_with_fallback_count']}",
        f"- Skipped: {summary['skipped_count']}",
        f"- Frozen: {summary['frozen_count']}",
        f"- Output: {output_path}",
    ])
    return 0


def _build_block_report(block, page_rule, slot_rule, canonical_entry, plan, risk_level):
    target = canonical_entry.get("style", {}) if canonical_entry else {}
    return {
        "block_id": block.block_id,
        "slide_index": block.slide_index,
        "resolved_page_type": page_rule.get("resolved_page_type") if page_rule else None,
        "resolved_page_submode": page_rule.get("resolved_page_submode") if page_rule else None,
        "resolved_object_slot": slot_rule.get("resolved_object_slot") if slot_rule else None,
        "resolved_slot_variant": slot_rule.get("resolved_slot_variant") if slot_rule else None,
        "content_intent_role": slot_rule.get("content_intent_role") if slot_rule else None,
        "mutation_permission_profile": slot_rule.get("mutation_permission_profile") if slot_rule else None,
        "hero_slot_confidence": slot_rule.get("hero_slot_confidence") if slot_rule else None,
        "before_style": {
            "font_family": block.style.font_family,
            "east_asia_font_family": block.style.east_asia_font_family,
            "color": block.style.color,
            "font_size_pt": block.style.font_size_pt,
            "bold": block.style.bold,
            "italic": block.style.italic,
        },
        "target_style": {
            "font_family": target.get("font_family"),
            "east_asia_font_family": target.get("east_asia_font_family"),
            "color": target.get("color"),
            "font_size_pt": target.get("font_size_pt"),
            "bold": target.get("bold"),
            "italic": target.get("italic"),
        },
        "applied_fields": list(plan.applied_fields),
        "preserved_fields": list(plan.preserved_fields),
        "fallback_steps_used": list(plan.steps),
        "layout_risk": risk_level,
        "result": plan.result,
        "skip_reason": plan.skip_reason,
    }


def _effective_allowed_fields(allowed_fields, canonical_entry, slot_rule=None):
    return effective_allowed_fields(tuple(allowed_fields), canonical_entry, slot_rule)


def _build_canonical_map(rules):
    return {canonical_key_for_rule_entry(entry): entry for entry in rules.get("canonical_styles", [])}


def _reviewed_fields_for_block(block_id, allowed_fields, reviewed_overrides):
    block_fields = (reviewed_overrides or {}).get("block_fields", {}) or {}
    if block_id not in block_fields:
        return tuple(allowed_fields)
    requested = block_fields.get(block_id)
    if requested is None:
        return tuple(allowed_fields)
    allowed = set(allowed_fields)
    out = []
    for field in requested:
        if field == "font_size_pt":
            continue
        if field in allowed and field not in out:
            out.append(field)
    return tuple(out)


def _reviewed_canonical_for_block(block_id, canonical_entry, reviewed_overrides, canonical_map=None):
    reviewed_overrides = reviewed_overrides or {}
    group_id = (reviewed_overrides.get("block_group_assignments") or {}).get(block_id)
    user_group = (reviewed_overrides.get("user_groups") or {}).get(group_id) if group_id else None
    if user_group:
        base = dict(canonical_entry or {})
        base["style"] = dict(user_group.get("target_style") or {})
        base["weak_canonical"] = False
        return base
    if group_id and canonical_map is not None:
        parts = str(group_id).split("|")
        if len(parts) == 4:
            reassigned = canonical_map.get(tuple(parts))
            if reassigned is not None:
                return reassigned
    return canonical_entry


def _reviewed_target_for_block(block_id, canonical_entry, reviewed_overrides, canonical_map=None):
    entry = _reviewed_canonical_for_block(block_id, canonical_entry, reviewed_overrides, canonical_map)
    style = (entry or {}).get("style") or {}
    return StyleFingerprint(
        font_family=style.get("font_family"),
        east_asia_font_family=style.get("east_asia_font_family"),
        color=style.get("color"),
        font_size_pt=style.get("font_size_pt"),
        bold=style.get("bold"),
        italic=style.get("italic"),
        source_level="reviewed" if entry is not canonical_entry else "canonical",
    )


if __name__ == "__main__":
    raise SystemExit(main())
