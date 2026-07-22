from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import template_brief_lock
from register_template import _extract_entry, _template_content_dir
from template_brief_lock import brief_lock_path, load_brief_lock
from template_preview import (
    _resolve_workspace as resolve_preview_workspace,
    export_template_preview,
)
from template_quality_checker import (
    _resolve_workspace as resolve_checker_workspace,
    check_template_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SUSTECH_WORKSPACE = REPO_ROOT / "templates" / "decks" / "sustech_academic_official"
ANTHROPIC_WORKSPACE = REPO_ROOT / "templates" / "brands" / "anthropic"
PRESENTATION_CORE_WORKSPACE = (
    REPO_ROOT / "templates" / "layouts" / "presentation_core"
)
CHINA_TELECOM_DECK_WORKSPACE = REPO_ROOT / "templates" / "decks" / "中国电信"

LOCK_FREE_WORKSPACES = [
    pytest.param("brand", ANTHROPIC_WORKSPACE, id="brand"),
    pytest.param("layout", PRESENTATION_CORE_WORKSPACE, id="layout"),
    pytest.param("deck", CHINA_TELECOM_DECK_WORKSPACE, id="deck"),
]

LOCK_FREE_PREVIEW_WORKSPACES = [
    pytest.param(PRESENTATION_CORE_WORKSPACE, id="layout"),
    pytest.param(CHINA_TELECOM_DECK_WORKSPACE, id="deck"),
]

LOCK_FREE_REGISTRAR_CASES = [
    pytest.param(
        "brand",
        "anthropic",
        {
            "summary": (
                "Anthropic / Claude brand family — AI research, product talks, "
                "developer conferences, technical training, and launches"
            ),
            "primary_color": "#D97757",
        },
        id="brand",
    ),
    pytest.param(
        "layout",
        "presentation_core",
        {
            "summary": (
                "A structure-only 16:9 system with 20 authored PowerPoint Layouts "
                "for general, editorial, image, process, and data presentations."
            ),
            "canvas_format": "ppt169",
            "page_count": 20,
            "page_types": [
                "title_slide",
                "title_content",
                "section_header",
                "two_content",
                "comparison",
                "title_only",
                "blank",
                "content_caption",
                "picture_caption",
                "hero_statement",
                "editorial_split",
                "three_card",
                "kpi_dashboard",
                "process_timeline",
                "data_story",
                "title_picture",
                "two_picture_caption",
                "screenshot_focus",
                "chart_insight",
                "table_summary",
            ],
        },
        id="layout",
    ),
    pytest.param(
        "deck",
        "中国电信",
        {
            "summary": (
                "中国电信政企数字化方案、转型规划与内部评审，用于说明方案并对齐决策和"
                "下一步；采用克制的红灰品牌视觉。"
            ),
            "canvas_format": "ppt169",
            "page_count": 5,
            "primary_color": "#C00000",
        },
        id="deck",
    ),
]


def test_canonical_workspace_resolvers_and_root_brief_lock() -> None:
    content_root = SUSTECH_WORKSPACE / "templates"

    assert resolve_checker_workspace(SUSTECH_WORKSPACE) == (
        SUSTECH_WORKSPACE,
        content_root,
    )
    assert resolve_checker_workspace(content_root) == (
        SUSTECH_WORKSPACE,
        content_root,
    )
    assert resolve_preview_workspace(SUSTECH_WORKSPACE) == (
        SUSTECH_WORKSPACE,
        content_root,
    )
    assert _template_content_dir(SUSTECH_WORKSPACE) == content_root
    assert brief_lock_path(content_root) == SUSTECH_WORKSPACE / "brief_lock.json"
    assert load_brief_lock(content_root)["revision"] == 1


def test_legacy_flat_workspace_and_nested_lock_fallback(tmp_path: Path) -> None:
    flat = tmp_path / "legacy_flat"
    flat.mkdir()
    (flat / "design_spec.md").write_text("# Legacy\n", encoding="utf-8")

    assert resolve_checker_workspace(flat) == (flat, flat)
    assert resolve_preview_workspace(flat) == (flat, flat)
    assert _template_content_dir(flat) == flat

    nested = tmp_path / "legacy_nested" / "templates"
    nested.mkdir(parents=True)
    (nested / "design_spec.md").write_text("# Legacy\n", encoding="utf-8")
    shutil.copy2(SUSTECH_WORKSPACE / "brief_lock.json", nested / "brief_lock.json")

    assert load_brief_lock(nested)["revision"] == 1


def test_sustech_nested_image_references_resolve() -> None:
    references: list[str] = []
    for svg_path in sorted((SUSTECH_WORKSPACE / "templates").glob("*.svg")):
        text = svg_path.read_text(encoding="utf-8")
        for asset_ref in re.findall(
            r'(?:xlink:href|href)=["\']([^"\']+)["\']',
            text,
        ):
            if asset_ref.startswith(("#", "data:")) or "://" in asset_ref:
                continue
            if Path(asset_ref).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            references.append(asset_ref)
            assert asset_ref.startswith("../images/")
            assert (svg_path.parent / asset_ref).is_file(), (svg_path.name, asset_ref)

    assert references


def test_sustech_checker_registrar_and_index_contract() -> None:
    result = check_template_dir(SUSTECH_WORKSPACE, require_brief_lock=True)
    assert result["passed"], result["errors"]
    assert result["kind"] == "deck"
    assert result["lock_revision"] == 1

    extracted = _extract_entry("deck", "sustech_academic_official", SUSTECH_WORKSPACE)
    assert extracted["entry"] == {
        "summary": "Official academic template for course reports, research briefings, thesis defenses, and seminars.",
        "canvas_format": "ppt169",
        "page_count": 8,
        "primary_color": "#003F43",
    }
    index = json.loads(
        (REPO_ROOT / "templates" / "decks" / "decks_index.json").read_text(
            encoding="utf-8"
        )
    )
    assert index["sustech_academic_official"] == extracted["entry"]
    assert set(index) == {"sustech_academic_official", "中国电信", "中汽研"}


def test_legacy_lock_reader_has_no_writer_export() -> None:
    assert set(template_brief_lock.__all__) == {
        "brief_lock_path",
        "load_brief_lock",
        "validate_brief_lock",
    }
    assert not hasattr(template_brief_lock, "write_brief_lock")


def test_sustech_deck_passes_explicit_strict_lock_cli() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "template_quality_checker.py"),
            str(SUSTECH_WORKSPACE),
            "--require-brief-lock",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "[CHECK] brief_lock revision: 1" in completed.stdout
    assert "[OK] Template self-check passed" in completed.stdout


