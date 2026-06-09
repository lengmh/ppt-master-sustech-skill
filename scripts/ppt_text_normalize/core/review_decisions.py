from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

ALLOWED_REVIEW_FIELDS = ("font_family", "bold", "color")
USER_GROUP_RE = re.compile(r"^user_group_[A-Za-z0-9_-]+$")


def compile_reviewed_rules(
    *,
    rules: dict[str, Any],
    review_model_payload: dict[str, Any],
    review_decisions_payload: dict[str, Any],
    source_rules_path: str = "rules.json",
    review_model_path: str = "review_model.json",
    review_decisions_path: str = "review_decisions.json",
) -> dict[str, Any]:
    _validate_payload_identity(
        review_model_payload=review_model_payload,
        review_decisions_payload=review_decisions_payload,
        source_rules_path=source_rules_path,
        review_model_path=review_model_path,
        review_decisions_path=review_decisions_path,
    )
    blocks = {item["block_id"]: item for item in review_model_payload.get("blocks", [])}
    groups = {item["group_id"]: item for item in review_model_payload.get("groups", [])}
    decisions = list(review_decisions_payload.get("decisions") or [])

    excluded: set[str] = set()
    assignments: dict[str, str] = {}
    block_fields: dict[str, list[str]] = {}
    user_groups: dict[str, dict[str, Any]] = _collect_user_groups(decisions, blocks)
    override_ids: set[str] = set()
    override_field_gate_ids: set[str] = set()

    for decision in decisions:
        if not isinstance(decision, dict):
            raise ValueError("each review decision must be an object")
        block_id = _require_str(decision, "block_id")
        if block_id not in blocks:
            raise ValueError(f"unknown block_id: {block_id}")
        action = _require_str(decision, "action")
        block = blocks[block_id]
        override = bool(decision.get("override_frozen_skip"))
        override_field_gate = bool(decision.get("override_field_gate"))
        fields = _normalize_fields(decision.get("fields") if "fields" in decision else None)

        if action == "exclude":
            if override:
                raise ValueError("override_frozen_skip is invalid for exclude")
            if override_field_gate:
                raise ValueError("override_field_gate is invalid for exclude")
            excluded.add(block_id)
            continue

        if block.get("status") == "unsupported":
            raise ValueError(f"unsupported block cannot be mutable: {block_id}")
        if block.get("status") in {"frozen", "skipped"} and not override:
            excluded.add(block_id)
            continue
        if override:
            override_ids.add(block_id)

        if action == "keep_auto":
            group_id = block.get("auto_group_id") or block.get("planned_group_id")
            if not group_id or group_id not in groups:
                raise ValueError(f"block has no auto group: {block_id}")
        elif action == "use_group":
            group_id = _require_str(decision, "group_id")
            if group_id not in groups and group_id not in user_groups:
                raise ValueError(f"unknown group_id: {group_id}")
        elif action == "create_group":
            group_id = _require_str(decision, "new_group_id")
            if not USER_GROUP_RE.match(group_id):
                raise ValueError(f"invalid new_group_id: {group_id}")
            reference_block_id = _require_str(decision, "reference_block_id")
            reference = blocks.get(reference_block_id)
            if reference is None:
                raise ValueError(f"unknown reference_block_id: {reference_block_id}")
            if reference.get("status") == "unsupported":
                raise ValueError(f"unsupported reference block: {reference_block_id}")
            user_groups[group_id] = {
                "reference_block_id": reference_block_id,
                "target_style": dict(reference.get("current_style") or {}),
                "fields": fields if fields is not None else ["font_family", "bold"],
                "override_field_gate": override_field_gate,
            }
            label = decision.get("label")
            if isinstance(label, str) and label.strip():
                user_groups[group_id]["label"] = label.strip()
        else:
            raise ValueError(f"unsupported review action: {action}")

        if fields == []:
            raise ValueError(f"at least one field is required for mutating decision: {block_id}")
        if fields is None:
            if group_id in groups:
                fields = list(groups[group_id].get("default_fields") or ["font_family"])
            elif group_id in user_groups:
                fields = list(user_groups[group_id].get("fields") or ["font_family", "bold"])
            else:
                fields = ["font_family"]
        _validate_fields_allowed_for_decision(block_id, fields, block, groups.get(group_id), user_groups.get(group_id), override_field_gate=override_field_gate)
        if override_field_gate:
            override_field_gate_ids.add(block_id)
        assignments[block_id] = group_id
        block_fields[block_id] = fields

    for block_id, block in blocks.items():
        if block.get("status") in {"frozen", "skipped"} and block_id not in assignments and block_id not in override_ids:
            excluded.add(block_id)

    reviewed = copy.deepcopy(rules)
    reviewed["review_gate"] = {
        "type": "visual_live_preview",
        "schema_version": "0.1",
        "source_rules": source_rules_path,
        "review_model": review_model_path,
        "review_decisions": review_decisions_path,
        "status": "reviewed",
    }
    reviewed["reviewed_overrides"] = {
        "excluded_block_ids": sorted(excluded),
        "block_group_assignments": dict(sorted(assignments.items())),
        "block_fields": {key: block_fields[key] for key in sorted(block_fields)},
        "user_groups": {key: user_groups[key] for key in sorted(user_groups)},
        "override_frozen_skip_block_ids": sorted(override_ids),
        "override_field_gate_block_ids": sorted(override_field_gate_ids),
    }
    return reviewed


