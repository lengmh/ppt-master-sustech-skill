import unittest
from pathlib import Path

from template_quality_checker import (
    _check_design_spec_against_lock,
    _check_design_spec_skeleton,
    _check_design_spec_without_lock,
)


class TestDesignSpecSkeletonCheck(unittest.TestCase):
    def test_personality_skeleton_passes_without_messages(self):
        errors = []
        warnings = []
        spec_text = "\n".join([
            "## I. Template Overview",
            "## II. Color Scheme",
            "## IV. Signature Design Elements",
            "## V. Page Roster",
        ])

        _check_design_spec_skeleton(spec_text, {}, errors, warnings)

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_skeleton_with_frontmatter_warns(self):
        errors = []
        warnings = []

        _check_design_spec_skeleton("plain spec", {"summary": "x"}, errors, warnings)

        self.assertEqual(errors, [])
        self.assertTrue(any("design_spec missing current/legacy skeleton sections" in item for item in warnings))

    def test_missing_skeleton_without_frontmatter_errors(self):
        errors = []
        warnings = []

        _check_design_spec_skeleton("plain spec", {}, errors, warnings)

        self.assertTrue(any("design_spec missing required sections" in item for item in errors))
        self.assertEqual(warnings, [])

    def test_against_lock_preserves_legacy_skeleton_warning(self):
        errors = []
        warnings = []
        spec_text = "\n".join([
            "Demo Template",
            "## I. Template Overview",
            "## II. Canvas Specification",
            "## III. Color Scheme",
            "## IV. Typography System",
            "## V. Page Structure",
            "## VI. Page Types",
        ])
        frontmatter = {
            "kind": "layout",
            "layout_id": "demo_layout",
            "category": "education",
            "summary": "Demo",
            "keywords": ["demo"],
            "primary_color": "#003F43",
            "canvas_format": "ppt169",
            "replication_mode": "standard",
            "native_structure_mode": "structured",
        }
        lock = {
            "template_identity": {
                "template_id": "demo_layout",
                "category": "education",
                "display_name": "Demo Template",
            },
            "canvas": {"format": "ppt169"},
            "style_contract": {"tone_summary": ""},
            "replication": {"mode": "standard"},
        }

        _check_design_spec_against_lock(spec_text, frontmatter, lock, "layout", errors, warnings)

        self.assertEqual(errors, [])
        self.assertTrue(any("legacy verbose template skeleton" in item for item in warnings))

    def test_without_lock_preserves_upstream_skeleton_warning(self):
        errors = []
        warnings = []
        spec_text = "\n".join([
            "## I. Template Overview",
            "## V. SVG Page Roster",
            "- 01_cover.svg",
        ])
        frontmatter = {
            "kind": "layout",
            "layout_id": "demo_layout",
            "summary": "Demo",
            "canvas_format": "ppt169",
        }

        _check_design_spec_without_lock(spec_text, frontmatter, Path("demo_layout"), "layout", errors, warnings)

        self.assertEqual(errors, [])
        self.assertTrue(any("upstream/compatibility template skeleton" in item for item in warnings))


if __name__ == "__main__":
    unittest.main()


def _qualified_brand_workspace(tmp_path):
    import shutil
    source = Path(__file__).resolve().parents[2] / "templates/brands/anthropic"
    workspace = tmp_path / "project"
    shutil.copytree(source, workspace)
    spec = workspace / "templates/design_spec.md"
    spec.rename(spec.with_name("design_spec.brand.anthropic.md"))
    return workspace


def test_qualified_brand_workspace_uses_upstream_validation(tmp_path):
    from template_quality_checker import check_template_dir
    workspace = _qualified_brand_workspace(tmp_path)
    result = check_template_dir(workspace)
    assert result["passed"], result["errors"]
    assert not (workspace / "brief_lock.json").exists()


def test_qualified_brand_rejects_identity_mismatch(tmp_path):
    from template_quality_checker import check_template_dir
    workspace = _qualified_brand_workspace(tmp_path)
    spec = workspace / "templates/design_spec.brand.anthropic.md"
    spec.rename(spec.with_name("design_spec.brand.wrong.md"))
    result = check_template_dir(workspace)
    assert not result["passed"]
    assert any("filename id" in error for error in result["errors"])


def test_qualified_brand_explicit_legacy_audit_still_requires_lock(tmp_path):
    from template_quality_checker import check_template_dir
    workspace = _qualified_brand_workspace(tmp_path)
    result = check_template_dir(workspace, require_brief_lock=True)
    assert not result["passed"]
    assert "Missing brief_lock.json" in result["errors"]
