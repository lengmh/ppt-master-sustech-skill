import unittest

from ppt_text_normalize.apply import _reviewed_fields_for_block
from ppt_text_normalize.core.review_decisions import compile_reviewed_rules


class VisualReviewFieldOverrideTest(unittest.TestCase):
    def _base_rules(self):
        return {
            "artifact_type": "ppt_text_normalize_rules",
            "canonical_styles": [],
            "slot_rules": [],
        }

    def _base_model(self, *, block_status="planned_change"):
        return {
            "artifact_type": "ppt_text_normalize_visual_review_model",
            "schema_version": "0.1",
            "source_rules": "rules.json",
            "groups": [
                {
                    "group_id": "group_title",
                    "allowed_fields": ["font_family"],
                    "default_fields": ["font_family"],
                    "optional_fields": [],
                    "target_style": {
                        "font_family": "Aptos",
                        "east_asia_font_family": "Microsoft YaHei",
                        "color": "#003F43",
                        "bold": True,
                    },
                }
            ],
            "blocks": [
                {
                    "block_id": "s01_sp02",
                    "status": block_status,
                    "allowed_fields": ["font_family"],
                    "planned_fields": ["font_family"],
                    "auto_group_id": "group_title",
                    "planned_group_id": "group_title",
                    "current_style": {
                        "font_family": "Arial",
                        "east_asia_font_family": "SimSun",
                        "color": "#111111",
                        "bold": False,
                    },
                }
            ],
        }

    def test_field_gate_override_allows_color_for_single_reviewed_block(self):
        reviewed = compile_reviewed_rules(
            rules=self._base_rules(),
            review_model_payload=self._base_model(),
            review_decisions_payload={
                "artifact_type": "ppt_text_normalize_review_decisions",
                "schema_version": "0.1",
                "review_model": "review_model.json",
                "decisions": [
                    {
                        "block_id": "s01_sp02",
                        "action": "use_group",
                        "group_id": "group_title",
                        "fields": ["font_family", "color"],
                        "override_field_gate": True,
                    }
                ],
            },
        )

        overrides = reviewed["reviewed_overrides"]
        self.assertEqual(overrides["block_fields"]["s01_sp02"], ["font_family", "color"])
        self.assertEqual(overrides["override_field_gate_block_ids"], ["s01_sp02"])
        self.assertEqual(
            _reviewed_fields_for_block("s01_sp02", ("font_family",), overrides),
            ("font_family", "color"),
        )

    def test_color_remains_rejected_without_field_gate_override(self):
        with self.assertRaisesRegex(ValueError, "field not allowed for block"):
            compile_reviewed_rules(
                rules=self._base_rules(),
                review_model_payload=self._base_model(),
                review_decisions_payload={
                    "artifact_type": "ppt_text_normalize_review_decisions",
                    "schema_version": "0.1",
                    "review_model": "review_model.json",
                    "decisions": [
                        {
                            "block_id": "s01_sp02",
                            "action": "use_group",
                            "group_id": "group_title",
                            "fields": ["font_family", "color"],
                        }
                    ],
                },
            )

    def test_field_gate_override_does_not_bypass_frozen_gate(self):
        reviewed = compile_reviewed_rules(
            rules=self._base_rules(),
            review_model_payload=self._base_model(block_status="frozen"),
            review_decisions_payload={
                "artifact_type": "ppt_text_normalize_review_decisions",
                "schema_version": "0.1",
                "review_model": "review_model.json",
                "decisions": [
                    {
                        "block_id": "s01_sp02",
                        "action": "use_group",
                        "group_id": "group_title",
                        "fields": ["font_family", "color"],
                        "override_field_gate": True,
                    }
                ],
            },
        )

        overrides = reviewed["reviewed_overrides"]
        self.assertEqual(overrides["excluded_block_ids"], ["s01_sp02"])
        self.assertEqual(overrides["block_fields"], {})
        self.assertEqual(overrides["override_field_gate_block_ids"], [])

    def test_field_gate_override_is_invalid_for_exclude_decision(self):
        with self.assertRaisesRegex(ValueError, "override_field_gate is invalid for exclude"):
            compile_reviewed_rules(
                rules=self._base_rules(),
                review_model_payload=self._base_model(),
                review_decisions_payload={
                    "artifact_type": "ppt_text_normalize_review_decisions",
                    "schema_version": "0.1",
                    "review_model": "review_model.json",
                    "decisions": [
                        {
                            "block_id": "s01_sp02",
                            "action": "exclude",
                            "override_field_gate": True,
                        }
                    ],
                },
            )

    def test_apply_field_gate_override_is_per_block(self):
        overrides = {
            "block_fields": {
                "s01_sp02": ["font_family", "color"],
                "s01_sp03": ["font_family", "color"],
            },
            "override_field_gate_block_ids": ["s01_sp02"],
        }

        self.assertEqual(
            _reviewed_fields_for_block("s01_sp02", ("font_family",), overrides),
            ("font_family", "color"),
        )
        self.assertEqual(
            _reviewed_fields_for_block("s01_sp03", ("font_family",), overrides),
            ("font_family",),
        )

    def test_field_gate_override_does_not_enable_font_size(self):
        with self.assertRaisesRegex(ValueError, "font_size_pt is disabled"):
            compile_reviewed_rules(
                rules=self._base_rules(),
                review_model_payload=self._base_model(),
                review_decisions_payload={
                    "artifact_type": "ppt_text_normalize_review_decisions",
                    "schema_version": "0.1",
                    "review_model": "review_model.json",
                    "decisions": [
                        {
                            "block_id": "s01_sp02",
                            "action": "use_group",
                            "group_id": "group_title",
                            "fields": ["font_size_pt"],
                            "override_field_gate": True,
                        }
                    ],
                },
            )

    def test_field_gate_override_does_not_make_unsupported_blocks_mutable(self):
        with self.assertRaisesRegex(ValueError, "unsupported block cannot be mutable"):
            compile_reviewed_rules(
                rules=self._base_rules(),
                review_model_payload=self._base_model(block_status="unsupported"),
                review_decisions_payload={
                    "artifact_type": "ppt_text_normalize_review_decisions",
                    "schema_version": "0.1",
                    "review_model": "review_model.json",
                    "decisions": [
                        {
                            "block_id": "s01_sp02",
                            "action": "use_group",
                            "group_id": "group_title",
                            "fields": ["font_family", "color"],
                            "override_field_gate": True,
                        }
                    ],
                },
            )


if __name__ == "__main__":
    unittest.main()