def _collect_user_groups(decisions: list[Any], blocks: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    user_groups: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict) or decision.get("action") != "create_group":
            continue
        group_id = _require_str(decision, "new_group_id")
        if not USER_GROUP_RE.match(group_id):
            raise ValueError(f"invalid new_group_id: {group_id}")
        reference_block_id = _require_str(decision, "reference_block_id")
        reference = blocks.get(reference_block_id)
        if reference is None:
            raise ValueError(f"unknown reference_block_id: {reference_block_id}")
        if reference.get("status") == "unsupported":
            raise ValueError(f"unsupported reference block: {reference_block_id}")
        if reference.get("status") in {"frozen", "skipped"} and not bool(decision.get("override_frozen_skip")):
            continue
        fields = _normalize_fields(decision.get("fields") if "fields" in decision else None)
        if fields == []:
            raise ValueError(f"at least one field is required for user group: {group_id}")
        if fields is None:
            fields = ["font_family", "bold"]
        _validate_fields_allowed_for_block(reference_block_id, fields, reference, override_field_gate=bool(decision.get("override_field_gate")))
        user_groups[group_id] = {
            "reference_block_id": reference_block_id,
            "target_style": dict(reference.get("current_style") or {}),
            "fields": fields,
        }
        label = decision.get("label")
        if isinstance(label, str) and label.strip():
            user_groups[group_id]["label"] = label.strip()
    return user_groups


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing or invalid {key}")
    return value


def _validate_payload_identity(
    *,
    review_model_payload: dict[str, Any],
    review_decisions_payload: dict[str, Any],
    source_rules_path: str,
    review_model_path: str,
    review_decisions_path: str,
) -> None:
    if review_model_payload.get("artifact_type") is not None and review_model_payload.get("artifact_type") != "ppt_text_normalize_visual_review_model":
        raise ValueError("invalid review_model artifact_type")
    if review_model_payload.get("schema_version") is not None and review_model_payload.get("schema_version") != "0.1":
        raise ValueError("unsupported review_model schema_version")
    if review_decisions_payload.get("artifact_type") is not None and review_decisions_payload.get("artifact_type") != "ppt_text_normalize_review_decisions":
        raise ValueError("invalid review_decisions artifact_type")
    if review_decisions_payload.get("schema_version") is not None and review_decisions_payload.get("schema_version") != "0.1":
        raise ValueError("unsupported review_decisions schema_version")
    declared_model = review_decisions_payload.get("review_model")
    if declared_model and not _path_reference_matches(str(declared_model), review_model_path, Path(review_decisions_path).parent):
        raise ValueError("review_model path does not match decisions payload")
    declared_rules = review_model_payload.get("source_rules")
    if declared_rules and not _path_reference_matches(str(declared_rules), source_rules_path, Path(review_model_path).parent):
        raise ValueError("source_rules path does not match review model")


def _path_reference_matches(declared: str, actual: str, base_dir: Path) -> bool:
    if declared == actual:
        return True
    declared_path = Path(declared)
    actual_path = Path(actual)
    if declared_path.is_absolute():
        return declared_path.resolve(strict=False) == actual_path.resolve(strict=False)
    if len(declared_path.parts) == 1 and declared_path.name == actual_path.name:
        return True
    return (base_dir / declared_path).resolve(strict=False) == actual_path.resolve(strict=False)


def _validate_fields_allowed_for_decision(
    block_id: str,
    fields: list[str],
    block: dict[str, Any],
    group: dict[str, Any] | None,
    user_group: dict[str, Any] | None,
    *,
    override_field_gate: bool = False,
) -> None:
    _validate_fields_allowed_for_block(block_id, fields, block, override_field_gate=override_field_gate)
    group_allowed = _allowed_fields_for_group(group, user_group, override_field_gate=override_field_gate)
    for field in fields:
        if field not in group_allowed:
            raise ValueError(f"field not allowed for selected group {block_id}: {field}")


def _allowed_fields_for_group(group: dict[str, Any] | None, user_group: dict[str, Any] | None, *, override_field_gate: bool = False) -> set[str]:
    if override_field_gate:
        return set(ALLOWED_REVIEW_FIELDS)
    if user_group is not None:
        return set(user_group.get("fields") or ALLOWED_REVIEW_FIELDS)
    if group is None:
        return set(ALLOWED_REVIEW_FIELDS)
    allowed = group.get("allowed_fields")
    if allowed is None:
        allowed = list(group.get("default_fields") or []) + list(group.get("optional_fields") or [])
    if allowed is None:
        allowed = ALLOWED_REVIEW_FIELDS
    return set(allowed)


def _validate_fields_allowed_for_block(block_id: str, fields: list[str], block: dict[str, Any], *, override_field_gate: bool = False) -> None:
    allowed = ALLOWED_REVIEW_FIELDS if override_field_gate else block.get("allowed_fields")
    if allowed is None:
        allowed = block.get("planned_fields")
    if allowed is None:
        allowed = ALLOWED_REVIEW_FIELDS
    allowed_set = set(allowed)
    for field in fields:
        if field not in allowed_set:
            raise ValueError(f"field not allowed for block {block_id}: {field}")


def _normalize_fields(value: Any) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError("fields must be a list")
    out: list[str] = []
    for field in value:
        if field == "font_size_pt":
            raise ValueError("font_size_pt is disabled in visual review MVP")
        if field not in ALLOWED_REVIEW_FIELDS:
            raise ValueError(f"unsupported field: {field}")
        if field not in out:
            out.append(field)
    return out
