from __future__ import annotations

from .model import (
    HeroDecision,
    ObjectSlotResolution,
    RoleMatch,
    SlideClassification,
    SlideSemanticResolution,
    TextBlock,
)

EMU_PER_PX = 9525


def classify_slide_semantics(slide_index: int, blocks: list[TextBlock], slide_count: int) -> SlideSemanticResolution:
    page_scores = _score_page_type(slide_index, blocks, slide_count)
    page_type, page_confidence, _page_margin, page_ambiguous = _resolve_scores(page_scores)
    hero_decision = _detect_hero_page(blocks)
    if hero_decision.is_frozen:
        page_type = "hero"
        page_confidence = max(page_confidence, hero_decision.page_confidence)
    page_submode, page_submode_confidence = _resolve_page_submode(page_type, blocks, hero_decision)
    slot_resolutions = {
        block.block_id: _classify_slot(block, blocks, page_type, page_submode, hero_decision, page_ambiguous)
        for block in blocks
    }
    signals = tuple(sorted(k for k, v in page_scores.items() if v > 0))
    if hero_decision.reasons:
        signals = signals + tuple(f"hero:{reason}" for reason in hero_decision.reasons)
    return SlideSemanticResolution(
        page_type=page_type,
        page_type_confidence=page_confidence,
        page_submode=page_submode,
        page_submode_confidence=page_submode_confidence,
        hero_decision=hero_decision,
        slot_resolutions=slot_resolutions,
        signals=signals,
    )


def _score_page_type(slide_index: int, blocks: list[TextBlock], slide_count: int) -> dict[str, float]:
    scores = {name: 0.0 for name in ["cover", "chapter", "toc", "content", "ending", "unknown"]}
    text_joined = " ".join(block.text.lower() for block in blocks)
    has_toc_context = _has_toc_context(blocks)
    chapter_opener_confidence = _chapter_opener_confidence(blocks)
    if has_toc_context:
        scores["toc"] += 3.0
    if any(keyword in text_joined for keyword in ["谢谢", "thanks", "q&a", "qa"]):
        scores["ending"] += 3.0
    if any(keyword in text_joined for keyword in ["chapter", "part", "section", "第1章", "第2章", "第一章", "第二章", "章节"]):
        scores["chapter"] += 2.0
    if chapter_opener_confidence >= 0.75:
        scores["chapter"] += 3.2
    if slide_index == 1:
        scores["cover"] += 1.2
    if slide_index >= max(slide_count - 1, 1):
        scores["ending"] += 1.0
    if any(block.container_type == "table_cell" for block in blocks):
        scores["content"] += 2.0
    if len(blocks) >= 2:
        scores["content"] += 1.5
    if any((block.style.font_size_pt or 0) >= 24 for block in blocks):
        scores["content"] += 0.8
    strong_toc_titles = [block for block in blocks if _looks_like_toc_item_title(block, has_toc_context=has_toc_context)]
    if len(strong_toc_titles) >= 4 and _looks_like_uniform_toc_grid(strong_toc_titles):
        scores["toc"] += 2.5
    if len(blocks) <= 2 and max(((block.style.font_size_pt or 0) for block in blocks), default=0) >= 28:
        scores["cover"] += 0.8
        scores["chapter"] += 0.5
    if max(scores.values()) == 0:
        scores["unknown"] = 1.0
    return scores


def _detect_hero_page(blocks: list[TextBlock]) -> HeroDecision:
    if not blocks:
        return HeroDecision(False)
    max_size = max((block.style.font_size_pt or 0.0) for block in blocks)
    text_count = len([block for block in blocks if block.text.strip()])
    reasons: list[str] = []
    score = 0.0
    if text_count <= 2:
        score += 0.35
        reasons.append("low_text_count")
    if max_size >= 36:
        score += 0.4
        reasons.append("dominant_large_text")
    if text_count == 1 and max_size >= 28:
        score += 0.25
        reasons.append("single_statement")
    confidence = round(min(score, 1.0), 4)
    return HeroDecision(is_frozen=confidence >= 0.7, page_confidence=confidence, reasons=tuple(reasons))


