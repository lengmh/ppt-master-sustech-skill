from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from ppt_text_normalize import scan


def _empty_pptx(path: Path) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "ppt/presentation.xml",
            '<p:presentation xmlns:p="http://schemas.openxmlformats.org/'
            'presentationml/2006/main"><p:sldIdLst/></p:presentation>',
        )
    return path


def test_default_workdir_uses_system_temp(tmp_path):
    input_pptx = _empty_pptx(tmp_path / "input.pptx")
    system_temp = tmp_path / "system-temp"

    with patch.object(scan.tempfile, "gettempdir", return_value=str(system_temp)):
        assert scan.main([str(input_pptx), "--task", "example-task"]) == 0

    workdir = system_temp / "ppt_text_normalize" / "example-task"
    for name in ("rules.json", "scan_report.json", "scan_report.md"):
        assert (workdir / name).is_file()


def test_explicit_workdir_overrides_system_temp(tmp_path):
    input_pptx = _empty_pptx(tmp_path / "input.pptx")
    workdir = tmp_path / "custom-workspace"

    with patch.object(scan.tempfile, "gettempdir", side_effect=AssertionError("unused")):
        assert scan.main([
            str(input_pptx), "--task", "example-task", "--workdir", str(workdir)
        ]) == 0

    assert (workdir / "rules.json").is_file()
