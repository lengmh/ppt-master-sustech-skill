from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

PageType = Literal["cover", "chapter", "toc", "content", "ending", "hero", "unknown"]
PageSubmode = Literal[
    "cover@standard",
    "cover@hero_like",
    "toc@uniform_list",
    "toc@uniform_grid",
    "toc@freeform_composition",
    "chapter@uniform_series",
    "chapter@freeform_hero",
    "content@standard",
    "content@hero_mixed",
    "ending@standard",
    "ending@hero_like",
    "unknown@default",
]
TextRole = Literal["title", "subtitle", "body", "caption", "table_text", "unknown"]
ObjectSlot = Literal[
    "page_title",
    "section_title",
    "header",
    "footer",
    "toc_title",
    "toc_item",
    "chapter_title",
    "chapter_marker",
    "content_body",
    "content_label",
    "content_emphasis",
    "content_caption",
    "content_stat",
    "table_text",
    "hero",
    "unknown",
]
MutationPermissionProfile = Literal[
    "frozen",
    "typography_only",
    "conservative_text",
    "slot_standard",
    "list_standard",
    "series_standard",
    "preserve_emphasis",
]
ContainerType = Literal["textbox", "placeholder", "table_cell"]
RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class StyleFingerprint:
    font_family: str | None = None
    east_asia_font_family: str | None = None
    color: str | None = None
    font_size_pt: float | None = None
    bold: bool | None = None
    italic: bool | None = None
    source_level: str | None = None


@dataclass(frozen=True)
class TextRunStyle:
    font_family: str | None = None
    east_asia_font: str | None = None
    color: str | None = None
    font_size_pt: float | None = None
    bold: bool | None = None
    italic: bool | None = None


@dataclass(frozen=True)
class TextBlock:
    block_id: str
    slide_index: int
    container_type: ContainerType
    text: str
    shape_name: str | None = None
    placeholder_type: str | None = None
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0
    paragraphs: int = 0
    paragraph_count: int = 0
    run_count: int = 0
    source_level: str | None = None
    style: StyleFingerprint = field(default_factory=StyleFingerprint)
    runs: tuple[TextRunStyle, ...] = ()
    unsupported_reason: str | None = None


@dataclass(frozen=True)
class HeroDecision:
    is_frozen: bool
    page_confidence: float = 0.0
    slot_confidence: float = 0.0
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObjectSlotResolution:
    object_slot: ObjectSlot
    slot_confidence: float
    slot_variant: str
    slot_variant_confidence: float
    content_intent_role: str | None
    uniformity_eligible: bool
    mutation_permission_profile: MutationPermissionProfile
    hero_slot_confidence: float = 0.0
    skip_reason: str | None = None


@dataclass(frozen=True)
class SlideSemanticResolution:
    page_type: PageType
    page_type_confidence: float
    page_submode: str
    page_submode_confidence: float
    hero_decision: HeroDecision
    slot_resolutions: dict[str, ObjectSlotResolution]
    signals: tuple[str, ...] = ()


def allowed_style_fields(profile: str, object_slot: str) -> tuple[str, ...]:
    if profile == "frozen":
        return ()
    if profile == "preserve_emphasis":
        return ("font_family",)
    if profile == "typography_only":
        return ("font_family", "bold")
    if profile == "conservative_text":
        return ("font_family",)
    if profile in {"list_standard", "series_standard"}:
        return ("font_family", "bold")
    if profile == "slot_standard":
        if object_slot in {"page_title", "header"}:
            return ("font_family", "bold", "color")
        if object_slot == "toc_title":
            return ("font_family", "bold")
        if object_slot == "footer":
            return ("font_family", "color")
        return ("font_family", "bold")
    return ("font_family",)


@dataclass(frozen=True)
class CanonicalStyle:
    page_type: PageType
    object_slot: ObjectSlot
    slot_variant: str
    permission_profile: MutationPermissionProfile
    source: str
    sample_count: int
    core_cluster_ratio: float
    style: StyleFingerprint
    weak_canonical: bool = False


@dataclass(frozen=True)
class LayoutRiskAssessment:
    level: RiskLevel
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoleMatch:
    role: str
    confidence: float
    margin: float
    ambiguous: bool
    signals: tuple[str, ...] = ()


@dataclass(frozen=True)
class SlideClassification:
    page_type: str
    confidence: float
    margin: float
    ambiguous: bool
    signals: tuple[str, ...]
    block_roles: dict[str, RoleMatch]
