#!/usr/bin/env python3
"""Optional browser geometry probe for SVG layout-quality diagnostics.

The probe is diagnostic only. It renders SVGs in Chromium when explicitly
invoked, measures real browser geometry, and emits the same issue schema as the
static checker. It never edits SVG, PPTX, design_spec.md, or spec_lock.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from svg_quality_checker import LayoutQualityHeuristics


# ponytail: keep optional browser probe while static SVG checks cannot catch rendered geometry regressions; revisit after CI has equivalent rendered overlap/overflow coverage.
def playwright_missing_message() -> str:
    return (
        "Python package 'playwright' is not installed. Run this optional probe with:\n"
        "  uv run --with playwright python scripts/svg_layout_probe.py ..."
    )


def chromium_missing_message() -> str:
    return (
        "Chromium browser binaries for Playwright are missing. Install them with:\n"
        "  uv run --with playwright python -m playwright install chromium"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_path",
        nargs="?",
        help="Project root containing svg_output/; omitted when --fixture-mode is used.",
    )
    parser.add_argument(
        "--fixture-mode",
        dest="fixture_mode",
        help="Measure a local SVG file or directory directly. Intended for synthetic tests only.",
    )
    parser.add_argument(
        "--pages",
        nargs="+",
        default=None,
        help="Project-mode page tokens to measure, e.g. 02 or 02_title.svg.",
    )
    parser.add_argument(
        "--server-url",
        default="http://localhost:5050",
        help="Live-preview server URL for project mode.",
    )
    parser.add_argument("--output", help="Write JSON report to this path.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    return parser.parse_args(argv)


def discover_targets(args: argparse.Namespace) -> list[Path]:
    if args.fixture_mode:
        fixture = Path(args.fixture_mode).resolve()
        if fixture.is_file():
            if fixture.suffix.lower() != ".svg":
                raise ValueError(f"fixture-mode target is not an SVG: {fixture}")
            return [fixture]
        if fixture.is_dir():
            targets = sorted(fixture.glob("*.svg"))
            if targets:
                return targets
            raise ValueError(f"no SVG files found in fixture directory: {fixture}")
        raise ValueError(f"fixture-mode target not found: {fixture}")

    if not args.project_path:
        raise ValueError("project_path is required unless --fixture-mode is set")
    project = Path(args.project_path).resolve()
    svg_dir = project / "svg_output"
    if not svg_dir.is_dir():
        raise ValueError(f"project mode requires svg_output/ under {project}")

    all_svgs = sorted(svg_dir.glob("*.svg"))
    if not args.pages:
        return all_svgs

    selected: list[Path] = []
    for token in args.pages:
        match = next((path for path in all_svgs if path.name == token or path.stem == token or path.name.startswith(token)), None)
        if match is None:
            raise ValueError(f"no SVG matches page token {token!r} in {svg_dir}")
        selected.append(match)
    return selected


def build_report(files: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "browser",
        "files": files,
    }


def check_server(server_url: str) -> None:
    url = f"{server_url.rstrip('/')}/api/slides"
    try:
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            if resp.status != 200:
                raise RuntimeError(f"{url} returned HTTP {resp.status}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"live-preview server not reachable at {server_url}: {exc}") from exc


MEASURE_JS = """
() => {
  function localName(el) { return (el.tagName || '').toLowerCase().split(':').pop(); }
  function num(v) {
    const n = parseFloat(v || '');
    return Number.isFinite(n) ? n : null;
  }
  function boxFor(el) {
    try {
      const b = el.getBBox();
      return {x: b.x, y: b.y, width: b.width, height: b.height};
    } catch (e) {
      return null;
    }
  }
  function canvasBox() {
    const svg = document.querySelector('svg');
    if (!svg) return null;
    if (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width && svg.viewBox.baseVal.height) {
      const b = svg.viewBox.baseVal;
      return {x: b.x, y: b.y, width: b.width, height: b.height};
    }
    const width = num(svg.getAttribute('width'));
    const height = num(svg.getAttribute('height'));
    if (width && height) return {x: 0, y: 0, width, height};
    return null;
  }
  const texts = Array.from(document.querySelectorAll('text')).map((el, idx) => {
    const style = window.getComputedStyle(el);
    return {
      element_ref: el.id || ('text#' + (idx + 1)),
      text: (el.textContent || '').trim(),
      font_size: num(el.getAttribute('font-size')) || num(style.fontSize) || 0,
      box: boxFor(el)
    };
  }).filter(item => item.box && item.text);
  const shapes = Array.from(document.querySelectorAll('rect,image')).map((el, idx) => {
    const style = window.getComputedStyle(el);
    const attrOpacity = num(el.getAttribute('opacity'));
    const styleOpacity = num(style.opacity);
    return {
      element_ref: el.id || (localName(el) + '#' + (idx + 1)),
      kind: localName(el),
      role: (el.getAttribute('data-layout-role') || el.getAttribute('data-role') || '').trim().toLowerCase(),
      aria_hidden: (el.getAttribute('aria-hidden') || '').trim().toLowerCase(),
      opacity: attrOpacity !== null ? attrOpacity : (styleOpacity !== null ? styleOpacity : 1),
      box: boxFor(el)
    };
  }).filter(item => item.box);
  return {canvas: canvasBox(), texts, shapes};
}
"""


INJECT_PROJECT_SVG_JS = """
async (pageName) => {
  const res = await fetch('/api/slide/' + pageName + '?_=' + Date.now());
  if (!res.ok) throw new Error('fetch /api/slide/' + pageName + ' returned ' + res.status);
  const data = await res.json();
  document.documentElement.innerHTML =
    '<head><style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}svg{display:block}</style></head>'
    + '<body>' + data.content + '</body>';
  return {len: data.content.length};
}
"""


def measure_fixture_targets(targets: list[Path], sync_playwright: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            for target in targets:
                page = context.new_page()
                svg = target.read_text(encoding="utf-8")
                page.set_content(
                    "<html><body style='margin:0'>" + svg + "</body></html>",
                    wait_until="domcontentloaded",
                )
                measured = page.evaluate(MEASURE_JS)
                page.close()
                records.append(_record_from_measurement(target.name, str(target), measured))
        finally:
            browser.close()
    return records


def measure_project_targets(
    targets: list[Path],
    server_url: str,
    sync_playwright: Any,
) -> list[dict[str, Any]]:
    check_server(server_url)
    records: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            for target in targets:
                page = context.new_page()
                page.goto(server_url, wait_until="domcontentloaded")
                page.evaluate(INJECT_PROJECT_SVG_JS, target.name)
                measured = page.evaluate(MEASURE_JS)
                page.close()
                records.append(_record_from_measurement(target.name, str(target), measured))
        finally:
            browser.close()
    return records


def _record_from_measurement(file_name: str, path: str, measured: dict[str, Any]) -> dict[str, Any]:
    return {
        "file": file_name,
        "path": path,
        "issues": _detect_browser_issues(measured),
    }


def _detect_browser_issues(measured: dict[str, Any]) -> list[dict[str, Any]]:
    heuristics = LayoutQualityHeuristics()
    issues: list[dict[str, Any]] = []
    texts = measured.get("texts") or []
    canvas = measured.get("canvas")
    shapes = [
        shape for shape in (measured.get("shapes") or [])
        if not _is_browser_decorative(shape, canvas, heuristics)
    ]

    for text in texts:
        font_size = float(text.get("font_size") or 0)
        if font_size and font_size < heuristics.min_readable_font_px:
            issues.append(_issue("font_too_small", text["element_ref"], "Font size appears too small for comfortable reading."))
        if font_size > heuristics.oversized_body_font_px:
            issues.append(_issue("font_too_large", text["element_ref"], "Font size appears oversized relative to common slide text usage."))

        container = _infer_browser_container(text.get("box"), shapes, heuristics)
        if container:
            box = text["box"]
            cbox = container["box"]
            if (
                box["width"] > cbox["width"] + heuristics.container_overflow_tolerance_px
                or box["height"] > cbox["height"] + heuristics.container_overflow_tolerance_px
            ):
                issue = _issue("overflow", text["element_ref"], "Text likely overflows its inferred container.")
                issue["container_ref"] = container["element_ref"]
                issue["bbox"] = box
                issue["container_bbox"] = cbox
                issues.append(issue)

    for left_index, left in enumerate(shapes):
        if left.get("role") == "image":
            continue
        for right in shapes[left_index + 1:]:
            if right.get("role") == "image":
                continue
            ratio = _intersection_ratio(left["box"], right["box"])
            if ratio > heuristics.overlap_area_ratio:
                issue_id = "card_collision" if left["kind"] == right["kind"] == "rect" else "element_overlap"
                issue = _issue(issue_id, left["element_ref"], "Content-like elements overlap beyond the layout tolerance.")
                issue["container_ref"] = right["element_ref"]
                issues.append(issue)
    return issues


def _is_browser_decorative(
    shape: dict[str, Any],
    canvas: dict[str, float] | None,
    heuristics: LayoutQualityHeuristics,
) -> bool:
    role = str(shape.get("role") or "").strip().lower()
    if role in {"decorative", "background"} or shape.get("aria_hidden") == "true":
        return True

    opacity = float(shape.get("opacity") if shape.get("opacity") is not None else 1)
    if opacity <= heuristics.decorative_opacity_max:
        return True

    box = shape.get("box") or {}
    box_area = max(0.0, float(box.get("width") or 0)) * max(0.0, float(box.get("height") or 0))
    if not canvas:
        return False

    canvas_area = max(0.0, float(canvas.get("width") or 0)) * max(0.0, float(canvas.get("height") or 0))
    if canvas_area <= 0:
        return False

    area_ratio = box_area / canvas_area
    if area_ratio <= heuristics.tiny_area_ratio:
        return True
    return (
        area_ratio >= heuristics.background_coverage_ratio
        and float(box.get("x") or 0) <= float(canvas.get("x") or 0) + heuristics.container_overflow_tolerance_px
        and float(box.get("y") or 0) <= float(canvas.get("y") or 0) + heuristics.container_overflow_tolerance_px
    )


def _issue(issue_id: str, element_ref: str, message: str) -> dict[str, Any]:
    return {
        "id": issue_id,
        "severity": "warning",
        "source": "browser",
        "element_ref": element_ref,
        "message": message,
        "suggestion": "Manual review needed; this probe does not modify layout.",
        "confidence": "high",
        "probe_recommended": False,
    }


def _infer_browser_container(
    text_box: dict[str, float] | None,
    shapes: list[dict[str, Any]],
    heuristics: LayoutQualityHeuristics,
) -> dict[str, Any] | None:
    if not text_box:
        return None
    candidates = []
    for shape in shapes:
        box = shape.get("box")
        if not box:
            continue
        if (
            box["x"] - heuristics.container_overflow_tolerance_px <= text_box["x"] <= box["x"] + box["width"] + heuristics.container_overflow_tolerance_px
            and box["y"] - heuristics.container_overflow_tolerance_px <= text_box["y"] <= box["y"] + box["height"] + heuristics.container_overflow_tolerance_px
        ):
            candidates.append(shape)
    if not candidates:
        return None
    return min(candidates, key=lambda shape: max(0, shape["box"]["width"]) * max(0, shape["box"]["height"]))


def _intersection_ratio(left: dict[str, float], right: dict[str, float]) -> float:
    x1 = max(left["x"], right["x"])
    y1 = max(left["y"], right["y"])
    x2 = min(left["x"] + left["width"], right["x"] + right["width"])
    y2 = min(left["y"] + left["height"], right["y"] + right["height"])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    intersection = (x2 - x1) * (y2 - y1)
    smaller = min(left["width"] * left["height"], right["width"] * right["height"])
    if smaller <= 0:
        return 0.0
    return intersection / smaller


def _is_chromium_missing(exc: Exception) -> bool:
    message = str(exc).lower()
    return "executable doesn't exist" in message or "playwright install" in message


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        targets = discover_targets(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(playwright_missing_message(), file=sys.stderr)
        return 3

    try:
        if args.fixture_mode:
            records = measure_fixture_targets(targets, sync_playwright)
        else:
            records = measure_project_targets(targets, args.server_url, sync_playwright)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        if _is_chromium_missing(exc):
            print(chromium_missing_message(), file=sys.stderr)
        else:
            print(f"browser probe failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    payload = build_report(records)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