def _resolve_page_submode(page_type: str, blocks: list[TextBlock], hero_decision: HeroDecision) -> tuple[str, float]:
    if page_type == "hero":
        return "content@hero_mixed", hero_decision.page_confidence
    if page_type == "toc":
        has_toc_context = _has_toc_context(blocks)
        title_items = [block for block in blocks if _looks_like_toc_item_title(block, has_toc_context=has_toc_context)]
        if _looks_like_uniform_toc_grid(title_items):
            return "toc@uniform_grid", 0.84
        item_like = [block for block in blocks if _looks_like_toc_item(block, has_toc_context=has_toc_context)]
        if len(item_like) >= 3 and _tops_are_regular(item_like):
            return "toc@uniform_list", 0.82
        return "toc@freeform_composition", 0.65
    if page_type == "chapter":
        if _looks_like_chapter_opener(blocks):
            return "chapter@uniform_series", 0.82
        if hero_decision.page_confidence >= 0.55:
            return "chapter@freeform_hero", max(hero_decision.page_confidence, 0.7)
        return "chapter@uniform_series", 0.62
    if page_type == "cover":
        return ("cover@hero_like", 0.72) if hero_decision.page_confidence >= 0.55 else ("cover@standard", 0.68)
    if page_type == "ending":
        return ("ending@hero_like", 0.72) if hero_decision.page_confidence >= 0.55 else ("ending@standard", 0.68)
    if page_type == "content":
        return ("content@hero_mixed", 0.72) if hero_decision.page_confidence >= 0.55 else ("content@standard", 0.78)
    return "unknown@default", 0.5


def _classify_slot(
    block: TextBlock,
    blocks: list[TextBlock],
    page_type: str,
    page_submode: str,
    hero_decision: HeroDecision,
    page_ambiguous: bool,
) -> ObjectSlotResolution:
    if hero_decision.is_frozen and _is_dominant_text(block, blocks):
        return ObjectSlotResolution("hero", 0.9, "hero@dominant_statement", 0.8, None, False, "frozen", hero_decision.page_confidence, "hero_frozen")
    if page_ambiguous:
        return ObjectSlotResolution("unknown", 0.3, "unknown@ambiguous", 0.3, None, False, "conservative_text", 0.0, "page_type_low_confidence")
    if block.container_type == "table_cell":
        return ObjectSlotResolution("table_text", 0.95, "table_text@cell", 0.9, None, True, "typography_only")
    if _is_header(block):
        return ObjectSlotResolution("header", 0.72, "header@top_chrome", 0.62, None, True, "slot_standard")
    if _is_footer(block):
        return _classify_footer_slot(block)
    if page_type == "toc" and _looks_like_toc_title(block):
        if _is_secondary_toc_title(block, blocks):
            return ObjectSlotResolution("toc_title", 0.82, "toc_title@secondary", 0.88, None, True, "conservative_text")
        return ObjectSlotResolution("toc_title", 0.86, "toc_title@primary", 0.9, None, True, "slot_standard")
    if page_type == "toc" and _looks_like_toc_item(block, has_toc_context=_has_toc_context(blocks)):
        if page_submode == "toc@uniform_grid" and _looks_like_toc_item_title(block, has_toc_context=_has_toc_context(blocks)):
            return ObjectSlotResolution("toc_item", 0.84, "toc_item@uniform_grid_title", 0.9, "toc_item_title", True, "list_standard")
        if page_submode == "toc@uniform_grid":
            return ObjectSlotResolution("toc_item", 0.68, "toc_item@uniform_grid_desc", 0.76, "toc_item_desc", True, "conservative_text")
        profile = "list_standard" if page_submode == "toc@uniform_list" else "conservative_text"
        eligible = page_submode == "toc@uniform_list"
        return ObjectSlotResolution("toc_item", 0.78, "toc_item@uniform_list" if eligible else "toc_item@freeform", 0.7, None, eligible, profile)
    if page_type == "chapter" and _is_chapter_marker(block):
        profile = "series_standard" if page_submode == "chapter@uniform_series" else "frozen"
        eligible = page_submode == "chapter@uniform_series"
        skip_reason = None if eligible else "hero_frozen"
        return ObjectSlotResolution("chapter_marker", 0.88, "chapter_marker@large_number", 0.84, None, eligible, profile, 0.0, skip_reason)
    if page_type == "chapter" and _is_chapter_title(block, blocks):
        profile = "series_standard" if page_submode == "chapter@uniform_series" else "frozen"
        eligible = page_submode == "chapter@uniform_series"
        skip_reason = None if eligible else "hero_frozen"
        return ObjectSlotResolution("chapter_title", 0.84, "chapter_title@standard", 0.76, None, eligible, profile, 0.0, skip_reason)
    if _is_page_title(block, blocks):
        return ObjectSlotResolution("page_title", 0.84, "page_title@standard_top", 0.72, None, True, "slot_standard")
    role, confidence = _content_intent(block)
    if confidence < 0.55:
        return ObjectSlotResolution("unknown", confidence, "unknown@content_area", confidence, None, False, "conservative_text", 0.0, "role_low_confidence")
    profile = {
        "content_body": "typography_only",
        "content_label": "typography_only",
        "content_emphasis": "preserve_emphasis",
        "content_caption": "conservative_text",
        "content_stat": "typography_only",
    }[role]
    return ObjectSlotResolution(role, confidence, f"{role}@standard", confidence, role, True, profile)


