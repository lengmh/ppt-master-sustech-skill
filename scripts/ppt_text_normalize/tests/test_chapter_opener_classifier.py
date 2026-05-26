import unittest

from ppt_text_normalize.core.model import StyleFingerprint, TextBlock
from ppt_text_normalize.core.role_classifier import classify_slide_semantics


class TestChapterOpenerClassifier(unittest.TestCase):
    def test_large_number_title_summary_layout_is_chapter_series(self):
        blocks = [
            TextBlock("s8_num", 8, "textbox", "02", left=708660, top=1870710, width=2561958, height=2682240,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", color="#003F43", font_size_pt=132.0, bold=True)),
            TextBlock("s8_title", 8, "textbox", "重塑零售空间", left=2886075, top=2662238, width=2895023, height=577081,
                      style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#003F43", font_size_pt=37.5, bold=True)),
            TextBlock("s8_subtitle", 8, "textbox", "不是卖产品，而是建立人与技术的连接", left=2931795, top=3308032, width=3597139, height=253916,
                      style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#585555", font_size_pt=16.5)),
            TextBlock("s8_b1", 8, "textbox", "• 关键词：开放、试用、服务、地标、公共性", left=3127058, top=3958114, width=3286156, height=196208,
                      style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#585555", font_size_pt=12.75)),
            TextBlock("s8_b2", 8, "textbox", "• 代表节点：第一家零售店、第五大道店、全球旗舰店", left=3127058, top=4281964, width=3940181, height=196208,
                      style=StyleFingerprint(font_family="FixtureCJKOutlier", east_asia_font_family="FixtureCJKOutlier", color="#585555", font_size_pt=12.75)),
            TextBlock("s8_footer", 8, "textbox", "Example Research Institute", left=863918, top=6600349, width=3228737, height=198120,
                      style=StyleFingerprint(font_family="FixtureLatinMajority", east_asia_font_family="FixtureCJKMajority", color="#9D9D9D", font_size_pt=9.75)),
        ]

        result = classify_slide_semantics(8, blocks, slide_count=15)

        self.assertEqual(result.page_type, "chapter")
        self.assertEqual(result.page_submode, "chapter@uniform_series")
        self.assertEqual(result.slot_resolutions["s8_num"].object_slot, "chapter_marker")
        self.assertEqual(result.slot_resolutions["s8_num"].mutation_permission_profile, "series_standard")
        self.assertEqual(result.slot_resolutions["s8_title"].object_slot, "chapter_title")
        self.assertEqual(result.slot_resolutions["s8_title"].mutation_permission_profile, "series_standard")


if __name__ == "__main__":
    unittest.main()
