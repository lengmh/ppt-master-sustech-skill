from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from .ooxml_package import OoxmlPackage
from .report_writer import write_json
from .review_model import build_review_model_payload
from .text_inventory import extract_text_blocks

try:
    from pptx_to_svg.converter import ConvertOptions, convert_pptx_to_svg
except ImportError:  # pragma: no cover
    ConvertOptions = None
    convert_pptx_to_svg = None


def build_review_workspace(input_pptx: Path, scan_dir: Path, workdir: Path) -> dict[str, Any]:
    input_pptx = Path(input_pptx).expanduser().resolve()
    scan_dir = Path(scan_dir).expanduser().resolve()
    workdir = Path(workdir).expanduser().resolve()
    rules_path = scan_dir / "rules.json"
    scan_report_path = scan_dir / "scan_report.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    workdir.mkdir(parents=True, exist_ok=True)
    flat_export_dir = workdir / "assets" / "flat_export"
    if convert_pptx_to_svg is None or ConvertOptions is None:
        raise RuntimeError("pptx_to_svg converter is not importable")
    result = convert_pptx_to_svg(
        input_pptx,
        flat_export_dir,
        ConvertOptions(inheritance_mode="flat", media_subdir="assets", asset_name_map={}),
    )

    with OoxmlPackage(input_pptx) as pkg:
        text_blocks = extract_text_blocks(pkg)
        slide_count = len(list(pkg.iter_slides()))

    slide_svg_map = {i: f"svg_output/slide_{i:02d}.svg" for i in range(1, slide_count + 1)}
    slide_background_map = {i: f"assets/flat_export/svg/slide_{i:02d}.svg" for i in range(1, slide_count + 1)}
    width, height = result.canvas_px
    slide_size_map = {i: (width, height) for i in range(1, slide_count + 1)}
    model = build_review_model_payload(
        source_pptx=str(input_pptx),
        source_rules=str(rules_path),
        source_scan_report=str(scan_report_path),
        rules=rules,
        text_blocks=text_blocks,
        slide_svg_map=slide_svg_map,
        slide_background_map=slide_background_map,
        slide_size_map=slide_size_map,
    )
    write_json(workdir / "review_model.json", model)
    for slide in model.get("slides", []):
        write_overlay_svg(workdir / slide["svg"], model, slide)
    write_initial_review_decisions(workdir / "review_decisions.json", "review_model.json")
    return model


def write_initial_review_decisions(path: Path, review_model_path: str) -> dict[str, Any]:
    payload = {
        "artifact_type": "ppt_text_normalize_review_decisions",
        "schema_version": "0.1",
        "review_model": review_model_path,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "decisions": [],
    }
    write_json(Path(path), payload)
    return payload


def write_overlay_svg(path: Path, review_model: dict[str, Any], slide: dict[str, Any]) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    slide_index = slide["slide_index"]
    width = slide.get("width") or 1280
    height = slide.get("height") or 720
    workspace_root = path.parent.parent
    bg_path = Path(slide["background_svg"])
    bg = _relative_href(path.parent, bg_path if bg_path.is_absolute() else workspace_root / bg_path)
    group_color = {group["group_id"]: group.get("color", "#9CA3AF") for group in review_model.get("groups", [])}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" data-normalization-review="true">',
        '<style>.normalization-review-overlay{cursor:pointer}.status-unsupported{pointer-events:none;opacity:.55}</style>',
        f'<image href="{escape(bg)}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="none"/>',
        '<g id="normalization-review-overlays">',
    ]
    for block in review_model.get("blocks", []):
        if block.get("slide_index") != slide_index:
            continue
        geom = block.get("geometry") or {}
        x = geom.get("x", 0)
        y = geom.get("y", 0)
        w = geom.get("width", 0)
        h = geom.get("height", 0)
        if not w or not h:
            continue
        status = block.get("status") or "skipped"
        group_id = block.get("planned_group_id") or block.get("auto_group_id")
        color = group_color.get(group_id, "#9CA3AF")
        fill = color if status == "planned_change" else "#D1D5DB"
        opacity = "0.22" if status == "planned_change" else "0.14"
        dash = ' stroke-dasharray="6 4"' if status in {"unchanged_selectable", "frozen", "skipped", "unsupported"} else ""
        css_status = f"status-{status}"
        safe_id = _safe_id(block["block_id"])
        parts.append(
            f'<g id="review_block_{safe_id}" class="normalization-review-overlay {css_status}" '
            f'data-review-block-id="{escape(block["block_id"])}" data-review-status="{escape(status)}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" ry="4" fill="{fill}" fill-opacity="{opacity}" stroke="{color}" stroke-width="2"{dash}/>'
            '</g>'
        )
    parts.extend(['</g>', '</svg>'])
    svg = "\n".join(parts)
    path.write_text(svg, encoding="utf-8")
    return svg


def _relative_href(from_dir: Path, target: Path) -> str:
    import os
    return os.path.relpath(target, from_dir).replace("\\", "/")


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value)
