from pathlib import Path
import json
import os
import subprocess
import sys
import unittest

from update_spec import parse_lock
from svg_quality_checker import LayoutQualityHeuristics, SVGQualityChecker


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "layout_quality"
REPO_ROOT = Path(__file__).resolve().parents[2]
TEMP_DIR = Path("/home/sustech/TempFiles")


class TestLayoutQualityBudget(unittest.TestCase):
    def setUp(self):
        self.checker = SVGQualityChecker()
        self.lock_data = parse_lock(FIXTURE_DIR / "spec_lock_layout_quality.md")

    def test_missing_layout_quality_uses_defaults_without_warning(self):
        result = {"warnings": []}

        budget = self.checker._get_layout_quality_budget({}, "P99", result)

        self.assertEqual(budget.text_budget, "medium")
        self.assertEqual(budget.risk, "none")
        self.assertEqual(budget.review_hint, "manual")
        self.assertEqual(result["warnings"], [])

    def test_page_specific_layout_quality_budget_is_parsed(self):
        result = {"warnings": []}

        budget = self.checker._get_layout_quality_budget(self.lock_data, "P02", result)

        self.assertEqual(budget.text_budget, "high")
        self.assertEqual(budget.risk, "cards-overflow")
        self.assertEqual(budget.review_hint, "wrap-risk")
        self.assertEqual(result["warnings"], [])

    def test_unknown_layout_quality_values_warn_and_fall_back(self):
        result = {"warnings": []}

        budget = self.checker._get_layout_quality_budget(self.lock_data, "P03", result)

        self.assertEqual(budget.text_budget, "medium")
        self.assertEqual(budget.risk, "none")
        self.assertEqual(budget.review_hint, "manual")
        self.assertTrue(any("layout_quality" in warning for warning in result["warnings"]))

    def test_layout_quality_heuristics_centralizes_numeric_thresholds(self):
        heuristics = LayoutQualityHeuristics()

        self.assertGreater(heuristics.cjk_char_width_factor, heuristics.latin_char_width_factor)
        self.assertGreater(heuristics.line_height_factor, 1)
        self.assertGreaterEqual(heuristics.container_overflow_tolerance_px, 0)


class TestStaticTextFitChecks(unittest.TestCase):
    def setUp(self):
        self.checker = SVGQualityChecker()

    def _issue_ids_for(self, fixture_name):
        result = self.checker.check_file(str(FIXTURE_DIR / fixture_name))
        return {issue["id"] for issue in result.get("layout_warnings", [])}

    def test_text_wider_than_inferred_container_emits_overflow(self):
        issue_ids = self._issue_ids_for("text_overflow_card.svg")

        self.assertIn("overflow", issue_ids)

    def test_small_body_font_emits_canonical_font_too_small(self):
        issue_ids = self._issue_ids_for("font_too_small.svg")

        self.assertIn("font_too_small", issue_ids)
        self.assertNotIn("text_too_small", issue_ids)

    def test_large_body_text_on_dense_page_emits_canonical_font_too_large(self):
        issue_ids = self._issue_ids_for("font_too_large_dense.svg")

        self.assertIn("font_too_large", issue_ids)
        self.assertNotIn("text_too_large", issue_ids)

    def test_large_hero_text_on_breathing_page_is_not_body_oversize(self):
        issue_ids = self._issue_ids_for("hero_title_breathing_ok.svg")

        self.assertNotIn("font_too_large", issue_ids)

    def test_declared_low_budget_with_many_characters_emits_budget_mismatch(self):
        issue_ids = self._issue_ids_for("low_budget_many_chars.svg")

        self.assertIn("budget_mismatch", issue_ids)

    def test_non_1280_canvas_uses_actual_geometry(self):
        issue_ids = self._issue_ids_for("non_1280_overflow.svg")

        self.assertIn("overflow", issue_ids)

    def test_near_threshold_readable_text_does_not_emit_overflow(self):
        issue_ids = self._issue_ids_for("near_threshold_ok.svg")

        self.assertNotIn("overflow", issue_ids)

    def test_translated_group_overflow_remains_probe_recommended(self):
        result = self.checker.check_file(str(FIXTURE_DIR / "transformed_group_overflow.svg"))
        issues = result.get("layout_warnings", [])

        self.assertTrue(
            any(issue["id"] == "overflow" and issue["probe_recommended"] for issue in issues)
        )


class TestStaticOverlapChecks(unittest.TestCase):
    def setUp(self):
        self.checker = SVGQualityChecker()

    def _issue_ids_for(self, fixture_name):
        result = self.checker.check_file(str(FIXTURE_DIR / fixture_name))
        return {issue["id"] for issue in result.get("layout_warnings", [])}

    def test_overlapping_content_cards_emit_card_collision(self):
        issue_ids = self._issue_ids_for("card_collision.svg")

        self.assertIn("card_collision", issue_ids)

    def test_overlapping_cards_without_text_still_emit_card_collision(self):
        issue_ids = self._issue_ids_for("card_collision_no_text.svg")

        self.assertIn("card_collision", issue_ids)

    def test_normal_card_grid_does_not_emit_card_collision(self):
        issue_ids = self._issue_ids_for("normal_card_grid_ok.svg")

        self.assertNotIn("card_collision", issue_ids)

    def test_manual_image_overlay_does_not_emit_card_collision(self):
        issue_ids = self._issue_ids_for("image_overlay_manual_ok.svg")

        self.assertNotIn("card_collision", issue_ids)


class TestLayoutQualityCliReport(unittest.TestCase):
    def _run_checker(self, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "scripts")
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "svg_quality_checker.py"), *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_layout_json_writes_static_issue_report(self):
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        output = TEMP_DIR / "layout-quality-static-test.json"
        output.unlink(missing_ok=True)

        completed = self._run_checker(
            str(FIXTURE_DIR),
            "--layout-json",
            str(output),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["source"], "static")
        issue_ids = {
            issue["id"]
            for file_report in payload["files"]
            for issue in file_report["issues"]
        }
        self.assertIn("overflow", issue_ids)
        self.assertIn("card_collision", issue_ids)

    def test_existing_export_output_cli_still_writes_text_report(self):
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        output = TEMP_DIR / "svg-quality-export-test.txt"
        output.unlink(missing_ok=True)

        completed = self._run_checker(
            str(FIXTURE_DIR),
            "--export",
            "--output",
            str(output),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertIn("PPT Master SVG Quality Check Report", output.read_text(encoding="utf-8"))

    def test_cli_suggests_optional_probe_for_ambiguous_layout_warning(self):
        completed = self._run_checker(str(FIXTURE_DIR / "text_overflow_card.svg"))

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertIn("svg_layout_probe.py", completed.stdout)


if __name__ == "__main__":
    unittest.main()
