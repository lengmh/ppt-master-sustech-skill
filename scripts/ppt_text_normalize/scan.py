from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ppt_text_normalize.core.canonical_style import build_canonical_style
from ppt_text_normalize.core.canonical_identity import canonical_variant_for_slot
from ppt_text_normalize.core.ooxml_package import OoxmlPackage
from ppt_text_normalize.core.report_writer import write_json, write_markdown
from ppt_text_normalize.core.role_classifier import classify_slide_semantics
from ppt_text_normalize.core.text_inventory import extract_text_blocks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan a PPTX and generate normalization rules.")
    parser.add_argument("input_pptx")
    parser.add_argument("--task", required=True)
    parser.add_argument("--workdir")
    return parser


def build_rules_and_scan_report(input_name: str, slide_count: int, blocks: list) -> tuple[dict, dict]:
    blocks_by_slide: dict[int, list] = defaultdict(list)
    for block in blocks:
        blocks_by_slide[block.slide_index].append(block)

    slide_results = {
        slide_index: classify_slide_semantics(slide_index, blocks_by_slide.get(slide_index, []), slide_count)
        for slide_index in range(1, slide_count + 1)
    }

    page_rules = []
    slot_rules = []
    canonical_buckets: dict[tuple[str, str, str, str], list] = defaultdict(list)
    low_confidence_blocks = 0
    hero_page_count = 0
    hero_slot_count = 0

    for slide_index, result in slide_results.items():
        if result.hero_decision.is_frozen:
            hero_page_count += 1
        page_rules.append({
            "slide_index": slide_index,
            "resolved_page_type": result.page_type,
            "page_type_confidence": result.page_type_confidence,
            "resolved_page_submode": result.page_submode,
            "page_submode_confidence": result.page_submode_confidence,
            "hero_page_confidence": result.hero_decision.page_confidence,
            "page_normalization_mode": "frozen" if result.hero_decision.is_frozen else _page_mode_for(result.page_type),
            "source": "auto",
        })
        for block in blocks_by_slide.get(slide_index, []):
            slot = result.slot_resolutions[block.block_id]
            if slot.hero_slot_confidence >= 0.7 or slot.object_slot == "hero":
                hero_slot_count += 1
            if slot.slot_confidence < 0.55 or slot.skip_reason:
                low_confidence_blocks += 1
            slot_rules.append({
                "slide_index": slide_index,
                "block_id": block.block_id,
                "resolved_object_slot": slot.object_slot,
                "slot_confidence": slot.slot_confidence,
                "resolved_slot_variant": slot.slot_variant,
                "slot_variant_confidence": slot.slot_variant_confidence,
                "content_intent_role": slot.content_intent_role,
                "hero_slot_confidence": slot.hero_slot_confidence,
                "uniformity_eligible": slot.uniformity_eligible,
                "mutation_permission_profile": slot.mutation_permission_profile,
                "skip_reason": slot.skip_reason,
                "source": "auto",
            })
            if _eligible_for_canonical(slot):
                key = (result.page_type, slot.object_slot, _canonical_variant(slot), slot.mutation_permission_profile)
                canonical_buckets[key].append(block)

    canonical_styles = []
    for (page_type, object_slot, slot_variant, profile), members in sorted(canonical_buckets.items()):
        canonical = build_canonical_style(page_type, object_slot, slot_variant, profile, members, source="majority_real_slide")
        canonical_styles.append({
            "page_type": canonical.page_type,
            "object_slot": canonical.object_slot,
            "slot_variant": canonical.slot_variant,
            "source": canonical.source,
            "support": {
                "sample_count": canonical.sample_count,
                "core_cluster_ratio": canonical.core_cluster_ratio,
            },
            "style": {
                "font_family": canonical.style.font_family,
                "east_asia_font_family": canonical.style.east_asia_font_family,
                "color": canonical.style.color,
                "font_size_pt": canonical.style.font_size_pt,
                "bold": canonical.style.bold,
                "italic": canonical.style.italic,
            },
            "permission_profile": canonical.permission_profile,
            "weak_canonical": canonical.weak_canonical,
        })

    rules = {
        "version": "0.2",
        "input_fingerprint": {"filename": input_name, "slide_count": slide_count},
        "defaults": {
            "page_modes": {
                "hero": "frozen",
                "cover": "conservative_text",
                "toc": "conservative_text",
                "chapter": "conservative_text",
                "ending": "conservative_text",
                "content": "standard",
                "unknown": "conservative_text",
            },
            "allow_size_shrink": False,
            "max_size_shrink_pt": 0.0,
            "preserve_local_emphasis": True,
        },
        "page_rules": page_rules,
        "slot_rules": slot_rules,
        "canonical_styles": canonical_styles,
        "fallback_policy": {"order": ["apply_allowed_fields", "skip_block"]},
        "hero_policy": {"freeze_by_default": True, "page_threshold": 0.7, "slot_threshold": 0.72, "report_only": True},
    }
    report = {
        "input_fingerprint": rules["input_fingerprint"],
        "slides": page_rules,
        "summary": {
            "slide_count": slide_count,
            "text_block_count": len(blocks),
            "page_type_resolved_ratio": _resolved_ratio(page_rules, "resolved_page_type"),
            "object_slot_resolved_ratio": _resolved_ratio(slot_rules, "resolved_object_slot"),
            "hero_page_count": hero_page_count,
            "hero_slot_count": hero_slot_count,
            "low_confidence_block_ratio": low_confidence_blocks / len(blocks) if blocks else 0.0,
            "canonical_style_count": len(canonical_styles),
            "weak_canonical_count": len([item for item in canonical_styles if item["weak_canonical"]]),
        },
    }
    return rules, report


def _page_mode_for(page_type: str) -> str:
    return "standard" if page_type == "content" else "conservative_text"


def _eligible_for_canonical(slot) -> bool:
    return (
        slot.object_slot != "unknown"
        and slot.object_slot != "hero"
        and slot.slot_confidence >= 0.55
        and slot.uniformity_eligible
        and slot.mutation_permission_profile != "frozen"
        and slot.skip_reason is None
    )


def _canonical_variant(slot) -> str:
    return canonical_variant_for_slot(slot)


def _resolved_ratio(rows: list[dict], field: str) -> float:
    if not rows:
        return 0.0
    resolved = [row for row in rows if row.get(field) not in {None, "unknown"}]
    return len(resolved) / len(rows)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_pptx = Path(args.input_pptx).expanduser().resolve()
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else Path(f"/home/sustech/TempFiles/ppt_text_normalize/{args.task}")
    workdir.mkdir(parents=True, exist_ok=True)

    with OoxmlPackage(input_pptx) as pkg:
        slides = list(pkg.iter_slides())
        blocks = extract_text_blocks(pkg)
        rules, scan_report = build_rules_and_scan_report(input_pptx.name, len(slides), blocks)

    write_json(workdir / "rules.json", rules)
    write_json(workdir / "scan_report.json", scan_report)
    write_markdown(workdir / "scan_report.md", [
        "# Scan Report",
        "",
        f"- Input: {input_pptx.name}",
        f"- Slides: {scan_report['summary']['slide_count']}",
        f"- Text blocks: {scan_report['summary']['text_block_count']}",
        f"- Canonical styles: {scan_report['summary']['canonical_style_count']}",
        f"- Hero pages: {scan_report['summary']['hero_page_count']}",
        f"- Hero slots: {scan_report['summary']['hero_slot_count']}",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
