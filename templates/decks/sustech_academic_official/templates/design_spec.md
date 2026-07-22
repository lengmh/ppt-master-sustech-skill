---
deck_id: sustech_academic_official
kind: deck
category: scenario
summary: Official academic template for course reports, research briefings, thesis defenses, and seminars.
keywords: [SUSTech, Academic, Official, University, Defense]
primary_color: "#003F43"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
source_canvas_width: 1280
source_canvas_height: 720
source_viewbox: "0 0 1280 720"
replication_mode: standard
native_structure_mode: structured
page_count: 8
---

# SUSTech Academic Official - Design Specification

> School-branded official academic presentation template for academic briefings, course reports, research updates, thesis defenses, and group seminars.

---

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | `sustech_academic_official` |
| **Display Name** | SUSTech Academic Official |
| **Category** | scenario |
| **Use Cases** | 学术汇报、课程汇报、研究汇报、论文答辩、组会分享 |
| **Design Tone** | Official, academic, restrained, school-branded |
| **Theme Mode** | Light theme, school-official academic presentation style |
| **Default Language** | Chinese |
| **Brand Positioning** | Closer to a university official template than a generic academic-defense template |
| **Reference Source** | `ppt/materials/sustech_templates/SUSTech_Academic_Template.pptx` |
| **Reference Slides Reviewed** | 1, 2, 3, 5, 6, 8, 10, 12, 14, 16 |

---

### Canvas Specification

| Property | Value |
| --- | --- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280 × 720 px |
| **viewBox** | `0 0 1280 720` |
| **Content-family Header Divider Baseline** | y = 76 |
| **Content-family Footer Divider Baseline** | y = 688 |
| **Content-family Footer Text Baseline** | y = 704 |
| **Content-family Title Start X** | x = 92 |
| **Content-family Section Name Baseline** | y = 106 |
| **Unified Top-right Logo Position** | x = 1060, y = 13, width = 220, height = 66 |
| **Content-family Base Flexible Working Zone** | x = 72, y = 132, width = 1136, height = 534 |
| **Content-family Visual Working Zone Safety** | Fixed 20 px from the shell edges and the footer divider |
| **Content-family Text-safe Zone Safety** | Same as visual working zone: fixed 20 px safety rule |

---

## II. Color Scheme

### Primary Brand Colors

| Role | Value | Usage |
| --- | --- | --- |
| **Primary Deep Teal** | `#003F43` | Main headings, logo-aligned brand tone, strong text emphasis |
| **Primary Orange** | `#E3660D` | Divider accent, process arrows, emphasis strokes |
| **Secondary Cyan** | `#01ABA8` | Secondary corner cues, complementary accent |
| **Warning Dark Red** | `#B63742` | Key highlights, emphasis titles, cautionary accent |

### Neutral / Surface Colors

| Role | Value | Usage |
| --- | --- | --- |
| **Background White** | `#FFFFFF` | Main page background |
| **Soft Panel Gray** | `#EAF1F0` | Light cyan card surfaces for parallel content, evidence support, and cool-secondary grouping |
| **Warm Panel** | `#F6EBDF` | Light warm/orange card surfaces for secondary emphasis and parallel grouping |
| **Soft Footer Ground** | `#F8F7F5` | Cover lower field / soft support surfaces |
| **Border Gray** | `#CECECE` | Dividers, subtle borders, shell outlines |

### Text Colors

| Role | Value | Usage |
| --- | --- | --- |
| **Primary Text** | `#1D1C1C` | Body content |
| **Secondary Text** | `#585555` | Descriptions, labels, explanatory text |
| **Tertiary Text** | `#9D9D9D` | Footer school name, helper text, captions |
| **Placeholder Text** | `#A8A4A1` | Template-only placeholder copy |

---

## III. Typography System

### Font Stack

- **Primary Font Stack**: `"Microsoft YaHei", Arial, sans-serif`
- **Title Support Stack**: `Arial, sans-serif`
- **Formula Stack**: `"Cambria Math", "Times New Roman", serif`

### Font Size Hierarchy

