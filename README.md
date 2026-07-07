<p align="center">
  <img src="assets/readme-hero.svg" alt="PPT Master" width="900">
</p>

<p align="center">
  <strong>document in · editable PPTX out</strong>
</p>

<p align="center">
  AI-assisted presentation generation for agent workflows.<br>
  SVG-first pages, native editable PPTX export, SUSTech-enhanced templates.
</p>

<p align="center">
  <a href="VERSION"><img alt="version" src="https://img.shields.io/badge/version-r3.1.0--v0.4.0-0ea5e9?style=flat-square"></a>
  <a href="https://github.com/lengmh/ppt-master-sustech-skill/stargazers"><img alt="stars" src="https://img.shields.io/github/stars/lengmh/ppt-master-sustech-skill?style=flat-square&label=stars&logo=github"></a>
  <a href="https://github.com/lengmh/ppt-master-sustech-skill/commits"><img alt="last commit" src="https://img.shields.io/github/last-commit/lengmh/ppt-master-sustech-skill?style=flat-square&label=last%20commit"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/github/license/lengmh/ppt-master-sustech-skill?style=flat-square&label=license"></a>
  <a href="RELEASE_META.json"><img alt="upstream" src="https://img.shields.io/badge/upstream-ppt--master%20v3.1.0-f59e0b?style=flat-square"></a>
</p>

<p align="center">
  <a href="#快速开始">Quick Start</a> ·
  <a href="#功能亮点">Features</a> ·
  <a href="#sustech-增强内容">SUSTech</a> ·
  <a href="docs/README.md">Docs</a> ·
  <a href="https://github.com/lengmh/ppt-master-sustech-skill/releases">Releases</a>
</p>

# PPT Master SUSTech 增强版 Skill

`ppt-master` 是一个面向 agent 环境的演示文稿生成 skill，可将 PDF、DOCX、PPTX、网页、Markdown、Excel 等材料转换为高质量 SVG 页面，并导出为可编辑 PPTX。

本仓库提供 SUSTech 增强版本线源码，适合在 Claude Code、Codex、Cursor 等具备 agent 能力的环境中使用。

## 版本信息

| 项目 | 值 |
|---|---|
| Release Version | `r3.1.0-v0.4.0` |
| Upstream Baseline | `hugohe3/ppt-master@v3.1.0` |
| Upstream Commit | `b8808a3a17377ea4e7fd79bdad096bab613f86b9` |
| Tracked Range | `v3.1.0..c2cb78ad997b41d16cefe083831d62571ab9f741` |
| Root Directory | `ppt-master/` |

Release page:

- <https://github.com/lengmh/ppt-master-sustech-skill/releases>

## 功能亮点

- 支持 PDF、DOCX、PPTX、网页、Markdown、Excel 等多种输入源。
- 通过 `design_spec.md` 和 `spec_lock.md` 驱动设计意图与执行约束。
- 采用 SVG-first 页面构建流程，并导出可编辑 PPTX。
- 支持浏览器 live preview，用于查看页面、direct edit 和提交标注。
- 支持 staged Confirm UI、日文 UI 文案、native PPTX template-fill 与 existing-PPTX 增强工作流。
- 支持 opt-in native PPTX tables/charts，并包含图表工作簿生成与负值点颜色修复。
- 支持 `brand / layout / deck` 三分模板体系。
- 支持 AI image manifest 工作流和图像 prompt catalog。
- 内置 chart templates、图表校验指引、speaker notes、动画与导出辅助能力。
- 内置 `ppt_text_normalize` Safe MVP：公开支持 `scan` / `apply` PPTX 文字样式归一化。
- 支持 opt-in `visual-review`，用于渲染后页面检查。
- 支持 LaTeX 公式渲染：通过 `scripts/latex_render.py` 和 `images/formula_manifest.json` 生成公式 PNG 资产。

## SUSTech 增强内容

本版本融合上游 v3.1.0 与 `main@c2cb78a` 跟踪更新，并叠加以下 SUSTech 增强：

- live-preview 以 upstream v3.1.0 direct-edit 行为为准；本地保留轻量 layout-quality 静态诊断，不覆盖上游交互模型。
- 模板创建审计流：`brief_lock.json`、strict validation mode、template preview feedback。
- SUSTech 与组织模板统一整理为 `templates/decks/` 条目。
- 已清理旧品牌类 `templates/layouts/`；该目录现在只保留结构型 layout presets。
- 正式纳入 `ppt_text_normalize` Safe MVP：本发布线只公开承诺 `scan` / `apply`，review gate / browser panel 需单独复核后再宣布。
- 通过 `VERSION` 和 `RELEASE_META.json` 记录版本、上游基线和追踪范围。
- 通过 [`docs/Roadmap.md`](docs/Roadmap.md) 记录 SUSTech 增强清单和上游兼容关注项。

## `ppt_text_normalize` 当前公开支持命令面

当前公开支持命令面包含：

- `scripts/ppt_text_normalize/scan.py`
- `scripts/ppt_text_normalize/apply.py`
- Safe MVP 保守归一化语义与配套报告输出

源码中保留的 review workspace / reviewed-rules 相关脚本不作为 `r3.1.0-v0.4.0` 的公开发布承诺；需要先完成单独复核。

## 目录结构

```text
SKILL.md                 # agent 主入口
VERSION                  # 当前 release 版本
RELEASE_META.json         # 版本、上游基线与追踪范围元数据
.env.example              # 环境变量示例
requirements.txt          # Python 依赖列表
references/               # agent 角色参考与生成指引
scripts/                  # 转换、渲染、预览、导出、模板等辅助脚本
templates/                # brands / layouts / decks / charts / icons
workflows/                # live-preview、create-template、template-fill、visual-review、图表校验等流程
docs/                     # 使用与设计文档
```

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

然后根据需要在 `.env` 中配置模型、图像生成、搜索、TTS 等 provider。

agent 主入口：

```text
SKILL.md
```

常用 CLI 检查：

```bash
python3 scripts/svg_to_pptx.py --help
python3 scripts/svg_editor/server.py --help
python3 scripts/latex_render.py --help
python3 scripts/visual_review.py --help
python3 scripts/register_template.py --help
```

说明：`visual-review` 只有在执行真实浏览器渲染时才需要 Playwright / Chromium；基础安装不强制要求。

## 更多文档

- [文档索引](docs/README.md)
- [SUSTech 增强路线图](docs/Roadmap.md)
- [技术设计](docs/technical-design.md)
- [模板架构](docs/templates-architecture.md)
- [第三方说明](THIRD_PARTY_NOTICES.md)

## License

本仓库沿用上游 MIT License。详见 [LICENSE](LICENSE)。

## Third-party Notices

内置或引用的图标、品牌标记、来源图片和模板资产可能遵循各自的上游许可证或署名要求。详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
