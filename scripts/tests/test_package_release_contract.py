from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

import package_release

from package_release import (
    FORBIDDEN_RELEASE_PATHS,
    REQUIRED_RELEASE_PATHS,
    ignore_copytree_entries,
    stage_local_release_tree,
    verify_release_zip,
)


PACKAGE_ROOT = "ppt-master"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _zip_entry(path: str) -> str:
    entry = f"{PACKAGE_ROOT}/{path}"
    return f"{entry}__test__" if path.endswith("/") else entry


def _write_zip(path: Path, entries: list[str]) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for entry in entries:
            archive.writestr(entry, b"")


def test_v61_required_and_retired_path_inventory() -> None:
    required = set(REQUIRED_RELEASE_PATHS)
    forbidden = set(FORBIDDEN_RELEASE_PATHS)

    assert {
        "scripts/project_specs.py",
        "scripts/page_context.py",
        "scripts/chart_recall.py",
        "scripts/attribution_guard.py",
        "scripts/svg_authoring_view.py",
        "scripts/template_preview_pptx.py",
        "scripts/template_brief_lock.py",
        ".env.example",
        "requirements.txt",
        "SPONSORS.md",
        "SPONSORS_CN.md",
        "references/native-data-interface.md",
        "references/pptx-structure-interface.md",
        "references/video-design.md",
        "templates/layouts/layouts_index.json",
        "templates/styles/styles_index.json",
        "workflows/routing.md",
        "workflows/generate-pptx.md",
        "workflows/edit-native-pptx.md",
        "workflows/stages/live-preview.md",
        "workflows/stages/refine-spec.md",
        "workflows/stages/resume-execute.md",
        "workflows/stages/topic-research.md",
        "workflows/stages/apply-template-workspace.md",
        "workflows/stages/visual-review.md",
        "workflows/profiles/beautify-pptx.md",
        "workflows/profiles/image-to-pptx.md",
        "workflows/profiles/quick-generate.md",
        "workflows/create-template.md",
        "workflows/create-template/create-brand.md",
        "workflows/create-template/create-style.md",
        "workflows/create-template/create-layout.md",
        "workflows/create-template/create-deck.md",
        "templates/decks/sustech_academic_official/templates/design_spec.md",
        "scripts/pptx_shapes/data/NOTICE.md",
        "scripts/pptx_shapes/data/LICENSE-OPEN-XML-SDK-MIT.txt",
        "scripts/pptx_shapes/data/LICENSE-APACHE-2.0.txt",
    } <= required
    assert {
        "AGENTS.md",
        "CONTEXT.md",
        "scripts/ppt_text_normalize/CONTEXT.md",
        "scripts/ppt_text_normalize/build_review_workspace.py",
        "scripts/ppt_text_normalize/compile_review_decisions.py",
        "scripts/ppt_text_normalize/contracts/review_decisions.schema.json",
        "scripts/ppt_text_normalize/contracts/review_model.schema.json",
        "scripts/ppt_text_normalize/contracts/rules_reviewed.schema.json",
        "scripts/ppt_text_normalize/core/review_decisions.py",
        "scripts/ppt_text_normalize/core/review_model.py",
        "scripts/ppt_text_normalize/core/review_workspace.py",
        "scripts/ppt_text_normalize/tests/test_visual_review_field_override.py",
        "scripts/svg_editor/static/normalization_review.js",
        "scripts/svg_to_pptx/text_contract.py",
        "scripts/svg_to_pptx/pptx_package/text_validation.py",
        "scripts/template_fill_pptx.py",
        "scripts/template_fill_pptx/",
        "scripts/native_enhance_pptx.py",
        "scripts/native_enhance_pptx_core.py",
        "scripts/native_narration_pptx.py",
        "workflows/distill-layouts.md",
        "workflows/live-preview.md",
        "workflows/template-fill-pptx.md",
        "workflows/native-enhance-pptx.md",
    } <= forbidden
    assert "workflows/create-brand.md" not in required
    assert "workflows/visual-review.md" not in required


def test_release_metadata_describes_legacy_brief_lock_compatibility() -> None:
    metadata = json.loads(
        (REPO_ROOT / "RELEASE_META.json").read_text(encoding="utf-8")
    )
    notes = metadata["notes"]

    assert "legacy brief-lock read and explicit strict-audit compatibility" in notes
    assert "SUSTech template audit" not in notes


