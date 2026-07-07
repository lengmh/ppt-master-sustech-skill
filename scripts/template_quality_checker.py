#!/usr/bin/env python3
"""Template-level validator for template outputs.

Checks the structural consistency between `design_spec.md`, SVG template files,
and referenced asset files. When `brief_lock.json` exists (or
`--require-brief-lock` is passed), it also verifies the SUSTech create-template
audit lock against the generated template package. Delegates low-level template
SVG safety checks to `svg_quality_checker.py --template-mode`, while keeping
local brief-level contract validation and registrar preflight checks.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from template_brief_lock import load_brief_lock
from svg_quality_checker import SVGQualityChecker

REQUIRED_PERSONALITY_SPEC_SECTIONS = [
    "## I. Template Overview",
    "## II. Color Scheme",
    "## IV. Signature Design Elements",
    "## V. Page Roster",
]

LEGACY_SPEC_SECTIONS = [
    "## I. Template Overview",
    "## II. Canvas Specification",
    "## III. Color Scheme",
    "## IV. Typography System",
    "## V. Page Structure",
    "## VI. Page Types",
]

REQUIRED_FRONTMATTER_KEYS = {
    "category",
    "summary",
    "keywords",
    "primary_color",
    "canvas_format",
    "replication_mode",
}

CORE_TEMPLATE_FILES = [
    "01_cover.svg",
    "02_chapter.svg",
    "03_content.svg",
    "04_ending.svg",
]

PLACEHOLDER_REQUIREMENTS = {
    "01_cover.svg": ["{{TITLE}}"],
    "02_chapter.svg": ["{{CHAPTER_TITLE}}"],
    "03_content.svg": ["{{PAGE_TITLE}}"],
}

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def _frontmatter_id(frontmatter: dict[str, Any], kind: str | None = None) -> Any:
    """Return the declared template id from current or legacy frontmatter."""
    if kind in {"brand", "layout", "deck"}:
        value = frontmatter.get(f"{kind}_id")
        if value is not None:
            return value
    for key in ("template_id", "deck_id", "layout_id", "brand_id"):
        value = frontmatter.get(key)
        if value is not None:
            return value
    return None


def _read_spec(spec_path: Path) -> tuple[str | None, str]:
    text = spec_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5:]


def _parse_frontmatter_block(block: str | None) -> dict[str, Any]:
    if not block:
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    data = yaml.safe_load(block) or {}
    return data if isinstance(data, dict) else {}


def _list_svg_files(template_dir: Path) -> list[Path]:
    return sorted(p for p in template_dir.glob("*.svg") if p.is_file())


def _expected_kind(template_dir: Path, frontmatter: dict[str, Any]) -> str:
    kind = frontmatter.get("kind")
    if isinstance(kind, str) and kind in {"brand", "layout", "deck"}:
        return kind
    parts = set(template_dir.resolve().parts)
    if "decks" in parts:
        return "deck"
    if "brands" in parts:
        return "brand"
    return "layout"


def _extract_roster_entries(body: str) -> list[str]:
    section_start = body.find("## V. Page Roster")
    if section_start == -1:
        section_start = body.find("## V. SVG Page Roster")
    if section_start == -1:
        return []
    next_section = body.find("\n## ", section_start + 1)
    section = body[section_start: next_section if next_section != -1 else None]
    entries: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if ".svg" not in stripped:
            continue
        for token in stripped.replace("`", " ").replace("|", " ").split():
            if token.endswith(".svg"):
                entries.append(token)
    return sorted(set(entries))


def _check_design_spec_skeleton(
    spec_text: str,
    frontmatter: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    has_personality = all(heading in spec_text for heading in REQUIRED_PERSONALITY_SPEC_SECTIONS)
    has_legacy = all(heading in spec_text for heading in LEGACY_SPEC_SECTIONS)
    has_upstream_roster = "## V. SVG Page Roster" in spec_text
    if has_personality:
        return
    if has_legacy:
        warnings.append("design_spec.md uses the legacy verbose template skeleton; new templates should migrate to the personality-only skeleton")
        return
    if has_upstream_roster and "## I. Template Overview" in spec_text:
        warnings.append("design_spec.md uses an upstream/compatibility template skeleton; strict SUSTech create-template checks require brief_lock.json")
        return

    missing = [heading for heading in REQUIRED_PERSONALITY_SPEC_SECTIONS if heading not in spec_text]
    if frontmatter:
        warnings.append(f"design_spec missing current/legacy skeleton sections; relying on frontmatter and registrar checks: {missing}")
    else:
        errors.append(f"design_spec missing required sections for either current or legacy skeleton: {missing}")


def _check_design_spec_against_lock(
    spec_text: str,
    frontmatter: dict[str, Any],
    lock: dict[str, Any],
    kind: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    _check_design_spec_skeleton(spec_text, frontmatter, errors, warnings)

    if frontmatter:
        missing = REQUIRED_FRONTMATTER_KEYS - set(frontmatter)
        if missing:
            errors.append(f"design_spec frontmatter missing keys: {sorted(missing)}")
        declared_id = _frontmatter_id(frontmatter, kind)
        if declared_id != lock["template_identity"]["template_id"]:
            errors.append(
                "design_spec frontmatter id mismatch: "
                f"expected {lock['template_identity']['template_id']!r}, got {declared_id!r}"
            )
        if frontmatter.get("category") != lock["template_identity"]["category"]:
            errors.append(
                "design_spec frontmatter category mismatch: "
                f"expected {lock['template_identity']['category']!r}, got {frontmatter.get('category')!r}"
            )
        if frontmatter.get("canvas_format") != lock["canvas"]["format"]:
            errors.append(
                "design_spec frontmatter canvas_format mismatch: "
                f"expected {lock['canvas']['format']!r}, got {frontmatter.get('canvas_format')!r}"
            )
        replication = lock.get("replication", {})
        if replication:
            expected_mode = replication.get("mode")
            if expected_mode and frontmatter.get("replication_mode") != expected_mode:
                errors.append(
                    "design_spec frontmatter replication_mode mismatch: "
                    f"expected {expected_mode!r}, got {frontmatter.get('replication_mode')!r}"
                )
    else:
        warnings.append("design_spec.md has no YAML frontmatter; register_template.py will rely on prose fallback")

    display_name = lock["template_identity"]["display_name"]
    if display_name not in spec_text:
        warnings.append("display_name not found verbatim in design_spec.md")

    tone = lock["style_contract"]["tone_summary"]
    if tone and tone not in spec_text:
        warnings.append("locked tone_summary not found verbatim in design_spec.md")


def _check_design_spec_without_lock(
    spec_text: str,
    frontmatter: dict[str, Any],
    template_dir: Path,
    kind: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    _check_design_spec_skeleton(spec_text, frontmatter, errors, warnings)

    if not frontmatter:
        warnings.append("design_spec.md has no YAML frontmatter; register_template.py will rely on prose fallback")
        return

    declared_kind = frontmatter.get("kind")
    if declared_kind and declared_kind != kind:
        errors.append(f"design_spec frontmatter kind mismatch: expected {kind!r}, got {declared_kind!r}")

    id_key = {"brand": "brand_id", "layout": "layout_id", "deck": "deck_id"}[kind]
    declared_id = _frontmatter_id(frontmatter, kind)
    if declared_id is not None and str(declared_id) != template_dir.name:
        errors.append(
            f"design_spec frontmatter id mismatch: expected {template_dir.name!r}, got {declared_id!r}"
        )

    if not str(frontmatter.get("summary") or "").strip():
        errors.append("design_spec frontmatter missing non-empty summary")

    if kind in {"layout", "deck"} and not str(frontmatter.get("canvas_format") or "").strip():
        errors.append("design_spec frontmatter missing non-empty canvas_format")


def _check_svg_files(
    template_dir: Path,
    lock: dict[str, Any] | None,
    frontmatter: dict[str, Any],
    body: str,
    kind: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    svg_files = _list_svg_files(template_dir)
    svg_names = [p.name for p in svg_files]

    replication = lock.get("replication", {}) if lock else {}
    replication_mode = replication.get("mode") or frontmatter.get("replication_mode") or "standard"

    if kind != "brand" and replication_mode == "standard":
        for svg_name in CORE_TEMPLATE_FILES:
            if svg_name not in svg_names:
                errors.append(f"missing core template file: {svg_name}")

    roster_entries = _extract_roster_entries(body)
    if roster_entries:
        missing_from_disk = sorted(set(roster_entries) - set(svg_names))
        if missing_from_disk:
            errors.append(f"design_spec roster references missing SVG files: {missing_from_disk}")
        orphan_svgs = sorted(set(svg_names) - set(roster_entries))
        if orphan_svgs:
            errors.append(f"template directory contains SVG files missing from design_spec roster: {orphan_svgs}")
    else:
        if "## V. Page Roster" in body:
            warnings.append("could not extract any .svg filenames from design_spec §V Page Roster")
        else:
            warnings.append("design_spec.md has no §V Page Roster; roster/file parity checks skipped for legacy template spec")

    placeholder_overrides = frontmatter.get("placeholders") if isinstance(frontmatter.get("placeholders"), dict) else {}
    for svg_path in svg_files:
        content = svg_path.read_text(encoding="utf-8")
        for token in PLACEHOLDER_REQUIREMENTS.get(svg_path.name, []):
            if svg_path.stem in placeholder_overrides or svg_path.name == "02_toc.svg":
                break
            if token not in content:
                warnings.append(f"{svg_path.name} missing conventional placeholder hint: {token}")
        for line in content.splitlines():
            if "href=" not in line:
                continue
            for quote in ('"', "'"):
                needle = f"href={quote}"
                if needle in line:
                    asset_ref = line.split(needle, 1)[1].split(quote, 1)[0]
                    if asset_ref.startswith("data:") or asset_ref.startswith("#") or "://" in asset_ref:
                        continue
                    suffix = Path(asset_ref).suffix.lower()
                    if suffix and suffix in IMAGE_SUFFIXES and not (template_dir / asset_ref).exists():
                        errors.append(f"{svg_path.name} references missing asset: {asset_ref}")
            if replication_mode == "mirror" and "{{" in line:
                errors.append(f"mirror-mode SVG must not contain placeholders: {svg_path.name}")


def _run_svg_quality_checker(template_dir: Path, expected_format: str, errors: list[str], warnings: list[str]) -> None:
    checker = SVGQualityChecker(template_mode=True)
    checker.check_directory(str(template_dir), expected_format=expected_format)
    if checker.summary["errors"] > 0:
        errors.append("SVG quality checker reported template SVG errors")
    if checker.summary["warnings"] > 0:
        warnings.append("SVG quality checker reported template SVG warnings")


def _run_register_preflight(template_dir: Path, kind: str, errors: list[str], warnings: list[str]) -> None:
    script_path = Path(__file__).with_name("register_template.py")
    kind_dir = {"brand": "brands", "layout": "layouts", "deck": "decks"}[kind]
    kind_root = script_path.parent.parent.resolve() / "templates" / kind_dir
    try:
        template_dir.resolve().relative_to(kind_root)
    except ValueError:
        warnings.append(f"register preflight skipped: template_dir is outside templates/{kind_dir}/")
        return
    completed = subprocess.run(
        [sys.executable, str(script_path), template_dir.name, "--kind", kind, "--dry-run"],
        cwd=script_path.parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        msg = completed.stderr.strip() or completed.stdout.strip() or "register_template.py --dry-run failed"
        errors.append(f"register preflight failed: {msg}")
    elif completed.stderr.strip():
        warnings.append(f"register preflight emitted stderr: {completed.stderr.strip()}")


def check_template_dir(template_dir: Path, expected_format: str, require_brief_lock: bool = False) -> dict[str, Any]:
    template_dir = Path(template_dir)
    errors: list[str] = []
    warnings: list[str] = []

    lock_path = template_dir / "brief_lock.json"
    lock: dict[str, Any] | None = None
    if lock_path.exists():
        try:
            lock = load_brief_lock(template_dir)
        except Exception as exc:
            errors.append(f"Invalid brief_lock.json: {exc}")
            return {"passed": False, "errors": errors, "warnings": warnings}
    elif require_brief_lock:
        errors.append("Missing brief_lock.json")
        return {"passed": False, "errors": errors, "warnings": warnings}
    else:
        warnings.append("Missing brief_lock.json; running frontmatter/prose compatibility checks")

    design_spec = template_dir / "design_spec.md"
    if not design_spec.exists():
        errors.append("Missing design_spec.md")
        return {"passed": False, "errors": errors, "warnings": warnings}

    frontmatter_block, body = _read_spec(design_spec)
    frontmatter = _parse_frontmatter_block(frontmatter_block)
    spec_text = design_spec.read_text(encoding="utf-8")

    kind = _expected_kind(template_dir, frontmatter)
    if lock is not None:
        _check_design_spec_against_lock(spec_text, frontmatter, lock, kind, errors, warnings)
    else:
        _check_design_spec_without_lock(spec_text, frontmatter, template_dir, kind, errors, warnings)
    _check_svg_files(template_dir, lock, frontmatter, body, kind, errors, warnings)
    _run_svg_quality_checker(template_dir, expected_format=expected_format, errors=errors, warnings=warnings)
    _run_register_preflight(template_dir, kind, errors=errors, warnings=warnings)

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "lock_revision": lock["revision"] if lock else "N/A",
        "template_dir": str(template_dir),
        "kind": kind,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a create-template output directory")
    parser.add_argument("template_dir", type=Path, help="Template directory under templates/layouts/ or templates/decks/")
    parser.add_argument("--format", dest="expected_format", required=True, help="Expected canvas format, e.g. ppt169")
    parser.add_argument(
        "--require-brief-lock",
        action="store_true",
        help="Require brief_lock.json. Use this for newly generated /create-template outputs.",
    )
    args = parser.parse_args()

    result = check_template_dir(
        args.template_dir,
        expected_format=args.expected_format,
        require_brief_lock=args.require_brief_lock,
    )

    print(f"[CHECK] template: {args.template_dir}")
    print(f"[CHECK] brief_lock revision: {result.get('lock_revision', 'N/A')}")
    print(f"[CHECK] kind: {result.get('kind', 'N/A')}")
    for error in result["errors"]:
        print(f"[ERROR] {error}")
    for warning in result["warnings"]:
        print(f"[WARN] {warning}")

    if result["passed"]:
        print("[OK] Template self-check passed")
        sys.exit(0)

    print("[FAIL] Template self-check failed")
    sys.exit(1)


if __name__ == "__main__":
    main()