def _content_intent(block: TextBlock) -> tuple[str, float]:
    text = block.text.strip()
    text_len = len(text.replace("\n", ""))
    size = block.style.font_size_pt or 0.0
    if any(ch.isdigit() for ch in text) and text_len <= 18 and size >= 20:
        return "content_stat", 0.72
    if text_len <= 12 and (block.style.bold or size >= 18):
        return "content_label", 0.68
    if size <= 13 or block.top >= 500:
        return "content_caption", 0.66
    if size >= 22 and text_len <= 30:
        return "content_emphasis", 0.62
    if text_len >= 18 or (block.paragraph_count or block.paragraphs) >= 2:
        return "content_body", 0.78
    return "content_body", 0.56


def _has_toc_context(blocks: list[TextBlock]) -> bool:
    return any(_looks_like_toc_title(block) for block in blocks)


def _classify_footer_slot(block: TextBlock) -> ObjectSlotResolution:
    variant = "footer@note"
    confidence = 0.7
    profile = "conservative_text"
    text = block.text.strip()
    if _looks_like_page_number(block):
        variant = "footer@page_num"
        confidence = 0.86
        profile = "slot_standard"
    elif _looks_like_org_footer(block):
        variant = "footer@org_name"
        confidence = 0.86
        profile = "slot_standard"
    return ObjectSlotResolution("footer", confidence, variant, 0.88, None, True, profile)


def _is_secondary_toc_title(block: TextBlock, blocks: list[TextBlock]) -> bool:
    toc_titles = sorted([item for item in blocks if _looks_like_toc_title(item)], key=lambda item: item.top)
    if not toc_titles:
        return False
    first = toc_titles[0]
    return block is not first and block.top > first.top


def _looks_like_page_number(block: TextBlock) -> bool:
    text = block.text.strip()
    return text.isdigit() and 1 <= len(text) <= 3 and _top_ge(block, 500) and block.left >= 900 * _coord_scale(block)


def _looks_like_org_footer(block: TextBlock) -> bool:
    text = block.text.strip().lower()
    if any(keyword in text for keyword in ["university", "institute", "college", "school", "大学", "学院"]):
        return True
    return _top_ge(block, 500) and block.left <= 180 * _coord_scale(block) and len(text) >= 10


