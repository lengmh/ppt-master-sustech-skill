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
  <a href="VERSION"><img alt="version" src="https://img.shields.io/badge/version-r4.1.0--v0.4.0-0ea5e9?style=flat-square"></a>
  <a href="https://github.com/lengmh/ppt-master-sustech-skill/stargazers"><img alt="stars" src="https://img.shields.io/github/stars/lengmh/ppt-master-sustech-skill?style=flat-square&label=stars&logo=github"></a>
  <a href="https://github.com/lengmh/ppt-master-sustech-skill/commits"><img alt="last commit" src="https://img.shields.io/github/last-commit/lengmh/ppt-master-sustech-skill?style=flat-square&label=last%20commit"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/github/license/lengmh/ppt-master-sustech-skill?style=flat-square&label=license"></a>
  <a href="RELEASE_META.json"><img alt="upstream" src="https://img.shields.io/badge/upstream-ppt--master%20v4.1.0-f59e0b?style=flat-square"></a>
</p>

<p align="center">
  <a href="#快速开始">Quick Start</a> ·
  <a href="#功能亮点">Features</a> ·
  <a href="#sustech-增强">SUSTech</a> ·
  <a href="docs/README.md">Docs</a> ·
  <a href="https://github.com/lengmh/ppt-master-sustech-skill/releases">Releases</a>
</p>

# PPT Master SUSTech 增强版 Skill

`ppt-master` 是一个面向 agent 环境的演示文稿生成 skill，可将 PDF、DOCX、PPTX、网页、Markdown、Excel 等材料转换为高质量 SVG 页面，并导出为可编辑 PPTX。

本仓库在上游能力基础上加入 SUSTech 模板与质量增强，可在 Claude Code、Codex、Cursor 等具备 agent 能力的环境中使用。

## 版本信息

| 项目 | 信息 |
|---|---|
| 当前版本 | `r4.1.0-v0.4.0` |
| 对应上游 | `hugohe3/ppt-master@v4.1.0` |
| 下载 | [GitHub Releases](https://github.com/lengmh/ppt-master-sustech-skill/releases) |

## 功能亮点

- 支持 PDF、DOCX、PPTX、网页、Markdown、Excel 等多种输入源，并自动整理为统一的 Markdown 与转换结果。
- 通过 `design_spec.md` 和 `spec_lock.md` 固化设计方向与执行约束，减少多轮生成中的样式漂移。
- 采用 SVG-first 页面构建流程，在保持视觉质量的同时导出可编辑 PPTX。
- 可在浏览器中预览、直接编辑和标注页面，并分阶段确认设计方向、设计系统、图像策略与执行选项；确认界面包含日文文案。
- 可分别处理 PPTX 模板填充、现有演示稿等比例美化，以及备注、音频、计时和转场增强。
- 可按需生成原生可编辑表格与图表，同时生成配套工作簿，并检查图表显示和负值配色等细节。
- 提供 `brand / layout / deck` 三类模板工作区，便于复用和管理模板页、图片及图标资产。
- 提供 AI 图像生成与检索、风格预览、图标同步和切图工具，方便统一视觉素材。
- 内置图表模板、演讲者备注、动画、LaTeX 公式渲染和导出辅助能力。
- 内置 `ppt_text_normalize` Safe MVP，可使用 `scan` / `apply` 检查并规范 PPTX 文字样式。
- 可按需启用 `visual-review`，检查渲染后的页面效果。

## SUSTech 增强

在上游 v4.1.0 基础上，本版本进一步提供：

- 轻量 layout-quality 静态诊断，帮助发现页面溢出、对齐和间距问题。
- 新建 Brand、Layout、Deck 模板以 `design_spec.md` 为唯一语义合同，保留旧 `brief_lock.json` 的读取与按需严格审计兼容。
- 内置 `sustech_academic_official` Deck，模板页与图片资产分层存放，便于复用和替换。
- 基于 `presentation_core` 提供结构化 Layout 集合，覆盖常见演示页面组织方式。

更多增强说明与后续规划见 [`docs/Roadmap.md`](docs/Roadmap.md)。

## PPTX 文本规范化

`ppt_text_normalize` 用于检查并统一 PPTX 中的文字样式，同时尽量保持原有内容和版式：

- `scripts/ppt_text_normalize/scan.py`：扫描潜在的样式不一致并生成报告。
- `scripts/ppt_text_normalize/apply.py`：根据扫描结果应用规范化调整。

默认采用 Safe MVP 策略，仅执行经过验证的保守调整。

## 目录结构

```text
SKILL.md                 # agent 主入口
VERSION                  # 当前版本
RELEASE_META.json         # 版本来源与上游信息
.env.example              # 环境变量示例
requirements.txt          # Python 依赖列表
references/               # agent 角色参考与生成指引
scripts/                  # 转换、渲染、预览、导出、模板等辅助脚本
templates/                # brands / layouts / decks / charts / icons
workflows/                # generate-pptx、stages、profiles、governance、create-template 等流程
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

常用工具入口（使用 `--help` 查看参数）：

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
