import unittest

from ppt_text_normalize.core.model import StyleFingerprint, TextBlock
from ppt_text_normalize.core.role_classifier import classify_slide_semantics
from ppt_text_normalize.scan import build_rules_and_scan_report


class TestSlotVariantSafety(unittest.TestCase):
    def test_toc_secondary_title_uses_conservative_variant(self):
        blocks = [
            TextBlock("s2_title", 2, "textbox", "目录", left=845820, top=312420,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=24, bold=True)),
            TextBlock("s2_contents", 2, "textbox", "Contents", left=850868, top=793480,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=20.02, bold=None)),
            TextBlock("s2_01", 2, "textbox", "01 产品设计：极简主义的形成", left=1333500, top=1733550,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_02", 2, "textbox", "02 零售空间：购买变成体验", left=6572250, top=1733550,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_03", 2, "textbox", "03 历史建筑：更新而非覆盖", left=1333500, top=2819400,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_04", 2, "textbox", "04 系统设计：整体方法宣言", left=6572250, top=2819400,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
        ]

        result = classify_slide_semantics(2, blocks, slide_count=10)

        self.assertEqual(result.slot_resolutions["s2_title"].slot_variant, "toc_title@primary")
        self.assertEqual(result.slot_resolutions["s2_title"].mutation_permission_profile, "slot_standard")
        self.assertEqual(result.slot_resolutions["s2_contents"].slot_variant, "toc_title@secondary")
        self.assertEqual(result.slot_resolutions["s2_contents"].mutation_permission_profile, "conservative_text")

    def test_footer_org_name_and_page_num_do_not_share_color_canonical(self):
        blocks = []
        for slide in range(3, 8):
            blocks.extend([
                TextBlock(f"s{slide}_org", slide, "textbox", "Example Research Institute",
                          left=863918, top=6600349, width=3228737, height=198120,
                          style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#9D9D9D", font_size_pt=9.75)),
                TextBlock(f"s{slide}_num", slide, "textbox", f"{slide:02d}",
                          left=11098035, top=6576060, width=300000, height=198120,
                          style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#003F43", font_size_pt=12.0, bold=True)),
                TextBlock(f"s{slide}_note", slide, "textbox", "页面说明文字",
                          left=2650808, top=5269706, width=3000000, height=198120,
                          style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#585555", font_size_pt=11.25)),
            ])

        rules, _report = build_rules_and_scan_report("demo.pptx", slide_count=8, blocks=blocks)
        org = next(item for item in rules["canonical_styles"] if item["object_slot"] == "footer" and item["slot_variant"] == "footer@org_name")
        page_num = next(item for item in rules["canonical_styles"] if item["object_slot"] == "footer" and item["slot_variant"] == "footer@page_num")
        note = next(item for item in rules["canonical_styles"] if item["object_slot"] == "footer" and item["slot_variant"] == "footer@note")

        self.assertEqual(org["style"]["color"], "#9D9D9D")
        self.assertEqual(page_num["style"]["color"], "#003F43")
        self.assertIsNone(note["style"]["color"])

    def test_weak_canonical_reduces_allowed_fields_to_font_family(self):
        from ppt_text_normalize.apply import _effective_allowed_fields

        self.assertEqual(
            _effective_allowed_fields(("font_family", "bold", "color"), {"weak_canonical": True}),
            ("font_family",),
        )


if __name__ == "__main__":
    unittest.main()
