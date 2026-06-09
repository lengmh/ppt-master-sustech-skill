from __future__ import annotations

import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ppt_text_normalize.core.review_workspace import build_review_workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a visual review workspace for ppt_text_normalize.")
    parser.add_argument("input_pptx")
    parser.add_argument("--scan-dir", required=True)
    parser.add_argument("--workdir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_review_workspace(Path(args.input_pptx), Path(args.scan_dir), Path(args.workdir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
