#!/usr/bin/env python3
"""Export a template-library preview workspace for Step 5.5 feedback.

Creates a timestamped workspace under the caller's current working directory,
stages template SVGs and assets into a project-like structure, then reuses
`finalize_svg.py` to produce `svg_final/` for visual review.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys

from finalize_svg import finalize_project

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
IMAGE_HREF_RE = re.compile(r'(?:xlink:href|href)\s*=\s*["\']?(?!data:)([^"\'\s>]+\.(?:png|jpg|jpeg|gif|webp))["\']?', re.IGNORECASE)


def build_preview_workspace_name(template_id: str, stamp: str) -> str:
    return f"{template_id}_template_preview_{stamp}"




def svg_file_has_only_embedded_images(svg_path: Path) -> bool:
    content = Path(svg_path).read_text(encoding="utf-8")
    return IMAGE_HREF_RE.search(content) is None

def export_template_preview(template_dir: Path, output_root: Path | None = None) -> Path:
    template_dir = Path(template_dir)
    if output_root is None:
        output_root = Path.cwd()
    output_root = Path(output_root)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = output_root / build_preview_workspace_name(template_dir.name, stamp)
    svg_output = workspace / "svg_output"
    svg_output.mkdir(parents=True, exist_ok=False)

    copied_svgs = 0
    for file in sorted(template_dir.iterdir()):
        if file.is_dir():
            continue
        suffix = file.suffix.lower()
        if suffix == ".svg":
            shutil.copy2(file, svg_output / file.name)
            copied_svgs += 1
        elif suffix in IMAGE_SUFFIXES:
            # Keep image assets beside the raw SVGs so relative href="foo.png"
            # references still resolve during finalize_svg.py. The copied
            # svg_output tree will then be embedded into svg_final/ as base64.
            shutil.copy2(file, svg_output / file.name)
        elif file.name in {"design_spec.md", "brief_lock.json"}:
            shutil.copy2(file, workspace / file.name)

    if copied_svgs == 0:
        raise RuntimeError(f"no SVG files found in template directory: {template_dir}")

    ok = finalize_project(
        workspace,
        {
            "embed_icons": True,
            "align_images": True,
            "flatten_text": False,
            "fix_rounded": False,
        },
        quiet=True,
    )
    if not ok:
        raise RuntimeError("preview export failed")

    svg_final = workspace / "svg_final"
    unembedded = [svg.name for svg in sorted(svg_final.glob("*.svg")) if not svg_file_has_only_embedded_images(svg)]
    if unembedded:
        raise RuntimeError(f"preview svg_final contains non-embedded image references: {unembedded}")
    return workspace


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a timestamped svg_final preview workspace for a template")
    parser.add_argument("template_dir", type=Path, help="Template directory under templates/layouts/")
    parser.add_argument("--output-root", type=Path, default=None, help="Where to create the preview workspace (default: current working directory)")
    args = parser.parse_args()

    workspace = export_template_preview(args.template_dir, output_root=args.output_root)
    print(f"[OK] Preview workspace exported: {workspace}")
    print(f"[OK] Review svg_final here: {workspace / 'svg_final'}")
    print("[OK] svg_final image references are embedded as base64 data URIs for direct-open preview")
    sys.exit(0)


if __name__ == "__main__":
    main()