def _chapter_opener_confidence(blocks: list[TextBlock]) -> float:
    if not blocks:
        return 0.0
    non_footer = [block for block in blocks if not _is_footer(block) and not _is_header(block)]
    marker = next((block for block in non_footer if _is_chapter_marker(block)), None)
    if marker is None:
        return 0.0
    title = next((block for block in non_footer if block is not marker and _is_chapter_title(block, non_footer)), None)
    if title is None:
        return 0.0
    score = 0.55
    if len(non_footer) >= 3:
        score += 0.1
    if marker.left < title.left and abs(marker.top - title.top) <= 160 * _coord_scale(marker):
        score += 0.15
    if any(_looks_like_summary_line(block) for block in non_footer if block not in {marker, title}):
        score += 0.1
    if any(block.text.strip().startswith(("•", "-", "–")) for block in non_footer):
        score += 0.1
    return round(min(score, 1.0), 4)


def _looks_like_chapter_opener(blocks: list[TextBlock]) -> bool:
    return _chapter_opener_confidence(blocks) >= 0.75


def _is_chapter_marker(block: TextBlock) -> bool:
    text = block.text.strip()
    size = block.style.font_size_pt or 0.0
    return (
        1 <= len(text) <= 3
        and text.isdigit()
        and not _is_footer(block)
        and size >= 48
        and _top_gt(block, 120)
    )


def _is_chapter_title(block: TextBlock, blocks: list[TextBlock]) -> bool:
    if _is_chapter_marker(block) or _is_footer(block) or _is_header(block):
        return False
    text_len = len(block.text.strip().replace("\n", ""))
    size = block.style.font_size_pt or 0.0
    return 2 <= text_len <= 32 and size >= 24 and (block.style.bold or size >= 32)


def _looks_like_summary_line(block: TextBlock) -> bool:
    text = block.text.strip()
    size = block.style.font_size_pt or 0.0
    return 8 <= len(text.replace("\n", "")) <= 80 and 11 <= size <= 20


def _looks_like_toc_item_title(block: TextBlock, *, has_toc_context: bool = False) -> bool:
    text = block.text.strip().lower()
    if not text or not _is_main_body_band(block):
        return False
    if _looks_like_year(text):
        return False
    if _looks_like_two_digit_toc_number(text):
        return True
    if _looks_like_chinese_toc_number(text):
        return True
    return has_toc_context and _looks_like_single_digit_toc_number(text)


def _looks_like_uniform_toc_grid(blocks: list[TextBlock]) -> bool:
    if len(blocks) < 4:
        return False
    row_count = len(_cluster_positions([block.top for block in blocks]))
    col_count = len(_cluster_positions([block.left for block in blocks]))
    if row_count < 2 or col_count < 2:
        return False
    sizes = [block.style.font_size_pt for block in blocks if block.style.font_size_pt is not None]
    if sizes and max(sizes) - min(sizes) > 3:
        return False
    bold_values = {block.style.bold for block in blocks if block.style.bold is not None}
    return len(bold_values) <= 1


def _cluster_positions(values: list[int]) -> list[int]:
    if not values:
        return []
    sorted_values = sorted(values)
    tolerance = 100000 if max(sorted_values) > 10000 else 40
    clusters = [sorted_values[0]]
    for value in sorted_values[1:]:
        if abs(value - clusters[-1]) > tolerance:
            clusters.append(value)
    return clusters


def _looks_like_toc_title(block: TextBlock) -> bool:
    return _top_le(block, 140) and any(keyword in block.text.lower() for keyword in ["目录", "agenda", "contents", "目次", "大纲", "outline"])


def _looks_like_toc_item(block: TextBlock, *, has_toc_context: bool = False) -> bool:
    text = block.text.strip().lower()
    if not text or not _is_main_body_band(block) or _looks_like_toc_title(block):
        return False
    if _looks_like_toc_item_title(block, has_toc_context=has_toc_context):
        return True
    return has_toc_context and len(text.replace("\n", "")) <= 60 and (block.style.font_size_pt or 0) <= 16