| Level | Usage | Size | Weight |
| --- | --- | --- | --- |
| H1 | Cover main title | 52px | Bold |
| H2 | Cover subtitle / ending message | 34–60px | Bold |
| H3 | Content / TOC page title | 32px | Bold |
| H4 | Chapter title | 50px | Bold |
| H5 | TOC item title | 27px | Bold |
| H6 | Card / block title | 20–24px | Bold |
| Section Line | `{{SECTION_NAME}}` | 26.7px / 20pt | Regular |
| Body | Main body text | 15–22px | Regular |
| Annotation | Caption / helper / note | 14–16px | Regular |
| Page Number | Footer page number | 16px | Bold |
| Chapter Number | Divider background number | 176px | Bold |

### Typography Behavior Rules

- Chinese is the default content language.
- Long Chinese or English text must be manually wrapped with multiple `<text>` lines or `<tspan>` when necessary; do not rely on automatic line wrapping.
- Long formulas and mixed English-symbol expressions must also be manually wrapped or split into multiple lines when needed; do not assume a single formula line will fit the evidence area safely.
- Content-family templates should favor multi-line readable blocks over long single-line text.

---

## IV. Signature Design Elements

### Shared Brand Elements

- Top-left uses the standard school motif asset where that page family requires the branded academic shell.
- Top-right uses the merged school-logo-structure asset.
- Bottom English school name is fixed text: `Southern University of Science and Technology`.

### Cover / Ending Specific Shell Rules

- Cover and ending pages retain explicit scenic campus background imagery.
- Cover uses the merged full top-right school logo asset only and intentionally does not use the extra top-left motif.
- Ending keeps the scenic background + top-right merged logo + simplified closing structure.

### TOC / Chapter / Content-family Shell Rules

- Content-family pages use a **two-part divider** below the title: orange lead segment + gray continuation segment.
- TOC / chapter / content-family pages share the same top divider rhythm and footer rhythm.
- TOC / chapter / content-family pages avoid large scenic imagery and instead rely on motif + logo + footer branding.

### Fixed Asset Policy

The following are fixed assets, **not placeholders**, and must not be replaced by generated content:

| Asset Role | Active File | Status |
| --- | --- | --- |
| School logo + top-right logo structure (merged active asset) | `full_top_right_school_logo.png` | Active |
| Cover scenic campus background | `cover_campus_bg.jpg` | Active |
| Ending scenic campus background | `ending_campus_bg.jpg` | Active |
| Top-left geometric school motif | `top_left_motif_standard.png` | Active |
| Bottom English school name | fixed text, not placeholder | Active |
| Standalone school logo | `school_logo.png` | Legacy / do not use for current layouts |
| Legacy top-left motif | `top_left_motif.png` | Legacy / do not use for current layouts |
| Legacy top-right logo structure | `top_right_logo_structure.png` | Legacy / do not use for current layouts |

### Content-family Structural Rules

### Content-family Card Color Rules

- **Primary use of Deep Teal (`#003F43`)**: page titles, TOC titles, chapter titles, structural headings, and strong text emphasis aligned with school branding.
- **Deep Teal background is NOT the default card background** inside `content_area`. It should be used only for **special hero / primary emphasis cards** where one block must dominate the page hierarchy.
- **Default content card options** inside `content_area` are:
  1. **White fill + gray border** (`#FFFFFF` + `#CECECE`) for neutral evidence / data / text containers
  2. **Light cyan fill** (`#EAF1F0`) for cool-secondary cards
  3. **Light warm fill** (`#F6EBDF`) for warm-secondary or emphasis cards
- For **parallel / same-level cards**, prefer either:
  - a **light cyan + light warm mixed pair/group**, or
  - a fully consistent set of **white-outline cards**, or
  - a fully consistent set of one secondary surface family when hierarchy is intentionally flat.
- Avoid using multiple large deep-teal cards on one content page. In most academic / official scenarios, at most **one hero deep-teal card** should appear on a page, and many pages should have none.
- Body content in cards should primarily use **Primary Text `#1D1C1C`** and **Secondary Text `#585555`**. Orange is for emphasis, connectors, or key labels rather than large text paragraphs.

- Page number is mandatory on content-family pages.
- `SECTION_NUM` is intentionally removed from this template contract; any numbering should be written directly into `{{PAGE_TITLE}}` when needed.
- `SOURCE` is intentionally removed from this template contract.
- The content-family working area should use outer space more fully than earlier conservative versions, while preserving a fixed 20 px safety edge inside the shell.
- The design philosophy is **weak framing + strong hierarchy**.
- `03_content.svg` is a free base template: it does **not** predefine card count, image slot count, fixed text slot count, or a default equal-split composition.

---

