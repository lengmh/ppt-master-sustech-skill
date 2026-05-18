# PPT Master SUSTech-Enhanced Version

This repository contains the SUSTech-enhanced public release source for `ppt-master`, used to turn PDF, DOCX, PPTX, web pages, Markdown, Excel workbooks, and similar inputs into high-quality, editable PPTX presentations.  
This enhanced line preserves the full workflow across content understanding, design-spec generation, SVG page construction, post-processing, and PPTX export, and is intended for agent-capable environments such as Claude Code, Cursor, and Codex.

## Key Features

- Supports multiple input types including PDF, Word, PPTX, web pages, Markdown, and Excel
- Uses `design_spec.md` and `spec_lock.md` to drive both design intent and execution constraints
- Exports editable PPTX decks instead of image-only slide output
- Supports template reuse, template creation, template validation, and template preview
- Includes image acquisition, AI image generation, chart verification, speaker notes, and post-processing workflows
- Includes a versioned, reproducible local release contract for packaging and distribution

## Release Identity

- **Release Version**: `r2.7.0-v0.1.0`
- **Upstream Baseline**: `hugohe3/ppt-master@v2.7.0`
- **Package Root Dir**: `ppt-master/`

## What this repository contains

This is a cleaned public release-source snapshot for the SUSTech-enhanced skill line. It includes:

- `SKILL.md`
- `VERSION`
- `RELEASE_META.json`
- `.env.example`
- `requirements.txt`
- `references/`
- `scripts/`
- `templates/`
- `workflows/`

## What this repository does not contain

This repository does **not** include local runtime outputs, temporary planning files, private environment files, or local workspace metadata.

Examples of excluded content:

- `.env`
- `.synced_hash`
- `projects/`
- `tmp/`
- `cache/`
- `docs/plan/`
- local virtual environments

## License

This repository follows the upstream MIT License. See the root [LICENSE](../LICENSE).

## Third-party notices

Some bundled or referenced icons, brand marks, sourced images, and template assets may still carry their own upstream license or attribution requirements. See [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md).

## Notes

This public-facing source tree is intended to track release-quality content for the SUSTech-enhanced line, not private day-to-day planning or local runtime state.
