# 模板架构：Brand / Style / Layout / Deck

> 本文定义四类可复用模板的所有权边界、工作区形态与安装后的解析
> 关系，面向贡献者和运行时作者。路由选择与具体执行步骤由
> [`routing.md`](../../workflows/routing.md) 和
> [`Create Template`](../../workflows/create-template.md) 负责。

---

## 一、四类独立的可复用契约

| 分类 | 库内位置 | 拥有什么 | 不拥有什么 |
|---|---|---|---|
| [**Brand**](../../templates/brands/README.md) | `templates/brands/<brand_id>/` | 身份：颜色、字体、Logo、语气、图标风格 | 页面结构或 SVG roster |
| [**Style**](../../templates/styles/README.md) | `templates/styles/<style_id>/` | 沟通方法、证据纪律、视觉系统默认值、审查重点 | 官方身份、应用上下文、几何或 roster |
| [**Layout**](../../templates/layouts/README.md) | `templates/layouts/<layout_id>/` | 中性画布、Master/Layout 图、页面类型、slot 与 SVG roster | 身份或重复应用场景 |
| [**Deck**](../../templates/decks/README.md) | `templates/decks/<deck_id>/` | 重复演示家族的应用上下文，以及整合后的身份与结构 | —— |

四者是种类，不是继承阶段。Design Spec 的 `kind` 与工作区形态共同
标识同一个可移植契约。PowerPoint Theme、Master、Layout 与
Placeholder 是编译目标，不是额外模板类型。

---

## 二、工作区与 Design Spec 契约

共享工作区以 [`templates/README.md`](../../templates/README.md) 为权威。
库内工作区由父目录识别 kind 与 id，因此使用 `templates/design_spec.md`；
项目工作区使用一层扁平 `templates/`，并使用
`design_spec.style.<style_id>.md` 这类限定文件名；文件名与 frontmatter
中的 kind/id 必须一致。

```text
<template_workspace>/
├── templates/       # 必需的 Design Spec；Layout/Deck 可放 SVG 原型
├── images/          # 可选位图；SVG 通过 ../images/<name> 引用
├── icons/imported/  # 可选的规范化导入向量
└── exports/         # 可选的派生审查证据，不是模板输入
```

| 分类 | 可移植契约 | 详细权威 |
|---|---|---|
| Brand | 仅身份的 spec；可有身份资产；无 roster | [`brands/README.md`](../../templates/brands/README.md) |
| Style | 单个无 roster 的方法/默认值 spec；无资产、无 SVG 页面 | [`styles/README.md`](../../templates/styles/README.md) |
| Layout | 仅结构的 spec，加结构化 SVG roster | [`layouts/README.md`](../../templates/layouts/README.md) |
| Deck | 应用上下文、身份、结构和结构化 SVG roster | [`decks/README.md`](../../templates/decks/README.md) |

只有 Layout 或 Deck 拥有 roster。项目工作区有 Layout 时，由 Layout
拥有活跃 roster；否则由 Deck 拥有。Brand 和 Style 可以与该 roster 共存，
但不贡献页面。

---

## 三、发现索引

库内发现只使用四份索引；目录扫描和裸名称匹配都不是发现机制。

| 分类 | 索引 | 选择字段 |
|---|---|---|
| Brand | [`brands_index.json`](../../templates/brands/brands_index.json) | `summary`、`primary_color` |
| Style | [`styles_index.json`](../../templates/styles/styles_index.json) | `summary`、`keywords` |
| Layout | [`layouts_index.json`](../../templates/layouts/layouts_index.json) | `summary`、`canvas_format`、`page_count`、`page_types` |
| Deck | [`decks_index.json`](../../templates/decks/decks_index.json) | `summary`、`canvas_format`、`page_count`、`primary_color` |

显式提供的确切工作区可以不经库内注册而被选择。其选择来源为
`explicit`，只记录来源，不改变该 kind 的语义。

---

## 四、选择、安装与解析

[`routing.md`](../../workflows/routing.md) 是选择器权威。库内选择由索引驱动；
显式工作区根是有意的选择，而不是让系统根据内容猜测模板。通用风格标签、
文案中的品牌名称或视觉描述都不会自行激活工作区。

默认 Generate 会在 Stage 2 前把选中的 kind 安装为限定 Design Spec。
Quick 直接消费显式提供的确切根目录。安装后的 specs 仍是相互独立的契约，
不会被压扁成一份人为合成的 `design_spec.md`。

| 决策 | 解析规则 |
|---|---|
| 当前项目契约与确认值 | 最新的显式用户指令和已确认项目状态 |
| 确切身份 | Brand 覆盖与 Deck 重叠的身份；两者都覆盖 Style fallback |
| 沟通方法与证据纪律 | 与当前项目兼容时由 Style 提供 |
| 可复用结构 | 优先 Layout，否则 Deck |
| 重复应用上下文 | Deck，但服从当前项目契约 |

仅 Style，或 Style 加 Brand，保持 flat 计划。Style 与 Layout/Deck 并存时，
Style 可以指导表达，而另一个 kind 提供结构。解析会记录工具所需的来源和
导出输入，不会把 Style 变成身份或结构所有者。

## 五、创建与验证

所有新工作区从 [`Create Template`](../../workflows/create-template.md) 进入，
并且只分派一个子工作流：

| 分类 | 子工作流 |
|---|---|
| Brand | [`create-brand.md`](../../workflows/create-template/create-brand.md) |
| Style | [`create-style.md`](../../workflows/create-template/create-style.md) |
| Layout | [`create-layout.md`](../../workflows/create-template/create-layout.md) |
| Deck | [`create-deck.md`](../../workflows/create-template/create-deck.md) |

子工作流负责 kind 专有的分析与产物；父工作流负责共同的 brief 确认、冲突
预检、工作区路由和验证交接。无 roster 的 Brand/Style 使用可移植工作区
契约；Layout/Deck 还要通过结构化 SVG、roster 及可选 review-PPTX 验证。
库内工作区只有在所属 kind 的 dry-run 通过后才注册。

## 六、不做

- 不自动匹配目录或从自然语言隐式激活模板。
- 不把 Style 用作身份、页面结构或应用契约。
- 不在本文复制 YAML/schema；精确字段和报错条件由各 kind README 与验证器负责。
- 不把 `exports/` 中的派生审查证据当作模板源。
