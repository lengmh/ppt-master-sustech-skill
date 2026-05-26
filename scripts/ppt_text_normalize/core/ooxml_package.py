from __future__ import annotations

import posixpath
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
    "p15": "http://schemas.microsoft.com/office/powerpoint/2012/main",
    "p16": "http://schemas.microsoft.com/office/powerpoint/2016/main",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
    "a16": "http://schemas.microsoft.com/office/drawing/2014/main",
}

PRESERVED_PREFIXES = {
    "a": NS["a"],
    "p": NS["p"],
    "r": NS["r"],
    "mc": NS["mc"],
    "p14": NS["p14"],
    "p15": NS["p15"],
    "p16": NS["p16"],
    "a14": NS["a14"],
    "a16": NS["a16"],
}


def serialize_xml_preserving_prefixes(root: ET.Element) -> bytes:
    """Serialize OOXML without breaking PowerPoint markup-compatibility prefixes.

    PowerPoint slides may contain `mc:AlternateContent` with values such as
    `Requires="p14"`. ElementTree's default serializer can rewrite the actual
    p14 namespace prefix to `ns4` while leaving the attribute value as `p14`,
    which makes PowerPoint repair the deck and potentially delete content.
    All slide XML write-back must go through this helper instead of raw
    `ET.tostring(...)`.
    """
    for prefix, uri in PRESERVED_PREFIXES.items():
        ET.register_namespace(prefix, uri)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def validate_markup_compatibility_prefixes(pptx_path: Path) -> list[str]:
    """Return OOXML markup-compatibility namespace errors for generated PPTX files."""
    errors: list[str] = []
    with zipfile.ZipFile(pptx_path, "r") as zf:
        for name in zf.namelist():
            if not (name.startswith("ppt/slides/slide") and name.endswith(".xml")):
                continue
            xml = zf.read(name).decode("utf-8", errors="replace")
            for requires_value in re.findall(r'Requires="([^"]+)"', xml):
                for prefix in requires_value.split():
                    if prefix in PRESERVED_PREFIXES and f"xmlns:{prefix}=" not in xml:
                        errors.append(f"{name}: Requires=\"{prefix}\" without xmlns:{prefix}")
            if "xmlns:ns" in xml:
                errors.append(f"{name}: unstable ElementTree ns* prefix leaked")
    return errors

SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
LAYOUT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
MASTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"
PRESENTATION_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
PACKAGE_REL = "_rels/.rels"


def _normalize_part_path(target: str, base: str | None = None) -> str:
    target = target.replace("\\", "/")
    if target.startswith("/"):
        return target.lstrip("/")
    if base is None:
        return target
    base_dir = posixpath.dirname(base.rstrip("/"))
    joined = posixpath.normpath(posixpath.join(base_dir, target))
    return joined.lstrip("/")


def _rels_path_for(part_path: str) -> str:
    parent, name = posixpath.split(part_path)
    if not parent:
        return f"_rels/{name}.rels"
    return f"{parent}/_rels/{name}.rels"


def _parse_rels(zf: zipfile.ZipFile, rels_path: str) -> dict[str, dict[str, str]]:
    if rels_path not in zf.namelist():
        return {}
    try:
        root = ET.fromstring(zf.read(rels_path))
    except ET.ParseError:
        return {}
    base = rels_path.replace("/_rels/", "/")
    if base.endswith(".rels"):
        base = base[:-5]
    rels: dict[str, dict[str, str]] = {}
    for child in root.findall(f"{{{NS['rel']}}}Relationship"):
        rid = child.attrib.get("Id", "")
        rtype = child.attrib.get("Type", "")
        target = child.attrib.get("Target", "")
        target_mode = child.attrib.get("TargetMode", "")
        if target_mode == "External":
            rels[rid] = {"type": rtype, "target": target, "external": "1"}
            continue
        rels[rid] = {"type": rtype, "target": _normalize_part_path(target, base)}
    return rels


