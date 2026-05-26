from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from ppt_text_normalize.core.ooxml_package import (
    serialize_xml_preserving_prefixes,
    validate_markup_compatibility_prefixes,
)


class TestOoxmlNamespacePreservation(unittest.TestCase):
    def test_serialize_preserves_mc_requires_prefix_declaration(self) -> None:
        xml = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld/>
  <mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
    <mc:Choice xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" Requires="p14">
      <p:transition p14:dur="400"><p:fade/></p:transition>
    </mc:Choice>
    <mc:Fallback><p:transition><p:fade/></p:transition></mc:Fallback>
  </mc:AlternateContent>
</p:sld>'''
        root = ET.fromstring(xml)

        out = serialize_xml_preserving_prefixes(root)

        self.assertIn(b'xmlns:p14=', out)
        self.assertIn(b'xmlns:mc=', out)
        self.assertIn(b'Requires="p14"', out)
        self.assertNotIn(b'xmlns:ns', out)
        self.assertIn(b'<mc:AlternateContent', out)
        self.assertIn(b'p14:dur="400"', out)

    def test_validate_flags_missing_requires_namespace(self) -> None:
        broken_slide = b'''<?xml version="1.0" encoding="utf-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
    <mc:Choice Requires="p14"><p:transition /></mc:Choice>
  </mc:AlternateContent>
</p:sld>'''
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = Path(tmp) / 'broken.pptx'
            with zipfile.ZipFile(pptx_path, 'w') as zf:
                zf.writestr('ppt/slides/slide1.xml', broken_slide)

            errors = validate_markup_compatibility_prefixes(pptx_path)

        self.assertTrue(errors)
        self.assertIn('Requires="p14" without xmlns:p14', errors[0])


if __name__ == '__main__':
    unittest.main()
