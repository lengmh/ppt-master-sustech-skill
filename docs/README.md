# 文档索引

本目录提供 SUSTech 增强版 `ppt-master` 的文档入口。

## 版本信息

| 项目 | 值 |
|---|---|
| Release Version | `r2.10.0-v0.3.0` |
| Upstream Baseline | `hugohe3/ppt-master@v2.10.0` |
| Tracked Range | `v2.10.0..137e0e5ebc385620e9cc95fcc56d8f67e3d8c3a9` |
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
- `scripts/docs/ppt-text-normalize.md` 记录当前内置 `ppt_text_normalize` Safe MVP 与正式支持、运行时可选的 visual review gate 命令面和安全边界。
- `ppt_text_normalize` 的 Safe MVP 内核仍是 `scan` / visual review / `apply`；visual review gate 是介于 scan 与 apply 之间的正式人工审核层。
