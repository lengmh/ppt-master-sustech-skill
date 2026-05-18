#!/usr/bin/env python3
"""Update the repository and sync Python dependencies when needed.

Usage:
    python3 skills/ppt-master/scripts/update_repo.py
    python3 skills/ppt-master/scripts/update_repo.py --skip-pip
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TOOLS_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Pull the latest repository changes and sync Python dependencies "
            "only when requirements.txt changes."
        )
    )
    parser.add_argument(
        "--skip-pip",
        action="store_true",
        help="Skip Python dependency sync even if requirements.txt changed.",
    )
    return parser.parse_args()


def run_command(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_git_available() -> None:
    if shutil.which("git") is None:
        raise RuntimeError("Missing executable: git")


def ensure_clean_tracked_worktree() -> None:
    status = run_command(["git", "status", "--porcelain", "--untracked-files=no"], check=False)
    if status.returncode != 0:
        details = (status.stderr or status.stdout or "").strip()
        raise RuntimeError(details or "Unable to inspect git status.")

    if status.stdout.strip():
        raise RuntimeError(
            "Tracked local changes detected. Please commit or stash them before running the update command."
        )


def get_head_revision() -> str:
    result = run_command(["git", "rev-parse", "HEAD"])
    return result.stdout.strip()


def resolve_requirements_file() -> Path | None:
    skill_local = SKILL_DIR / "requirements.txt"
    repo_root = REPO_ROOT / "requirements.txt"
    if skill_local.exists():
        return skill_local
    if repo_root.exists():
        return repo_root
    return None


def sync_python_dependencies(requirements_file: Path | None) -> None:
    if requirements_file is None or not requirements_file.exists():
        print("requirements.txt not found; skipping Python dependency sync.")
        return

    print(f"requirements.txt changed. Syncing Python dependencies from: {requirements_file}")
    result = run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())


def main() -> int:
    args = parse_args()

    try:
        ensure_git_available()
        ensure_clean_tracked_worktree()

        requirements_file = resolve_requirements_file()
        before_head = get_head_revision()
        before_requirements = file_digest(requirements_file) if requirements_file else None

        print(f"Repository: {REPO_ROOT}")
        if requirements_file is not None:
            if requirements_file.parent == SKILL_DIR:
                print(f"Using skill-local requirements.txt: {requirements_file}")
            else:
                print(
                    "Skill-local requirements.txt not found. Falling back to repo-root requirements.txt: "
                    f"{requirements_file}"
                )
        pull_result = run_command(["git", "pull", "--ff-only"])
        if pull_result.stdout.strip():
            print(pull_result.stdout.strip())
        if pull_result.stderr.strip():
            print(pull_result.stderr.strip())

        after_head = get_head_revision()
        requirements_file_after = resolve_requirements_file()
        after_requirements = file_digest(requirements_file_after) if requirements_file_after else None

        if before_head == after_head:
            print("Repository is already up to date.")
        else:
            print(f"Updated from {before_head[:7]} to {after_head[:7]}.")

        if args.skip_pip:
            print("Skipped Python dependency sync (--skip-pip).")
        elif before_requirements != after_requirements:
            sync_python_dependencies(requirements_file_after)
        else:
            print("requirements.txt unchanged. Skipping Python dependency sync.")

        print("Note: system dependencies such as Node.js and Pandoc still need to be installed manually.")
        return 0
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        print(details or "Command failed.", file=sys.stderr)
        return exc.returncode or 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
