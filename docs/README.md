# 文档索引

本目录提供 SUSTech 增强版 `ppt-master` 的文档入口。

## 版本信息

| 项目 | 值 |
|---|---|
| Release Version | `r3.1.0-v0.4.0` |
| Upstream Baseline | `hugohe3/ppt-master@v3.1.0` |
| Tracked Range | `v3.1.0..c2cb78ad997b41d16cefe083831d62571ab9f741` |
| Root Directory | `ppt-master/` |

## 文档列表

- [Roadmap](Roadmap.md) — SUSTech 增强清单、上游追踪状态和兼容关注项。
- [技术设计](technical-design.md) — 系统架构和工作流设计。
- [模板架构](templates-architecture.md) — `brand / layout / deck` 模板模型。
- [第三方说明](THIRD_PARTY_NOTICES.md) — 内置或引用资产的许可证和署名说明。
- [中文技术设计](zh/technical-design.md)
- [中文模板架构](zh/templates-architecture.md)

## 使用提示

- 根目录 [`README.md`](../README.md) 是推荐起点。
- `SKILL.md` 是 agent 主入口。
- `VERSION` 和 `RELEASE_META.json` 记录版本、上游基线和追踪范围。
- `docs/Roadmap.md` 记录 SUSTech 特有增强和上游兼容关注项。
- `scripts/docs/ppt-text-normalize.md` 记录当前内置 `ppt_text_normalize` Safe MVP；本发布线公开支持 `scan` / `apply`。
- review gate / browser panel / reviewed-rules flow 保留为源码资产，需单独复核后再作为公开能力宣布。