def _load_xml(zf: zipfile.ZipFile, part_path: str) -> ET.Element | None:
    if part_path not in zf.namelist():
        return None
    try:
        return ET.fromstring(zf.read(part_path))
    except ET.ParseError:
        return None


@dataclass
class PartRef:
    path: str
    xml: ET.Element
    rels: dict[str, dict[str, str]] = field(default_factory=dict)

    def resolve_rel(self, rid: str) -> str | None:
        info = self.rels.get(rid)
        if info is None or info.get("external"):
            return None
        return info.get("target")


@dataclass
class SlideRef:
    index: int
    part: PartRef
    layout: PartRef | None
    master: PartRef | None


class OoxmlPackage:
    def __init__(self, pptx_path: Path) -> None:
        self.path = Path(pptx_path)
        self.zip: zipfile.ZipFile | None = None
        self.presentation: PartRef | None = None
        self.slide_size_emu: tuple[int, int] = (0, 0)
        self._slides: list[SlideRef] = []
        self._part_cache: dict[str, PartRef] = {}

    def __enter__(self) -> "OoxmlPackage":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        if self.zip is not None:
            return
        self.zip = zipfile.ZipFile(self.path, "r")
        self._load_presentation()
        self._load_slides()

    def close(self) -> None:
        if self.zip is not None:
            self.zip.close()
            self.zip = None

    def iter_slides(self) -> Iterator[SlideRef]:
        yield from self._slides

    def save_as(self, output_path: Path, xml_overrides: dict[str, bytes]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        assert self.zip is not None
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as out:
            for name in self.zip.namelist():
                payload = xml_overrides.get(name)
                if payload is None:
                    payload = self.zip.read(name)
                out.writestr(name, payload)

    def _load_part(self, part_path: str) -> PartRef | None:
        cached = self._part_cache.get(part_path)
        if cached is not None:
            return cached
        assert self.zip is not None
        xml = _load_xml(self.zip, part_path)
        if xml is None:
            return None
        rels = _parse_rels(self.zip, _rels_path_for(part_path))
        part = PartRef(path=part_path, xml=xml, rels=rels)
        self._part_cache[part_path] = part
        return part

    def _load_presentation(self) -> None:
        assert self.zip is not None
        package_rels = _parse_rels(self.zip, PACKAGE_REL)
        pres_path = None
        for info in package_rels.values():
            if info.get("type") == PRESENTATION_REL:
                pres_path = info["target"]
                break
        if pres_path is None:
            pres_path = "ppt/presentation.xml"
        self.presentation = self._load_part(pres_path)
        if self.presentation is None:
            raise RuntimeError(f"presentation.xml missing in {self.path}")
        size = self.presentation.xml.find("p:sldSz", NS)
        if size is not None:
            self.slide_size_emu = (
                int(size.attrib.get("cx", "0") or 0),
                int(size.attrib.get("cy", "0") or 0),
            )

    def _load_slides(self) -> None:
        assert self.presentation is not None
        slides: list[SlideRef] = []
        for idx, sld in enumerate(self.presentation.xml.findall("p:sldIdLst/p:sldId", NS), start=1):
            rid = sld.attrib.get(f"{{{NS['r']}}}id")
            if not rid:
                continue
            slide_path = self.presentation.resolve_rel(rid)
            if not slide_path:
                continue
            slide_part = self._load_part(slide_path)
            if slide_part is None:
                continue
            layout_path = next((rel["target"] for rel in slide_part.rels.values() if rel.get("type") == LAYOUT_REL), None)
            layout_part = self._load_part(layout_path) if layout_path else None
            master_path = None
            if layout_part is not None:
                master_path = next((rel["target"] for rel in layout_part.rels.values() if rel.get("type") == MASTER_REL), None)
            master_part = self._load_part(master_path) if master_path else None
            slides.append(SlideRef(index=idx, part=slide_part, layout=layout_part, master=master_part))
        self._slides = slides
