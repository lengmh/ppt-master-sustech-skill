import unittest

from ppt_text_normalize.core.model import StyleFingerprint, TextBlock
from ppt_text_normalize.core.role_classifier import classify_slide_semantics
from ppt_text_normalize.scan import build_rules_and_scan_report


class TestTocGridEastAsia(unittest.TestCase):
    def test_toc_two_column_grid_is_uniform_grid_and_title_items_are_eligible(self):
        blocks = [
            TextBlock("s2_title", 2, "textbox", "目录", top=312420, left=845820, width=1200000, height=400000,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=24, bold=True)),
            TextBlock("s2_01", 2, "textbox", "01 产品设计：极简主义的形成", top=1733550, left=1333500, width=3600000, height=350000,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_02", 2, "textbox", "02 零售空间：购买变成体验", top=1733550, left=6572250, width=3600000, height=350000,
                      style=StyleFingerprint(font_family="FixtureCJKMinority", east_asia_font_family="FixtureCJKMinority", font_size_pt=15, bold=True)),
            TextBlock("s2_03", 2, "textbox", "03 历史建筑：更新而非覆盖", top=2819400, left=1333500, width=3600000, height=350000,
                      style=StyleFingerprint(font_family="FixtureCJKMinority", east_asia_font_family="FixtureCJKMinority", font_size_pt=15, bold=True)),
            TextBlock("s2_04", 2, "textbox", "04 系统设计：整体方法宣言", top=2819400, left=6572250, width=3600000, height=350000,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_05", 2, "textbox", "05 方法抽取：设计原则", top=3905250, left=1333500, width=3600000, height=350000,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_06", 2, "textbox", "06 课堂讨论：迁移应用", top=3905250, left=6572250, width=3600000, height=350000,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s2_footer_page", 2, "textbox", "02", top=6576060, left=11098035, width=300000, height=200000,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=12, bold=True)),
        ]
        result = classify_slide_semantics(2, blocks, slide_count=8)
        self.assertEqual(result.page_type, "toc")
        self.assertEqual(result.page_submode, "toc@uniform_grid")
        self.assertEqual(result.slot_resolutions["s2_title"].object_slot, "toc_title")
        self.assertEqual(result.slot_resolutions["s2_footer_page"].object_slot, "footer")
        self.assertEqual(result.slot_resolutions["s2_02"].object_slot, "toc_item")
        self.assertEqual(result.slot_resolutions["s2_02"].slot_variant, "toc_item@uniform_grid_title")
        self.assertEqual(result.slot_resolutions["s2_02"].mutation_permission_profile, "list_standard")
        self.assertTrue(result.slot_resolutions["s2_02"].uniformity_eligible)

    def test_numbered_content_grid_without_toc_context_is_not_toc(self):
        blocks = [
            TextBlock("s3_title", 3, "textbox", "为什么研究这个设计案例？", top=312420, left=845820,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=24, bold=True)),
            TextBlock("s3_q1", 3, "textbox", "1. 它解决了什么使用障碍？", top=3950018, left=1411605,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=13.5)),
            TextBlock("s3_q2", 3, "textbox", "2. 它用了哪些形式语言与空间策略？", top=4311968, left=1411605,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=13.5)),
            TextBlock("s3_q3", 3, "textbox", "3. 它如何改变人与技术的关系？", top=3950018, left=6174105,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=13.5)),
            TextBlock("s3_q4", 3, "textbox", "4. 这些方法能否迁移到学习场景？", top=4311968, left=6174105,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=13.5)),
        ]
        result = classify_slide_semantics(3, blocks, slide_count=8)
        self.assertNotEqual(result.page_type, "toc")
        self.assertNotEqual(result.page_submode, "toc@uniform_grid")

    def test_timeline_years_without_toc_context_are_not_toc_items(self):
        blocks = [
            TextBlock("s4_title", 4, "textbox", "50年设计演进时间线", top=312420, left=845820,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=24, bold=True)),
            TextBlock("s4_y1", 4, "textbox", "1976", top=2238375, left=1109222,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s4_y2", 4, "textbox", "1998", top=2238375, left=3566168,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s4_y3", 4, "textbox", "2007", top=2238375, left=6625268,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
            TextBlock("s4_y4", 4, "textbox", "2017", top=2238375, left=8633972,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", font_size_pt=15, bold=True)),
        ]
        result = classify_slide_semantics(4, blocks, slide_count=8)
        self.assertNotEqual(result.page_type, "toc")

    def test_scan_canonical_for_toc_grid_preserves_size_and_color_but_sets_east_asia_majority(self):
        blocks = [
            TextBlock("s2_01", 2, "textbox", "01 产品设计：极简主义的形成", top=1733550, left=1333500,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", color="#003F43", font_size_pt=15, bold=True)),
            TextBlock("s2_02", 2, "textbox", "02 零售空间：购买变成体验", top=1733550, left=6572250,
                      style=StyleFingerprint(font_family="FixtureCJKMinority", east_asia_font_family="FixtureCJKMinority", color="#E3660D", font_size_pt=15, bold=True)),
            TextBlock("s2_03", 2, "textbox", "03 历史建筑：更新而非覆盖", top=2819400, left=1333500,
                      style=StyleFingerprint(font_family="FixtureCJKMinority", east_asia_font_family="FixtureCJKMinority", color="#01ABA8", font_size_pt=15, bold=True)),
            TextBlock("s2_04", 2, "textbox", "04 系统设计：整体方法宣言", top=2819400, left=6572250,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", color="#B63742", font_size_pt=15, bold=True)),
            TextBlock("s2_05", 2, "textbox", "05 方法抽取：设计原则", top=3905250, left=1333500,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", color="#003F43", font_size_pt=15, bold=True)),
            TextBlock("s2_06", 2, "textbox", "06 课堂讨论：迁移应用", top=3905250, left=6572250,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", color="#E3660D", font_size_pt=15, bold=True)),
        ]
        rules, _report = build_rules_and_scan_report("demo.pptx", slide_count=3, blocks=blocks)
        canonical = next(item for item in rules["canonical_styles"] if item["object_slot"] == "toc_item")
        self.assertEqual(canonical["slot_variant"], "toc_item@uniform_grid_title")
        self.assertEqual(canonical["style"]["font_family"], "FixtureLatinMajority")
        self.assertEqual(canonical["style"]["east_asia_font_family"], "FixtureCJKMajority")
        self.assertIsNone(canonical["style"]["font_size_pt"])
        self.assertIsNone(canonical["style"]["color"])


if __name__ == "__main__":
    unittest.main()
