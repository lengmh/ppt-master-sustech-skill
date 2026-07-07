from pathlib import Path
import unittest

from svg_layout_probe import (
    build_report,
    chromium_missing_message,
    discover_targets,
    parse_args,
    playwright_missing_message,
    _detect_browser_issues,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "layout_quality"


class TestSvgLayoutProbeReport(unittest.TestCase):
    def test_build_report_uses_browser_schema(self):
        payload = build_report([
            {
                "file": "text_overflow_card.svg",
                "path": str(FIXTURE_DIR / "text_overflow_card.svg"),
                "issues": [
                    {
                        "id": "overflow",
                        "severity": "warning",
                        "source": "browser",
                        "element_ref": "text element 1",
                    }
                ],
            }
        ])

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["source"], "browser")
        self.assertEqual(payload["files"][0]["issues"][0]["id"], "overflow")

    def test_fixture_mode_discovers_svg_file(self):
        args = parse_args([
            "--fixture-mode",
            str(FIXTURE_DIR / "text_overflow_card.svg"),
            "--json",
        ])

        targets = discover_targets(args)

        self.assertEqual([target.name for target in targets], ["text_overflow_card.svg"])

    def test_fixture_mode_discovers_svg_directory(self):
        args = parse_args(["--fixture-mode", str(FIXTURE_DIR)])

        targets = discover_targets(args)

        self.assertIn("text_overflow_card.svg", {target.name for target in targets})

    def test_missing_dependency_messages_are_distinct_and_actionable(self):
        self.assertIn("Python package 'playwright'", playwright_missing_message())
        self.assertIn("uv run --with playwright", playwright_missing_message())
        self.assertIn("Chromium", chromium_missing_message())
        self.assertIn("uv run --with playwright python -m playwright install chromium", chromium_missing_message())

    def test_browser_issue_detection_ignores_full_canvas_background_rect(self):
        issues = _detect_browser_issues({
            "canvas": {"x": 0, "y": 0, "width": 1280, "height": 720},
            "texts": [
                {
                    "element_ref": "renamed-copy",
                    "text": "This sentence is intentionally far too long for the small panel.",
                    "font_size": 22,
                    "box": {"x": 120, "y": 136, "width": 589.4, "height": 25},
                }
            ],
            "shapes": [
                {
                    "element_ref": "rect#1",
                    "kind": "rect",
                    "role": "",
                    "opacity": 1,
                    "box": {"x": 0, "y": 0, "width": 1280, "height": 720},
                },
                {
                    "element_ref": "content-shell",
                    "kind": "rect",
                    "role": "",
                    "opacity": 1,
                    "box": {"x": 100, "y": 100, "width": 220, "height": 120},
                },
            ],
        })

        issue_ids = {issue["id"] for issue in issues}
        self.assertIn("overflow", issue_ids)
        self.assertNotIn("card_collision", issue_ids)


if __name__ == "__main__":
    unittest.main()