def test_brand_checker_does_not_require_canvas_format() -> None:
    result = check_template_dir(ANTHROPIC_WORKSPACE)

    assert result["passed"], result["errors"]
    assert result["kind"] == "brand"
    assert not any("Missing canvas format" in error for error in result["errors"])


@pytest.mark.parametrize(("expected_kind", "workspace"), LOCK_FREE_WORKSPACES)
def test_lock_free_workspaces_pass_default_validation_without_writing_a_lock(
    expected_kind: str,
    workspace: Path,
) -> None:
    lock_path = workspace / "brief_lock.json"
    assert not lock_path.exists()

    result = check_template_dir(workspace)

    assert result["passed"], result["errors"]
    assert result["kind"] == expected_kind
    assert result["lock_revision"] == "N/A"
    assert not lock_path.exists()


@pytest.mark.parametrize("workspace", LOCK_FREE_PREVIEW_WORKSPACES)
def test_lock_free_workspace_preview_does_not_depend_on_a_brief_lock(
    workspace: Path,
    tmp_path: Path,
) -> None:
    lock_path = workspace / "brief_lock.json"
    assert not lock_path.exists()

    preview_workspace = export_template_preview(
        workspace,
        output_root=tmp_path,
    )

    expected_svgs = sorted(
        path.name for path in (workspace / "templates").glob("*.svg")
    )
    preview_svgs = sorted(
        path.name for path in (preview_workspace / "svg_final").glob("*.svg")
    )
    assert preview_svgs == expected_svgs
    assert not (preview_workspace / "brief_lock.json").exists()
    assert not lock_path.exists()


@pytest.mark.parametrize(
    ("kind", "template_id", "expected_entry"),
    LOCK_FREE_REGISTRAR_CASES,
)
def test_lock_free_registrar_dry_run_uses_spec_and_template_assets(
    kind: str,
    template_id: str,
    expected_entry: dict[str, object],
) -> None:
    workspace = REPO_ROOT / "templates" / f"{kind}s" / template_id
    lock_path = workspace / "brief_lock.json"
    assert not lock_path.exists()

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "register_template.py"),
            template_id,
            "--kind",
            kind,
            "--dry-run",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    json_start = completed.stdout.find("{")
    assert json_start >= 0
    index, json_length = json.JSONDecoder().raw_decode(completed.stdout[json_start:])
    assert index[template_id] == expected_entry
    assert "[OK] Dry-run preview" in completed.stdout[json_start + json_length:]
    assert not lock_path.exists()


def test_active_create_template_route_is_design_spec_only() -> None:
    workflow = (REPO_ROOT / "workflows" / "create-template.md").read_text(
        encoding="utf-8"
    )
    prompt_manifest = json.loads(
        (REPO_ROOT / "scripts" / "prompt_audit_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    legacy_reference = (
        REPO_ROOT / "references" / "template-brief-confirmation.md"
    ).read_text(encoding="utf-8")

    assert "[TEMPLATE_BRIEF_CONFIRMED]" in workflow
    for legacy_lock_instruction in (
        "brief_lock.json",
        "template_brief_lock",
        "--require-brief-lock",
        "template-brief-confirmation.md",
    ):
        assert legacy_lock_instruction not in workflow

    for route_name in (
        "route.create-template.brand",
        "route.create-template.layout",
        "route.create-template.deck",
    ):
        assert (
            "references/template-brief-confirmation.md"
            not in prompt_manifest["load_sets"][route_name]["files"]
        )

    assert "legacy read compatibility" in legacy_reference
    assert "[TEMPLATE_BRIEF_CONFIRMED]" not in legacy_reference
    assert "write_brief_lock" not in legacy_reference


def test_layout_quality_schema_accepts_only_bounded_contract() -> None:
    schema = json.loads(
        (REPO_ROOT / "templates" / "schemas" / "spec_lock.schema.json").read_text(
            encoding="utf-8"
        )
    )
    definition = next(
        section
        for section in schema["x-markdown"]["sections"]
        if section["id"] == "layout_quality"
    )

    assert definition["required"] is False
    assert re.fullmatch(definition["entry_key_pattern"], "P02")
    assert not re.fullmatch(definition["entry_key_pattern"], "page-2")
    assert re.fullmatch(
        definition["value_pattern"],
        "text_budget=high; risk=cards-overflow; review_hint=wrap-risk",
    )
    assert not re.fullmatch(
        definition["value_pattern"],
        "text_budget=unbounded; risk=unknown; review_hint=auto",
    )