def _tops_are_regular(blocks: list[TextBlock]) -> bool:
    if len(blocks) < 3:
        return False
    tops = sorted(block.top for block in blocks)
    gaps = [b - a for a, b in zip(tops, tops[1:])]
    return max(gaps) - min(gaps) <= 40 if gaps else False


def _is_dominant_text(block: TextBlock, blocks: list[TextBlock]) -> bool:
    size = block.style.font_size_pt or 0.0
    return size == max((item.style.font_size_pt or 0.0) for item in blocks)


def _is_top_or_large(block: TextBlock) -> bool:
    return _top_le(block, 160) or (block.style.font_size_pt or 0.0) >= 24


def _is_header(block: TextBlock) -> bool:
    return _top_le(block, 40) and (block.style.font_size_pt or 0.0) <= 14


def _is_footer(block: TextBlock) -> bool:
    return _top_ge(block, 500) and (block.style.font_size_pt or 0.0) <= 14


def _is_page_title(block: TextBlock, blocks: list[TextBlock]) -> bool:
    size = block.style.font_size_pt or 0.0
    return _top_le(block, 150) and (size >= 22 or _is_dominant_text(block, blocks))


def _looks_like_two_digit_toc_number(text: str) -> bool:
    if len(text) < 3:
        return False
    if not text[:2].isdigit():
        return False
    if text[0] not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
        return False
    return not text[2].isdigit()


def _looks_like_single_digit_toc_number(text: str) -> bool:
    return len(text) >= 3 and text[0].isdigit() and not text[1].isdigit() and text[1] in {".", "．", "、", ":", "：", " "}


def _looks_like_chinese_toc_number(text: str) -> bool:
    numerals = "一二三四五六七八九十"
    return (
        len(text) >= 2
        and (
            text[0] in numerals and text[1] in {"、", ".", "．", " ", "：", ":"}
            or text.startswith("第") and len(text) >= 3 and text[1] in numerals and text[2] in {"章", "节", "部分", "讲"}
        )
    )


def _looks_like_year(text: str) -> bool:
    return len(text) == 4 and text.isdigit() and 1900 <= int(text) <= 2099


def _is_main_body_band(block: TextBlock) -> bool:
    return _top_gt(block, 120) and not _is_footer(block) and not _is_header(block)


def _coord_scale(block: TextBlock) -> int:
    values = (block.left, block.top, block.width, block.height)
    return EMU_PER_PX if max((abs(value) for value in values), default=0) > 10000 else 1


def _top_le(block: TextBlock, px: int) -> bool:
    return block.top <= px * _coord_scale(block)


def _top_ge(block: TextBlock, px: int) -> bool:
    return block.top >= px * _coord_scale(block)


def _top_gt(block: TextBlock, px: int) -> bool:
    return block.top > px * _coord_scale(block)


def _resolve_scores(scores: dict[str, float]) -> tuple[str, float, float, bool]:
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_name, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = best_score - second_score
    total = sum(v for _, v in ranked)
    confidence = best_score / total if total > 0 else 0.0
    return best_name, round(confidence, 4), round(margin, 4), margin < 0.15


def classify_slide(slide_index: int, blocks: list[TextBlock], slide_count: int) -> SlideClassification:
    semantic = classify_slide_semantics(slide_index, blocks, slide_count)
    block_roles = {
        block_id: RoleMatch(
            role=slot.object_slot,
            confidence=slot.slot_confidence,
            margin=slot.slot_confidence,
            ambiguous=slot.skip_reason in {"role_low_confidence", "page_type_low_confidence"},
            signals=(slot.slot_variant,),
        )
        for block_id, slot in semantic.slot_resolutions.items()
    }
    return SlideClassification(
        page_type=semantic.page_type,
        confidence=semantic.page_type_confidence,
        margin=semantic.page_type_confidence,
        ambiguous=semantic.page_type_confidence < 0.45,
        signals=semantic.signals,
        block_roles=block_roles,
    )