def test_release_metadata_tracks_v673_fixed_cutoff() -> None:
    metadata = json.loads(
        (REPO_ROOT / "RELEASE_META.json").read_text(encoding="utf-8")
    )
    upstream = metadata["upstream"]

    assert metadata["schema_version"] == 1
    assert metadata["release_version"] == "r6.7.3-v0.4.0"
    assert (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip() == metadata["release_version"]
    assert metadata["local"]["version"] == "0.4.0"
    assert upstream == {
        "repo": "hugohe3/ppt-master",
        "version": "6.7.3",
        "tag": "v6.7.3",
        "commit": "622bf0148bca4f697b0184322c7e2aa2a04520a2",
        "baseline_kind": "tag",
        "tracked_ref": "refs/heads/main",
        "tracked_commit": "523e5bd972f94c3cac8742fec0d54d43824a17bb",
        "tracked_range": "v6.7.3..523e5bd972f94c3cac8742fec0d54d43824a17bb",
        "absorbed_from_commit": "c40bca58e168fcef2facdc7612cc352d1233679b",
        "absorbed_range": (
            "c40bca58e168fcef2facdc7612cc352d1233679b"
            "..523e5bd972f94c3cac8742fec0d54d43824a17bb"
        ),
    }


def test_package_filter_excludes_unreleased_normalizer_review_flow() -> None:
    normalizer_dir = REPO_ROOT / "scripts" / "ppt_text_normalize"
    editor_static_dir = REPO_ROOT / "scripts" / "svg_editor" / "static"

    assert {
        "build_review_workspace.py",
        "compile_review_decisions.py",
    } <= ignore_copytree_entries(
        str(normalizer_dir),
        ["apply.py", "build_review_workspace.py", "compile_review_decisions.py"],
    )
    assert "normalization_review.js" in ignore_copytree_entries(
        str(editor_static_dir),
        ["app.js", "normalization_review.js"],
    )


def test_staged_release_tree_excludes_unreleased_normalizer_review_flow(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / PACKAGE_ROOT
    package_root.mkdir()
    stage_local_release_tree(package_root)

    for path in (
        "scripts/ppt_text_normalize/build_review_workspace.py",
        "scripts/ppt_text_normalize/compile_review_decisions.py",
        "scripts/ppt_text_normalize/contracts/review_decisions.schema.json",
        "scripts/ppt_text_normalize/contracts/review_model.schema.json",
        "scripts/ppt_text_normalize/contracts/rules_reviewed.schema.json",
        "scripts/ppt_text_normalize/core/review_decisions.py",
        "scripts/ppt_text_normalize/core/review_model.py",
        "scripts/ppt_text_normalize/core/review_workspace.py",
        "scripts/ppt_text_normalize/tests/test_visual_review_field_override.py",
        "scripts/svg_editor/static/normalization_review.js",
    ):
        assert not (package_root / path).exists(), path
    assert "CONTEXT.md" not in (
        package_root / "scripts" / "ppt_text_normalize" / "README.md"
    ).read_text(encoding="utf-8")


def test_verify_release_zip_accepts_required_inventory(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    _write_zip(archive, [_zip_entry(path) for path in REQUIRED_RELEASE_PATHS])

    verify_release_zip(archive, PACKAGE_ROOT)


def test_package_release_rejects_a_nonstandard_package_root(tmp_path: Path) -> None:
    output_path = tmp_path / "unexpected-root.zip"

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "package_release.py"),
            "--package-dirname",
            "unexpected-root",
            "--output",
            str(output_path),
            "--temp-root",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "Package root directory must be 'ppt-master'" in completed.stderr
    assert not output_path.exists()


def test_verify_release_zip_rejects_extra_top_level_entries(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    _write_zip(
        archive,
        [_zip_entry(path) for path in REQUIRED_RELEASE_PATHS],
    )

    with ZipFile(archive, "a", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("unexpected-root/extra.txt", b"")

    with pytest.raises(RuntimeError, match="Unexpected top-level entries"):
        verify_release_zip(archive, PACKAGE_ROOT)


@pytest.mark.parametrize("forbidden_path", FORBIDDEN_RELEASE_PATHS)
def test_verify_release_zip_rejects_forbidden_inventory(
    tmp_path: Path,
    forbidden_path: str,
) -> None:
    archive = tmp_path / "release.zip"
    entries = [_zip_entry(path) for path in REQUIRED_RELEASE_PATHS]
    entries.append(_zip_entry(forbidden_path))
    _write_zip(archive, entries)

    with pytest.raises(RuntimeError, match="Forbidden entries present"):
        verify_release_zip(archive, PACKAGE_ROOT)


def test_temp_root_defaults_to_system_temp(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("PPT_MASTER_TEMP_ROOT", raising=False)
    monkeypatch.setattr(package_release.tempfile, "gettempdir", lambda: str(tmp_path))

    assert package_release.detect_temp_root() == tmp_path / "ppt-master"


def test_temp_root_honors_environment_override(monkeypatch, tmp_path: Path) -> None:
    override = tmp_path / "custom-workspace"
    monkeypatch.setenv("PPT_MASTER_TEMP_ROOT", str(override))

    assert package_release.detect_temp_root() == override