## V. Page Roster

### 1. Cover Page — `01_cover.svg`
- Light official opening page with scenic lower background.
- Uses the merged full top-right school logo asset only; no extra top-left motif.
- Preferred fields: `{{TITLE}}`, `{{SUBTITLE}}`, `{{AUTHOR}}`, `{{DATE}}`.
- `DEPARTMENT` and `EMAIL` are intentionally excluded.
- Academic identity fields remain cover-only.

### 2. Table of Contents Page — `02_toc.svg`
- School motif + merged full top-right logo asset + official footer shell.
- Title positioned like a content page title.
- Uses canonical indexed TOC placeholders.
- TOC numbering may remain decorative / structural and does not require dedicated numeric placeholders.
- `{{TOC_ITEM_1_DESC}}`-style descriptions are allowed and supported.
- Generalized indexed naming (`1..N`) is intentionally preserved in the contract so the TOC can be expanded later, even though the current template file implements six visible TOC rows.

### 3. Chapter Divider Page — `02_chapter.svg`
- Official chapter break with large chapter number and chapter title.
- Preferred fields: `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`.
- No chapter subtitle or fixed chapter descriptor line is part of the active contract.

### 4. Base Content Page — `03_content.svg`
- Acts as the **free composition base template**.
- Minimizes rigid inner structure.
- Intended for summary pages, mixed-information pages, and flexible layouts. Parallel content should generally be grouped using white-outline, light cyan, and light warm cards before considering dark hero blocks. Parallel content should generally be grouped using white-outline, light cyan, and light warm cards before considering dark hero blocks.
- `{{CONTENT_AREA}}` should be treated as an open stage rather than a locked card grid. Default card coloring should follow the template card color rules: white-outline / light cyan / light warm first, deep teal background only for exceptional hero emphasis. Default card coloring should follow the template card color rules: white-outline / light cyan / light warm first, deep teal background only for exceptional hero emphasis.
- It is a design boundary shell, not a fixed execution layout.

### 5. Text-Image Variant — `03_content_text_image.svg`
- Acts as an **image-led asymmetric reference**.
- Large figure area takes priority.
- Text region becomes compact guidance rather than co-equal mass.
- Encourages reduced empty text area and clearer visual hierarchy.
- It is a style / composition reference, not a rigid implementation grammar.

### 6. Formula / Chart / Evidence Variant — `03_content_formula_chart.svg`
- Acts as an **evidence-led reasoning reference**.
- Formula and chart do not need to appear together.
- Supports formula-led pages, chart-led pages, or balanced reasoning pages.
- Weak derivation / logic / arrow anchors are allowed.
- It is a style / composition reference, not a rigid implementation grammar.

### 7. Process / Method / Path Variant — `03_content_process.svg`
- Acts as a **process-led but flexible reference**.
- Process may be a light guide, a fused structure with content, or the main visual focus.
- Lower content region may merge explanation, method details, results, or application.
- It is a style / composition reference, not a rigid implementation grammar.

### 8. Ending Page — `04_ending.svg`
- Simple official closing page with scenic background.
- Active contract keeps only `{{THANK_YOU}}`.
- `{{CONTACT_INFO}}` is intentionally excluded.

---

## VI. Layout Modes (Recommended)

| Layout Mode | Recommended Use |
| --- | --- |
| **Free Composition Base** | Mixed summary pages, conclusion pages, overview pages |
| **Image-led Asymmetry** | Figure-first pages, visual evidence pages, product / chart screenshots |
| **Evidence-led Reasoning** | Formula derivation, chart interpretation, technical proof, benchmark explanation |
| **Process-led Structure** | Workflow, methodology, system path, staged explanation |
| **Process + Content Fusion** | When the process itself is visual but also needs explanatory integration |

### Mode Selection Principles

- Prefer the content variant whose **main visual hierarchy** matches the page’s core message.
- Do not force equal split layouts when the information weight is asymmetric.
- Reduce large empty text boxes; expand the main visual or core reasoning area first.
- The three content variants remain design-idea / style references, not fixed execution specifications.

---

## VII. Spacing Specification

| Element | Value / Rule |
| --- | --- |
| Title left inset | 92px |
| Top divider baseline | 76px |
| Footer divider baseline | 688px |
| Footer text baseline | 704px |
| Base content outer shell | x=72, y=132, width=1136, height=534 |
| Content-family inner safety edge | Fixed 20 px from shell edges |
| Recommended card padding | 18–30px depending on card size |
| Recommended block gap | 20–28px |
| Recommended caption strip height | 28–36px |
| Recommended rounded corner radius | 12–22px |

