from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SLOT_VARIANT_CONFIDENCE_THRESHOLD = 0.85
FOOTER_VARIANTS_PRESERVED_BELOW_THRESHOLD = {"footer@org_name", "footer@page_num", "footer@note"}


def canonical_variant_for_slot(slot_rule: Any) -> str:
    object_slot = str(_get(slot_rule, "resolved_object_slot", _get(slot_rule, "object_slot", "unknown")) or "unknown")
    variant = str(_get(slot_rule, "resolved_slot_variant", _get(slot_rule, "slot_variant", f"{object_slot}@default")) or f"{object_slot}@default")
    confidence = _float(_get(slot_rule, "slot_variant_confidence", 0.0))
    if confidence >= SLOT_VARIANT_CONFIDENCE_THRESHOLD:
        return variant
    if object_slot == "footer" and variant in FOOTER_VARIANTS_PRESERVED_BELOW_THRESHOLD:
        return variant
    return f"{object_slot}@default"


def canonical_key_for_rule_entry(entry: Mapping[str, Any]) -> tuple[str, str, str, str]:
    object_slot = str(entry.get("object_slot") or "unknown")
    return (
        str(entry.get("page_type") or "unknown"),
        object_slot,
        str(entry.get("slot_variant") or f"{object_slot}@default"),
        str(entry.get("permission_profile") or entry.get("mutation_permission_profile") or "conservative_text"),
    )


def canonical_key_for_block(page_rule: Mapping[str, Any] | None, slot_rule: Mapping[str, Any] | None) -> tuple[str, str, str, str] | None:
    if not page_rule or not slot_rule:
        return None
    object_slot = str(slot_rule.get("resolved_object_slot") or "unknown")
    return (
        str(page_rule.get("resolved_page_type") or "unknown"),
        object_slot,
        canonical_variant_for_slot(slot_rule),
        str(slot_rule.get("mutation_permission_profile") or "conservative_text"),
    )


def _get(source: Any, key: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
