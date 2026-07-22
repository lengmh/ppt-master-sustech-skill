#!/usr/bin/env python3
"""Readers and validators for legacy create-template brief locks.

New Create Template workspaces use ``design_spec.md`` as their only semantic
contract. This module remains available to inspect existing ``brief_lock.json``
artifacts without creating or updating them.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "artifact_type",
    "revision",
    "template_identity",
    "library_positioning",
    "style_contract",
    "canvas",
    "reference_source",
    "asset_policy",
    "designer_constraints",
    "open_assumptions",
}

REQUIRED_IDENTITY_KEYS = {"template_id", "display_name", "category"}
REQUIRED_POSITIONING_KEYS = {"applicable_scenarios", "keywords"}
REQUIRED_STYLE_KEYS = {"tone_summary", "design_style", "theme_mode", "theme_color"}
REQUIRED_CANVAS_KEYS = {"format"}
REQUIRED_REFERENCE_KEYS = {"type", "factual_findings"}
REQUIRED_ASSET_POLICY_KEYS = {"include", "exclude", "simplification_policy"}
REQUIRED_DESIGNER_CONSTRAINT_KEYS = {"placeholder_contract", "must_keep", "must_avoid"}
REQUIRED_REPLICATION_KEYS = {"mode", "fidelity_level"}


def _workspace_root(template_dir: Path) -> Path:
    path = Path(template_dir)
    if (path / "templates" / "design_spec.md").is_file():
        return path
    if path.name == "templates" and (path / "design_spec.md").is_file():
        return path.parent
    return path


def brief_lock_path(template_dir: Path) -> Path:
    return _workspace_root(Path(template_dir)) / "brief_lock.json"


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _require_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _require_string_list(name: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    return value


def validate_brief_lock(data: dict[str, Any]) -> None:
    missing = REQUIRED_TOP_LEVEL_KEYS - set(data)
    if missing:
        raise ValueError(f"brief_lock missing keys: {sorted(missing)}")

    if data.get("artifact_type") != "brief_lock":
        raise ValueError("artifact_type must be 'brief_lock'")
    if not isinstance(data.get("revision"), int) or data["revision"] < 1:
        raise ValueError("revision must be an integer >= 1")
    _require_string("schema_version", data.get("schema_version"))

    identity = _require_mapping("template_identity", data["template_identity"])
    missing_identity = REQUIRED_IDENTITY_KEYS - set(identity)
    if missing_identity:
        raise ValueError(f"template_identity missing keys: {sorted(missing_identity)}")
    for key in REQUIRED_IDENTITY_KEYS:
        _require_string(f"template_identity.{key}", identity.get(key))

    positioning = _require_mapping("library_positioning", data["library_positioning"])
    missing_positioning = REQUIRED_POSITIONING_KEYS - set(positioning)
    if missing_positioning:
        raise ValueError(f"library_positioning missing keys: {sorted(missing_positioning)}")
    _require_string_list("library_positioning.applicable_scenarios", positioning.get("applicable_scenarios"))
    _require_string_list("library_positioning.keywords", positioning.get("keywords"))

    style = _require_mapping("style_contract", data["style_contract"])
    missing_style = REQUIRED_STYLE_KEYS - set(style)
    if missing_style:
        raise ValueError(f"style_contract missing keys: {sorted(missing_style)}")
    for key in REQUIRED_STYLE_KEYS:
        _require_string(f"style_contract.{key}", style.get(key))

    canvas = _require_mapping("canvas", data["canvas"])
    missing_canvas = REQUIRED_CANVAS_KEYS - set(canvas)
    if missing_canvas:
        raise ValueError(f"canvas missing keys: {sorted(missing_canvas)}")
    _require_string("canvas.format", canvas.get("format"))

    reference_source = _require_mapping("reference_source", data["reference_source"])
    missing_reference = REQUIRED_REFERENCE_KEYS - set(reference_source)
    if missing_reference:
        raise ValueError(f"reference_source missing keys: {sorted(missing_reference)}")
    _require_string("reference_source.type", reference_source.get("type"))
    _require_string_list("reference_source.factual_findings", reference_source.get("factual_findings"))

    asset_policy = _require_mapping("asset_policy", data["asset_policy"])
    missing_asset_policy = REQUIRED_ASSET_POLICY_KEYS - set(asset_policy)
    if missing_asset_policy:
        raise ValueError(f"asset_policy missing keys: {sorted(missing_asset_policy)}")
    _require_string_list("asset_policy.include", asset_policy.get("include"))
    _require_string_list("asset_policy.exclude", asset_policy.get("exclude"))
    _require_string("asset_policy.simplification_policy", asset_policy.get("simplification_policy"))

    designer_constraints = _require_mapping("designer_constraints", data["designer_constraints"])
    missing_constraints = REQUIRED_DESIGNER_CONSTRAINT_KEYS - set(designer_constraints)
    if missing_constraints:
        raise ValueError(f"designer_constraints missing keys: {sorted(missing_constraints)}")
    _require_string("designer_constraints.placeholder_contract", designer_constraints.get("placeholder_contract"))
    _require_string_list("designer_constraints.must_keep", designer_constraints.get("must_keep"))
    _require_string_list("designer_constraints.must_avoid", designer_constraints.get("must_avoid"))

    replication = data.get("replication")
    if replication is not None:
        replication = _require_mapping("replication", replication)
        missing_replication = REQUIRED_REPLICATION_KEYS - set(replication)
        if missing_replication:
            raise ValueError(f"replication missing keys: {sorted(missing_replication)}")
        mode = _require_string("replication.mode", replication.get("mode"))
        if mode not in {"standard", "fidelity", "mirror"}:
            raise ValueError("replication.mode must be one of: standard, fidelity, mirror")
        fidelity_level = replication.get("fidelity_level")
        if mode == "mirror":
            if fidelity_level not in (None, "", "literal"):
                raise ValueError("replication.fidelity_level for mirror must be omitted, empty, or 'literal'")
        else:
            level = _require_string("replication.fidelity_level", fidelity_level)
            if level not in {"literal", "adapted"}:
                raise ValueError("replication.fidelity_level must be one of: literal, adapted")

    _require_string_list("open_assumptions", data.get("open_assumptions"))


def load_brief_lock(template_dir: Path) -> dict[str, Any]:
    template_dir = Path(template_dir)
    lock_path = brief_lock_path(template_dir)
    legacy_path = template_dir / "brief_lock.json"
    if not lock_path.exists() and legacy_path != lock_path and legacy_path.exists():
        lock_path = legacy_path
    payload = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("brief_lock root must be an object")
    validate_brief_lock(payload)
    return payload


__all__ = [
    "brief_lock_path",
    "load_brief_lock",
    "validate_brief_lock",
]
