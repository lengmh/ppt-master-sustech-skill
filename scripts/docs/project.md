## `project_manager.py`

Project workspace bootstrapper for PPT Master.

```bash
python3 scripts/project_manager.py init demo_project --format ppt169
python3 scripts/project_manager.py import-sources projects/demo_project sources/input.md --move
```

Use this to create the standard project directory tree and archive source files into `sources/`.

## `pptx_template_import.py`

Unified PPTX preparation entry point for `/create-template`.

```bash
python3 scripts/pptx_template_import.py <template.pptx>
python3 scripts/pptx_template_import.py <template.pptx> -o <output_dir>
python3 scripts/pptx_template_import.py <template.pptx> --manifest-only
python3 scripts/pptx_template_import.py <template.pptx> --embed-images
python3 scripts/pptx_template_import.py <template.pptx> --inheritance-mode both
```

Outputs:
- `manifest.json` — factual metadata (theme, layouts, masters, assets, page-type candidates)
- `summary.md` — short human-readable digest derived from the manifest
- `assets/` — extracted reusable image assets
- `svg/` — layered machine-readable import view (`master_*.svg`, `layout_*.svg`, `slide_NN.svg`, `inheritance.json`)
- `svg-flat/` — self-contained per-slide preview view (when `--inheritance-mode both`)

Notes:
- Reads OOXML directly via `pptx_to_svg`; no PowerPoint COM / `Slide.Export` path remains in the main import flow
- `--inheritance-mode both` is the default and is recommended for template derivation
- `--manifest-only` skips SVG generation and writes only metadata + assets
- Intended for template reference preparation, not for final 1:1 PPT delivery

## `template_quality_checker.py`

Template-level self-check for `/create-template` outputs.

```bash
python3 scripts/template_quality_checker.py templates/layouts/sustech_academic_official --format ppt169
```

Checks:
- `brief_lock.json` exists and is parseable
- `design_spec.md` follows the merged personality-only template skeleton
- locked identity / category / canvas / replication fields do not drift from `brief_lock.json`
- SVG roster, placeholder, and asset references are consistent
- raw SVG technical checks still pass through `svg_quality_checker.py --template-mode`
- `register_template.py --dry-run` succeeds as a preflight

## `template_preview.py`

Export a timestamped template preview workspace for the registration-preflight feedback gate.

```bash
python3 scripts/template_preview.py templates/layouts/sustech_academic_official
python3 scripts/template_preview.py templates/layouts/sustech_academic_official --output-root /tmp
```

Outputs:
- `<preview_workspace>/svg_output/` — copied raw template SVGs
- `<preview_workspace>/svg_final/` — post-processed preview files generated via `finalize_svg.py`

Use this before registration so the user can review the rendered template effect and decide whether feedback is implementation-level or brief-level.

## `register_template.py`

Global template registrar for `templates/layouts/`.

```bash
python3 scripts/register_template.py sustech_academic_official
python3 scripts/register_template.py sustech_academic_official --dry-run
python3 scripts/register_template.py --rebuild-all
```

Outputs:
- updates `templates/layouts/layouts_index.json`
- refreshes the auto-managed Quick Index block inside `templates/layouts/README.md`
- prints a completion card with the current SVG roster

## `package_release.py`

Build the versioned SUSTech custom skill release zip.

```bash
python3 scripts/package_release.py
python3 scripts/package_release.py --output /home/sustech/playground/ppt-master-skill.zip
python3 scripts/package_release.py --keep-temp
python3 scripts/package_release.py --temp-root /home/sustech/TempFiles
python3 scripts/package_release.py --allow-upstream-support-fallback
python3 scripts/package_release.py --env-example-file .env.example --requirements-file requirements.txt
```

Behavior:
- reads local release metadata from `VERSION` + `RELEASE_META.json`
- stages a clean `ppt-master/` directory in a temporary workspace
- copies local skill content from `SKILL.md`, `VERSION`, `RELEASE_META.json`, `.env.example`, `requirements.txt`, `references/`, `scripts/`, `templates/`, and `workflows/`
- defaults to **strict-local** support files: missing local `.env.example` or `requirements.txt` is an error
- only downloads upstream support files when `--allow-upstream-support-fallback` is explicitly provided (or when explicit override paths are supplied)
- defaults the output zip filename to `ppt-master-sustech-r<upstream>-v<local>-YYYY-MM-DD.zip`
- keeps the zip-internal root directory stable as `ppt-master/`
- excludes local packaging noise such as `.git/`, venvs, `plan/`, `__pycache__/`, `.pyc`, `.gitignore`, and `.synced_hash`
- `--temp-root` controls the parent directory for per-run staging workspaces; the script removes the generated staging subdirectory after a successful run unless `--keep-temp` is set
- validates the final zip before reporting success, including `VERSION`, `RELEASE_META.json`, `.env.example`, and `requirements.txt`

## `error_helper.py`

Show standardized fixes for common project errors.

```bash
python3 scripts/error_helper.py
python3 scripts/error_helper.py missing_readme
python3 scripts/error_helper.py missing_readme project_path=my_project
```
