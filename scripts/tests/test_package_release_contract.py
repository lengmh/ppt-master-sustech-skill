from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from package_release import (
    FORBIDDEN_RELEASE_PATHS,
    REQUIRED_RELEASE_PATHS,
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


def test_v41_required_and_retired_path_inventory() -> None:
    required = set(REQUIRED_RELEASE_PATHS)
    forbidden = set(FORBIDDEN_RELEASE_PATHS)

    assert {
        "scripts/project_specs.py",
        "scripts/page_context.py",
        "scripts/chart_recall.py",
        "scripts/svg_authoring_view.py",
        "scripts/template_preview_pptx.py",
        "scripts/template_brief_lock.py",
        ".env.example",
        "requirements.txt",
        "references/native-data-interface.md",
        "references/pptx-structure-interface.md",
        "workflows/generate-pptx.md",
        "workflows/stages/live-preview.md",
        "workflows/stages/refine-spec.md",
        "workflows/stages/resume-execute.md",
        "workflows/stages/topic-research.md",
        "workflows/stages/apply-template-workspace.md",
        "workflows/stages/visual-review.md",
        "workflows/profiles/beautify-pptx.md",
        "workflows/create-template/create-brand.md",
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
        "scripts/svg_to_pptx/text_contract.py",
        "scripts/svg_to_pptx/pptx_package/text_validation.py",
        "workflows/distill-layouts.md",
        "workflows/live-preview.md",
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
