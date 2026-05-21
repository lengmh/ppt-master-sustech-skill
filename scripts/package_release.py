#!/usr/bin/env python3
"""Build a versioned SUSTech custom ppt-master skill release zip.

Usage:
    python3 scripts/package_release.py
    python3 scripts/package_release.py --output /path/to/ppt-master-skill.zip
    python3 scripts/package_release.py --keep-temp
    python3 scripts/package_release.py --env-example-file .env.example --requirements-file requirements.txt
    python3 scripts/package_release.py --allow-upstream-support-fallback

The release layout intentionally mirrors the upstream ``skills/ppt-master/``
subtree shape while using local release metadata and support files by default:

- ``ppt-master/.gitignore``
- ``ppt-master/README.md``
- ``ppt-master/LICENSE``
- ``ppt-master/THIRD_PARTY_NOTICES.md``
- ``ppt-master/SKILL.md``
- ``ppt-master/VERSION``
- ``ppt-master/RELEASE_META.json``
- ``ppt-master/.env.example``
- ``ppt-master/requirements.txt``
- ``ppt-master/docs/README.md``
- ``ppt-master/docs/THIRD_PARTY_NOTICES.md``
- ``ppt-master/references/``
- ``ppt-master/scripts/``
- ``ppt-master/templates/``
- ``ppt-master/workflows/``

Top-level local-only development noise (for example ``.git/``, venvs, tracked
plan docs, ``__pycache__/``, and bytecode files) is excluded automatically.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

DEFAULT_PACKAGE_DIRNAME = "ppt-master"
DEFAULT_UPSTREAM_OWNER = "hugohe3"
DEFAULT_UPSTREAM_REPO = "ppt-master"
DEFAULT_UPSTREAM_REF = "main"

LOCAL_RELEASE_ITEMS = (
    ".gitignore",
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "SKILL.md",
    "VERSION",
    "RELEASE_META.json",
    "docs/README.md",
    "docs/THIRD_PARTY_NOTICES.md",
    "references",
    "scripts",
    "templates",
    "workflows",
)
LOCAL_SUPPORT_FILES = (
    ".env.example",
    "requirements.txt",
)

VERSION_PATTERN = re.compile(
    r"^r(?P<upstream>\d+\.\d+\.\d+)-v(?P<local>\d+\.\d+\.\d+)$"
)

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    ".venv-flask-check",
    ".venv-svg-editor",
    "__pycache__",
    "plan",
}
EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    ".synced_hash",
    "Thumbs.db",
}
EXCLUDED_SUFFIXES = {
    ".log",
    ".pyc",
    ".temp",
    ".tmp",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a versioned SUSTech custom release zip for the local "
            "ppt-master skill."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output zip path (default: current directory with a "
            "version-aware date-stamped filename)."
        ),
    )
    parser.add_argument(
        "--package-dirname",
        default=DEFAULT_PACKAGE_DIRNAME,
        help=f"Top-level directory name inside the zip (default: {DEFAULT_PACKAGE_DIRNAME}).",
    )
    parser.add_argument(
        "--temp-root",
        type=Path,
        default=None,
        help=(
            "Workspace parent directory used while staging files "
            "(default: auto-detect). The script removes only the per-run "
            "staging subdirectory, not this parent directory itself."
        ),
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary staging workspace after the zip is built.",
    )
    parser.add_argument(
        "--upstream-owner",
        default=DEFAULT_UPSTREAM_OWNER,
        help=f"GitHub owner for upstream skill metadata fetch (default: {DEFAULT_UPSTREAM_OWNER}).",
    )
    parser.add_argument(
        "--upstream-repo",
        default=DEFAULT_UPSTREAM_REPO,
        help=f"GitHub repo for upstream skill metadata fetch (default: {DEFAULT_UPSTREAM_REPO}).",
    )
    parser.add_argument(
        "--upstream-ref",
        default=DEFAULT_UPSTREAM_REF,
        help=f"Git ref/tag/branch for upstream skill metadata fetch (default: {DEFAULT_UPSTREAM_REF}).",
    )
    parser.add_argument(
        "--env-example-file",
        type=Path,
        default=None,
        help="Local .env.example source. If omitted, fetch from upstream.",
    )
    parser.add_argument(
        "--requirements-file",
        type=Path,
        default=None,
        help="Override source for requirements.txt (default: local skill root file).",
    )
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=120,
        help="Network timeout in seconds for upstream support-file downloads (default: 120).",
    )
    parser.add_argument(
        "--allow-upstream-support-fallback",
        action="store_true",
        help=(
            "Allow downloading support files from upstream when local "
            "requirements.txt or .env.example is missing."
        ),
    )
    return parser.parse_args()


def detect_temp_root() -> Path:
    import os

    env_value = os.environ.get("PPT_MASTER_TEMP_ROOT")
    if env_value:
        return Path(env_value)

    preferred_roots = [
        Path("/home/sustech/TempFiles"),
        Path(r"F:\AI playground\TempFiles"),
    ]
    for candidate in preferred_roots:
        if candidate.exists():
            return candidate

    return Path(tempfile.gettempdir()) / "ppt-master"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def build_upstream_raw_url(owner: str, repo: str, ref: str, filename: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/"
        f"skills/ppt-master/{filename}"
    )


def download_file_via_curl(url: str, destination: Path, *, timeout: int) -> bool:
    if shutil.which("curl") is None:
        return False
    ensure_parent(destination)
    try:
        subprocess.run(
            [
                "curl",
                "-L",
                "--fail",
                "--silent",
                "--show-error",
                "--max-time",
                str(timeout),
                "-o",
                str(destination),
                url,
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return True
    except subprocess.CalledProcessError:
        return False


def download_file(url: str, destination: Path, *, timeout: int) -> None:
    if download_file_via_curl(url, destination, timeout=timeout):
        return

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ppt-master-package-release/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc

    ensure_parent(destination)
    destination.write_bytes(payload)


def load_version_file() -> str:
    version_path = SKILL_DIR / "VERSION"
    if not version_path.exists():
        raise RuntimeError(f"Missing VERSION file: {version_path}")
    value = version_path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError("VERSION file is empty.")
    return value


def load_release_meta() -> dict:
    meta_path = SKILL_DIR / "RELEASE_META.json"
    if not meta_path.exists():
        raise RuntimeError(f"Missing RELEASE_META.json file: {meta_path}")
    try:
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid RELEASE_META.json: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("RELEASE_META.json root must be an object.")
    return payload


def validate_release_metadata(meta: dict, version_text: str) -> tuple[str, str]:
    match = VERSION_PATTERN.fullmatch(version_text)
    if not match:
        raise RuntimeError(
            "VERSION must match `r<upstream-version>-v<local-version>` "
            f"(got: {version_text!r})."
        )

    release_version = meta.get("release_version")
    if release_version != version_text:
        raise RuntimeError(
            "RELEASE_META.json release_version does not match VERSION "
            f"({release_version!r} != {version_text!r})."
        )

    upstream = meta.get("upstream")
    local = meta.get("local")
    package = meta.get("package")
    support_files = meta.get("support_files")
    if not isinstance(upstream, dict):
        raise RuntimeError("RELEASE_META.json missing `upstream` object.")
    if not isinstance(local, dict):
        raise RuntimeError("RELEASE_META.json missing `local` object.")
    if not isinstance(package, dict):
        raise RuntimeError("RELEASE_META.json missing `package` object.")
    if not isinstance(support_files, dict):
        raise RuntimeError("RELEASE_META.json missing `support_files` object.")

    upstream_version = upstream.get("version")
    local_version = local.get("version")
    if upstream_version != match.group("upstream"):
        raise RuntimeError(
            "RELEASE_META.json upstream.version does not match VERSION "
            f"({upstream_version!r} != {match.group('upstream')!r})."
        )
    if local_version != match.group("local"):
        raise RuntimeError(
            "RELEASE_META.json local.version does not match VERSION "
            f"({local_version!r} != {match.group('local')!r})."
        )
    if package.get("root_dirname") != DEFAULT_PACKAGE_DIRNAME:
        raise RuntimeError(
            "RELEASE_META.json package.root_dirname must be "
            f"{DEFAULT_PACKAGE_DIRNAME!r}."
        )
    return str(upstream_version), str(local_version)


def default_output_path(release_version: str) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    return Path.cwd() / f"ppt-master-sustech-{release_version}-{today}.zip"


def copy_local_item(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            ignore=ignore_copytree_entries,
        )
        return

    ensure_parent(destination)
    shutil.copy2(source, destination)


def ignore_copytree_entries(_dirpath: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in EXCLUDED_DIR_NAMES or name in EXCLUDED_FILE_NAMES:
            ignored.add(name)
            continue
        if Path(name).suffix.lower() in EXCLUDED_SUFFIXES:
            ignored.add(name)
    return ignored


def stage_local_release_tree(package_root: Path) -> None:
    for item in LOCAL_RELEASE_ITEMS:
        source = SKILL_DIR / item
        if not source.exists():
            raise RuntimeError(f"Missing required local release item: {source}")
        copy_local_item(source, package_root / item)


def stage_upstream_support_files(
    package_root: Path,
    *,
    env_example_file: Path | None,
    requirements_file: Path | None,
    upstream_owner: str,
    upstream_repo: str,
    upstream_ref: str,
    download_timeout: int,
    allow_upstream_support_fallback: bool,
) -> None:
    env_target = package_root / ".env.example"
    req_target = package_root / "requirements.txt"
    env_local = SKILL_DIR / ".env.example"
    req_local = SKILL_DIR / "requirements.txt"

    if env_example_file is not None:
        if not env_example_file.exists():
            raise RuntimeError(f"Missing local .env.example source: {env_example_file}")
        shutil.copy2(env_example_file, env_target)
    elif env_local.exists():
        shutil.copy2(env_local, env_target)
    elif not allow_upstream_support_fallback:
        raise RuntimeError(
            "Missing local .env.example. Strict-local release packaging is the "
            "default; pass --allow-upstream-support-fallback to download it "
            "from upstream explicitly."
        )
    else:
        download_file(
            build_upstream_raw_url(
                upstream_owner, upstream_repo, upstream_ref, ".env.example"
            ),
            env_target,
            timeout=download_timeout,
        )

    if requirements_file is not None:
        if not requirements_file.exists():
            raise RuntimeError(
                f"Missing local requirements.txt source: {requirements_file}"
            )
        shutil.copy2(requirements_file, req_target)
    elif req_local.exists():
        shutil.copy2(req_local, req_target)
    elif not allow_upstream_support_fallback:
        raise RuntimeError(
            "Missing local requirements.txt. Strict-local release packaging is "
            "the default; pass --allow-upstream-support-fallback to download "
            "it from upstream explicitly."
        )
    else:
        download_file(
            build_upstream_raw_url(
                upstream_owner, upstream_repo, upstream_ref, "requirements.txt"
            ),
            req_target,
            timeout=download_timeout,
        )


def build_zip(staging_root: Path, output_path: Path) -> int:
    ensure_parent(output_path)
    if output_path.exists():
        output_path.unlink()

    file_count = 0
    with zipfile.ZipFile(
        output_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(staging_root.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(staging_root)
            archive.write(path, rel.as_posix())
            file_count += 1
    return file_count


def verify_release_zip(zip_path: Path, package_dirname: str) -> None:
    required_entries = [
        f"{package_dirname}/.gitignore",
        f"{package_dirname}/README.md",
        f"{package_dirname}/LICENSE",
        f"{package_dirname}/THIRD_PARTY_NOTICES.md",
        f"{package_dirname}/SKILL.md",
        f"{package_dirname}/VERSION",
        f"{package_dirname}/RELEASE_META.json",
        f"{package_dirname}/.env.example",
        f"{package_dirname}/requirements.txt",
        f"{package_dirname}/docs/README.md",
        f"{package_dirname}/docs/THIRD_PARTY_NOTICES.md",
        f"{package_dirname}/references/",
        f"{package_dirname}/scripts/",
        f"{package_dirname}/templates/",
        f"{package_dirname}/workflows/",
    ]
    forbidden_entries = [
        f"{package_dirname}/.synced_hash",
        f"{package_dirname}/docs/adr/",
        f"{package_dirname}/docs/plan/",
        f"{package_dirname}/docs/superpowers/",
        f"{package_dirname}/plan/",
        f"{package_dirname}/.git/",
        f"{package_dirname}/.venv/",
        f"{package_dirname}/.venv-flask-check/",
        f"{package_dirname}/.venv-svg-editor/",
    ]

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()

    missing: list[str] = []
    for entry in required_entries:
        if entry.endswith("/"):
            if not any(name.startswith(entry) for name in names):
                missing.append(entry)
        elif entry not in names:
            missing.append(entry)

    present_forbidden: list[str] = []
    for entry in forbidden_entries:
        if entry.endswith("/"):
            if any(name.startswith(entry) for name in names):
                present_forbidden.append(entry)
        elif entry in names:
            present_forbidden.append(entry)

    if missing or present_forbidden:
        parts: list[str] = []
        if missing:
            parts.append("Missing required entries: " + ", ".join(missing))
        if present_forbidden:
            parts.append("Forbidden entries present: " + ", ".join(present_forbidden))
        raise RuntimeError("Zip verification failed. " + " | ".join(parts))


def format_size(path: Path) -> str:
    size = path.stat().st_size
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def main() -> int:
    args = parse_args()
    version_text = load_version_file()
    meta = load_release_meta()
    upstream_version, local_version = validate_release_metadata(meta, version_text)
    output_path = args.output or default_output_path(version_text)

    temp_root = args.temp_root or detect_temp_root()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    staging_root = temp_root / f"ppt-master-release-{stamp}"
    package_root = staging_root / args.package_dirname

    try:
        if staging_root.exists():
            shutil.rmtree(staging_root)
        package_root.mkdir(parents=True, exist_ok=False)

        stage_local_release_tree(package_root)
        stage_upstream_support_files(
            package_root,
            env_example_file=args.env_example_file,
            requirements_file=args.requirements_file,
            upstream_owner=args.upstream_owner,
            upstream_repo=args.upstream_repo,
            upstream_ref=args.upstream_ref,
            download_timeout=args.download_timeout,
            allow_upstream_support_fallback=args.allow_upstream_support_fallback,
        )

        file_count = build_zip(staging_root, output_path)
        verify_release_zip(output_path, args.package_dirname)

        print(f"[OK] Release zip created: {output_path}")
        print(f"[OK] Release version: {version_text}")
        print(
            f"[OK] Upstream baseline: {upstream_version} "
            f"({meta['upstream'].get('tag', 'no-tag')})"
        )
        print(f"[OK] Local version: {local_version}")
        print(f"[OK] Files packed: {file_count}")
        print(f"[OK] Zip size: {format_size(output_path)}")
        print(f"[OK] Package root inside zip: {args.package_dirname}/")
        print(
            "[OK] Support files: "
            f"{meta['support_files'].get('requirements_source', 'unknown')} "
            "requirements.txt, "
            f"{meta['support_files'].get('env_example_source', 'unknown')} "
            ".env.example"
        )
        if args.keep_temp:
            print(f"[OK] Temp workspace kept: {staging_root}")
        else:
            shutil.rmtree(staging_root)
            print(f"[OK] Temp staging workspace removed: {staging_root}")
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
