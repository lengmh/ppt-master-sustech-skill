from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def effective_allowed_fields(
    allowed_fields: tuple[str, ...],
    canonical_entry: Mapping[str, Any] | None,
    slot_rule: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Apply final Safe MVP field narrowing shared by preview and apply.

    This helper intentionally preserves the existing conservative behavior from
    ``apply.py`` so the visual review model never previews fields that the apply
    path would later refuse.
    """
    fields = tuple(allowed_fields)
    canonical_entry = canonical_entry or {}
    slot_rule = slot_rule or {}
    slot_variant = str(slot_rule.get("resolved_slot_variant") or "")

    if canonical_entry.get("weak_canonical"):
        fields = tuple(field for field in fields if field == "font_family")
    if slot_variant == "toc_title@secondary":
        fields = tuple(field for field in fields if field == "font_family")
    if slot_variant == "footer@note":
        fields = tuple(field for field in fields if field == "font_family")
    return fields
