from pathlib import Path
import unittest

from ppt_text_normalize.core.canonical_style import build_canonical_style
from ppt_text_normalize.core.model import StyleFingerprint, TextBlock


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_PATHS = [
    REPO_ROOT / "ppt_text_normalize" / "scan.py",
    REPO_ROOT / "ppt_text_normalize" / "apply.py",
    *(REPO_ROOT / "ppt_text_normalize" / "core").glob("*.py"),
]


class TestNoFixtureHardcoding(unittest.TestCase):
    def test_production_code_does_not_contain_sample_fixture_identifiers(self):
        forbidden_literals = (
            "测试案例1",
            "apple_sustech_learning_dense",
            "Southern University of Science and Technology",
            "safe_mvp_validation",
            "example_dense",
            "宋体",
            "黑体",
            "SimSun",
            "SimHei",
            "Microsoft YaHei",
            "微软雅黑",
        )

        hits: list[str] = []
        for path in PRODUCTION_PATHS:
            content = path.read_text(encoding="utf-8")
            for literal in forbidden_literals:
                if literal in content:
                    hits.append(f"{path.relative_to(REPO_ROOT)} contains {literal!r}")

        self.assertEqual(hits, [])

    def test_canonical_font_family_is_data_driven_not_specific_font_driven(self):
        blocks = [
            TextBlock(
                "s1_a",
                1,
                "textbox",
                "目录项 A",
                style=StyleFingerprint(font_family="FixtureMajoritySans", east_asia_font_family="FixtureMajorityCJK", bold=True),
            ),
            TextBlock(
                "s1_b",
                1,
                "textbox",
                "目录项 B",
                style=StyleFingerprint(font_family="FixtureMajoritySans", east_asia_font_family="FixtureMajorityCJK", bold=True),
            ),
            TextBlock(
                "s1_c",
                1,
                "textbox",
                "目录项 C",
                style=StyleFingerprint(font_family="FixtureMinoritySerif", east_asia_font_family="FixtureMinorityCJK", bold=True),
            ),
        ]

        canonical = build_canonical_style(
            "toc",
            "toc_item",
            "toc_item@uniform_grid_title",
            "list_standard",
            blocks,
            "majority_real_slide",
        )

        self.assertEqual(canonical.style.font_family, "FixtureMajoritySans")
        self.assertEqual(canonical.style.east_asia_font_family, "FixtureMajorityCJK")


if __name__ == "__main__":
    unittest.main()
