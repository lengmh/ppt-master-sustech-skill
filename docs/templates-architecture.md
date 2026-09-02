# Template Architecture: Brand / Style / Layout / Deck

> This architecture document defines the four reusable template kinds, their
> ownership boundaries, workspace shape, and how an installed set is resolved.
> It is for contributors and runtime authors. Route selection and exact
> procedure remain owned by [`routing.md`](../workflows/routing.md) and
> [`Create Template`](../workflows/create-template.md).

---

## 1. Four independent reusable contracts

| Kind | Library location | Owns | Does not own |
|---|---|---|---|
| [**Brand**](../templates/brands/README.md) | `templates/brands/<brand_id>/` | Identity: color, typography, logo, voice, icon style | Page structure or an SVG roster |
| [**Style**](../templates/styles/README.md) | `templates/styles/<style_id>/` | Communication method, evidence discipline, visual-system defaults, review focus | Official identity, application context, geometry, or a roster |
| [**Layout**](../templates/layouts/README.md) | `templates/layouts/<layout_id>/` | Brand-neutral canvas, Master/Layout graph, page types, slots, and SVG roster | Identity or a recurring application |
| [**Deck**](../templates/decks/README.md) | `templates/decks/<deck_id>/` | Recurring presentation-family context plus integrated identity and structure | — |

These are kinds, not inheritance stages. `kind` in a Design Spec and the
workspace shape identify the same portable contract. PowerPoint Theme,
Master, Layout, and Placeholder objects are compilation targets rather than
additional template kinds.

---

## 2. Workspace and Design Spec contract

[`templates/README.md`](../templates/README.md) is the shared workspace
authority. A library workspace uses its parent directory to identify kind and
id, so it keeps `templates/design_spec.md`. A project workspace has one flat
`templates/` directory and uses qualified files such as
`design_spec.style.<style_id>.md`; filename kind/id and frontmatter must agree.

```text
<template_workspace>/
├── templates/       # required Design Spec; Layout/Deck may add SVG prototypes
├── images/          # optional bitmaps, addressed by SVG as ../images/<name>
├── icons/imported/  # optional canonical imported vectors
└── exports/         # optional derived review evidence, never a template input
```

| Kind | Portable contract | Detailed authority |
|---|---|---|
| Brand | Identity-only spec; optional identity assets; no roster | [`brands/README.md`](../templates/brands/README.md) |
| Style | One roster-free method/defaults spec; no assets or SVG pages | [`styles/README.md`](../templates/styles/README.md) |
| Layout | Structure-only spec plus a structured SVG roster | [`layouts/README.md`](../templates/layouts/README.md) |
| Deck | Application context, identity, structure, and a structured SVG roster | [`decks/README.md`](../templates/decks/README.md) |

Only Layout or Deck owns a roster. In a project workspace, Layout owns the
active roster when present; otherwise Deck owns it. Brand and Style may coexist
with that roster without contributing pages.

---

## 3. Discovery indexes

Library discovery uses exactly four indexes; directory scanning and bare-name
matching are not discovery mechanisms.

| Kind | Index | Selector fields |
|---|---|---|
| Brand | [`brands_index.json`](../templates/brands/brands_index.json) | `summary`, `primary_color` |
| Style | [`styles_index.json`](../templates/styles/styles_index.json) | `summary`, `keywords` |
| Layout | [`layouts_index.json`](../templates/layouts/layouts_index.json) | `summary`, `canvas_format`, `page_count`, `page_types` |
| Deck | [`decks_index.json`](../templates/decks/decks_index.json) | `summary`, `canvas_format`, `page_count`, `primary_color` |

An exact supplied workspace can be selected without library registration. Its
selection source is `explicit`, which records provenance only and does not
change the kind's semantics.

---

## 4. Selection, installation, and resolution

[`routing.md`](../workflows/routing.md) is the selector authority.
Library selection is index-backed; an explicit workspace root is an intentional
selection rather than a request for heuristic matching. A generic style label,
brand name in prose, or visual description never activates a workspace by
itself.

Default Generate installs the selected kinds as qualified Design Specs before
Stage 2. Quick consumes supplied exact roots directly. The installed specs
remain separate contracts; they are not collapsed into a synthetic
single-source `design_spec.md`.

| Decision | Resolution rule |
|---|---|
| Current project contract and confirmed values | Latest explicit user instruction and confirmed project state |
| Exact identity | Brand overrides overlapping Deck identity; both override Style fallbacks |
| Communication method and evidence discipline | Style, where compatible with the current project |
| Reusable structure | Layout, otherwise Deck |
| Recurring application context | Deck, subordinate to the current project contract |

Style alone, or Style plus Brand, keeps a flat plan. A Style beside Layout or
Deck can guide expression while the other kind supplies structure. Resolution
records tool-facing provenance and exporter inputs; it does not make Style an
identity or structural owner.

## 5. Creation and validation

All new workspaces enter [`Create Template`](../workflows/create-template.md),
which dispatches exactly one child:

| Kind | Child workflow |
|---|---|
| Brand | [`create-brand.md`](../workflows/create-template/create-brand.md) |
| Style | [`create-style.md`](../workflows/create-template/create-style.md) |
| Layout | [`create-layout.md`](../workflows/create-template/create-layout.md) |
| Deck | [`create-deck.md`](../workflows/create-template/create-deck.md) |

The child owns kind-specific analysis and output. The parent owns the shared
brief confirmation, collision preflight, workspace routing, and validation
handoff. Roster-free Brand/Style use the portable workspace contract; Layout
and Deck additionally pass structured SVG, roster, and optional review-PPTX
validation. Library workspaces register only after their kind-specific
dry-run succeeds.

## 6. Non-goals

- No automatic catalog matching or implicit activation from prose.
- No use of Style as an identity, page-structure, or application contract.
- No YAML/schema duplication here; the kind READMEs and validators own exact
  fields and error conditions.
- No treating generated review evidence in `exports/` as template source.
