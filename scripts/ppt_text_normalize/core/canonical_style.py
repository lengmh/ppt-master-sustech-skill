from __future__ import annotations

from collections import Counter

from .model import CanonicalStyle, StyleFingerprint, TextBlock, allowed_style_fields
from .style_cluster import build_core_clusters


def build_canonical_style(
    page_type: str,
    object_slot: str,
    slot_variant: str,
    permission_profile: str,
    blocks: list[TextBlock],
    source: str,
) -> CanonicalStyle:
    allowed_fields = allowed_style_fields(permission_profile, object_slot)
    core_fields = tuple(
        field
        for field in ("font_family", "east_asia_font_family", "bold", "color")
        if field in allowed_fields or (field == "east_asia_font_family" and "font_family" in allowed_fields)
    )
    if not core_fields:
        core_fields = ("font_family", "east_asia_font_family")
    clusters = build_core_clusters(blocks, core_fields=core_fields)
    if not clusters:
        raise ValueError("cannot build canonical style from empty block list")
    top = clusters[0]
    members = top["members"]
    style = StyleFingerprint(
        font_family=_majority([b.style.font_family for b in members]) if "font_family" in allowed_fields else None,
        east_asia_font_family=_majority([b.style.east_asia_font_family for b in members]) if "font_family" in allowed_fields else None,
        color=_majority([b.style.color for b in members]) if "color" in allowed_fields else None,
        font_size_pt=_majority([b.style.font_size_pt for b in members]) if "font_size_pt" in allowed_fields else None,
        bold=_majority([b.style.bold for b in members]) if "bold" in allowed_fields else None,
        italic=_majority([b.style.italic for b in members]) if "italic" in allowed_fields else None,
    )
    sample_count = len(blocks)
    ratio = float(top["ratio"])
    return CanonicalStyle(
        page_type=page_type,
        object_slot=object_slot,
        slot_variant=slot_variant,
        permission_profile=permission_profile,
        source=source,
        sample_count=sample_count,
        core_cluster_ratio=ratio,
        style=style,
        weak_canonical=sample_count < 3 or ratio < 0.6,
    )


def _majority(values):
    cleaned = [value for value in values if value is not None]
    if not cleaned:
        return None
    return Counter(cleaned).most_common(1)[0][0]