### Practical Spacing Rules

- Prefer using the lower area more fully before adding new empty gutters.
- Content-family pages should approach the footer divider more closely than earlier versions, while still preserving the fixed 20 px safety band.
- `visual working zone` and `text-safe zone` are aligned: both follow the same fixed 20 px safety rule.
- When text threatens to overflow, prefer wrapping and vertical expansion over reducing the visual hierarchy of the page title.

---

## VIII. SVG Technical Constraints

### Mandatory Rules

1. `viewBox` must remain `0 0 1280 720`.
2. Use inline SVG attributes only; no `<style>`, `class`, or `@font-face`.
3. Use `fill-opacity` / `stroke-opacity`; do not use `rgba()`.
4. Use manual text wrapping via multiple `<text>` nodes or `<tspan>` when needed.
5. Use semantic asset references where possible.

### Prohibited Elements

- `<foreignObject>`
- `<textPath>`
- `<clipPath>`
- `mask`
- `<script>`
- `<animate*>`
- `<iframe>`
- `<symbol> + <use>`
- `<g opacity="...">` group opacity patterns for PPT output

### PPT Compatibility Rules

- Long text must be layout-tested in SVG form before export.
- Long formulas and mixed English-symbol expressions must also be explicitly checked for line fit and manually wrapped if necessary.
- Do not assume PPT native shapes will auto-wrap long single-line SVG text safely.
- Image-led / evidence-led variants should protect their main visual area from long explanatory text spillover.

---

## IX. Placeholder Specification

| Placeholder | Applicable Page | Notes |
| --- | --- | --- |
| `{{TITLE}}` | Cover | Main cover title |
| `{{SUBTITLE}}` | Cover | Cover subtitle |
| `{{AUTHOR}}` | Cover | Presenter / academic identity |
| `{{DATE}}` | Cover | Cover date |
| `{{TOC_ITEM_1_TITLE}}` ~ `{{TOC_ITEM_N_TITLE}}` | TOC | Canonical indexed TOC titles |
| `{{TOC_ITEM_1_DESC}}` ~ `{{TOC_ITEM_N_DESC}}` | TOC | Canonical indexed TOC descriptions |
| `{{CHAPTER_NUM}}` | Chapter | Chapter number |
| `{{CHAPTER_TITLE}}` | Chapter | Chapter title |
| `{{PAGE_TITLE}}` | Content family | Main content title; embeds numbering if needed |
| `{{SECTION_NAME}}` | Content family | Secondary line below page title |
| `{{CONTENT_AREA}}` | Content family | Flexible / representative content anchor |
| `{{PAGE_NUM}}` | Content family | Footer page number |
| `{{THANK_YOU}}` | Ending | Ending-only message |

### Intentionally Excluded Placeholders

The following placeholder families are **not part of the active contract** for this template:

- `{{DEPARTMENT}}`
- `{{EMAIL}}`
- `{{SECTION_NUM}}`
- `{{SOURCE}}`
- `{{CONTACT_INFO}}`

---

## X. Usage Guide (Recommended)

1. Use `03_content.svg` when the page needs free composition and the hierarchy should be decided by the actual material.
2. Use `03_content_text_image.svg` when the main figure or screenshot should dominate the page and the text only needs to guide reading.
3. Use `03_content_formula_chart.svg` when the page is evidence-led: formula-led, chart-led, or balanced reasoning are all valid uses.
4. Use `03_content_process.svg` when the process itself is important, whether as a dominant visual, a fused narrative structure, or a lightweight guide.
5. For all content-family pages, expand the composition toward the outer working zone before introducing unnecessary empty gutters.
6. When text becomes long, wrap it manually and preserve hierarchy instead of shrinking the whole layout indiscriminately.

## XI. Contract Notes and Exceptions

- Cover retains academic identity fields only; no extra identity expansion is required elsewhere.
- TOC keeps canonical indexed placeholders even when numeric labels are visually shown on the page.
- Ending page is deliberately simplified to `{{THANK_YOU}}` only.
- Content variants are intended as **references for hierarchy and composition**, not rigid slot diagrams.
- Any future validation deck should use these rules as the authoritative content-family behavior contract.
