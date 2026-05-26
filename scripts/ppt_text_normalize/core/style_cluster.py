from __future__ import annotations

from collections import defaultdict

from .model import TextBlock


def build_core_clusters(blocks: list[TextBlock], core_fields: tuple[str, ...] = ("font_family", "color")) -> list[dict[str, object]]:
    clusters: dict[tuple[object, ...], list[TextBlock]] = defaultdict(list)
    for block in blocks:
        key = tuple(getattr(block.style, field) for field in core_fields)
        clusters[key].append(block)
    total = len(blocks)
    rows: list[dict[str, object]] = []
    for key, members in clusters.items():
        row = {field: value for field, value in zip(core_fields, key)}
        row["members"] = members
        row["ratio"] = len(members) / total if total else 0.0
        rows.append(row)
    return sorted(rows, key=lambda item: len(item["members"]), reverse=True)
