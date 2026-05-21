# PPT Master SUSTech-Enhanced Version

这是基于上游 `ppt-master` 的 SUSTech 增强版 skill 发布源码，用于将 PDF、DOCX、PPTX、网页、Markdown、Excel 等材料转换为高质量、可编辑的 PPTX 演示文稿。  
该版本围绕内容理解、设计规范生成、SVG 页面构建、后处理与 PPTX 导出建立了一条完整工作流，适合在 Claude Code、Cursor、Codex 等具备 agent 能力的环境中使用。

## 主要特性

- 支持 PDF、Word、PPTX、网页、Markdown、Excel 等多种输入源
- 基于 `design_spec.md` 与 `spec_lock.md` 驱动页面设计与执行约束
- 输出可编辑 PPTX，而非单纯图片化页面
- 支持模板复用、模板创建、模板自检与模板预览
- 支持图像获取、AI 生图、图表校验、speaker notes 与后处理流水线
- 支持本地版本化发布与可复现的 release contract

## 发布身份

- **Release Version**: `r2.7.0-v0.1.1`
- **Upstream Baseline**: `hugohe3/ppt-master@v2.7.0`
- **Package Root Dir**: `ppt-master/`

## 这个仓库包含什么

这是面向公开发布的、清理后的 SUSTech 增强版 skill 源码内容，包含：

- `SKILL.md`
- `VERSION`
- `RELEASE_META.json`
- `.env.example`
- `requirements.txt`
- `references/`
- `scripts/`
- `templates/`
- `workflows/`

## 这个仓库不包含什么

本仓库**不包含**本地运行产物、临时计划文档、私有环境文件和本地工作区元数据。

例如：

- `.env`
- `.synced_hash`
- `projects/`
- `tmp/`
- `cache/`
- `docs/plan/`
- 本地虚拟环境目录

## 许可证

本仓库沿用上游项目的 MIT License。详见 [LICENSE](./LICENSE)。

## 第三方说明

部分内置或引用的图标、品牌标记、来源图片和模板资源，可能仍然遵循其各自的上游许可证或署名要求。详见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。

## 说明

本公开仓库用于承载 SUSTech 增强版本线的 release-quality 源码，不承载日常私有计划、运行状态或本地工作区信息。
