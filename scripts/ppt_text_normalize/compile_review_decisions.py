from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ppt_text_normalize.core.report_writer import write_json
from ppt_text_normalize.core.review_decisions import compile_reviewed_rules


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile visual review decisions into reviewed normalization rules.")
    parser.add_argument("--rules", required=True)
    parser.add_argument("--review-model", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rules_path = Path(args.rules).expanduser().resolve()
    model_path = Path(args.review_model).expanduser().resolve()
    decisions_path = Path(args.decisions).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    reviewed = compile_reviewed_rules(
        rules=json.loads(rules_path.read_text(encoding="utf-8")),
        review_model_payload=json.loads(model_path.read_text(encoding="utf-8")),
        review_decisions_payload=json.loads(decisions_path.read_text(encoding="utf-8")),
        source_rules_path=str(rules_path),
        review_model_path=str(model_path),
        review_decisions_path=str(decisions_path),
    )
    write_json(output_path, reviewed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
