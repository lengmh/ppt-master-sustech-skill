# Legacy Template Brief Lock Compatibility

## Status

New `/create-template` workspaces do not use this reference. Their required
brief proposal and confirmation gate live only in
[`workflows/create-template.md`](../workflows/create-template.md), and their
single durable semantic contract is `design_spec.md`.

This file records only legacy read compatibility for already-existing
`brief_lock.json` artifacts. It does not define a second creation workflow,
proposal shape, confirmation gate, or new-lock schema.

## Legacy read compatibility

Existing artifacts may retain a root `brief_lock.json`. The repository keeps
the following compatibility surface for them:

- `scripts/template_brief_lock.py` resolves canonical workspace roots, reads a
  root or legacy nested lock, and validates its existing schema.
- `scripts/template_quality_checker.py` validates a present legacy lock while
  performing the normal `design_spec.md`, SVG, asset, and registrar checks.
- `template_quality_checker.py --require-brief-lock` remains an explicit
  legacy-audit option. It is never part of the new Create Template route.
- `scripts/template_preview.py` remains lock-optional. When a legacy lock is
  present, it may be copied into preview evidence; its absence does not affect
  preview generation.

The current `sustech_academic_official` Deck remains a supported example of a
workspace with a historical lock. Do not migrate, rewrite, or delete that
artifact as part of normal template creation.

## New workspace boundary

For every new Brand, Layout, and Deck workspace, validate and register from
child-owned `design_spec.md` frontmatter, template SVGs, and referenced assets.
Library and project scopes share that contract; scope changes only the
workspace location and whether a global index is registered.

If a confirmed brief needs revision, return to the shared Create Template
workflow, reconfirm it there, and update the resulting `design_spec.md` and
affected assets together. Do not create a parallel audit artifact or infer
legacy-lock fields for new workspaces.
