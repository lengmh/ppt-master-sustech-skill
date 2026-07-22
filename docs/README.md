# 文档索引

本目录提供 SUSTech 增强版 `ppt-master` 的文档入口。

## 版本信息

| 项目 | 值 |
|---|---|
| Release Version | `r4.1.0-v0.4.0` |
| Upstream Baseline | `hugohe3/ppt-master@v4.1.0` |
| Post-tag Tracking | None; fixed tag baseline |
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
- 新建 Brand、Layout、Deck 模板只使用 `design_spec.md`；已有 `brief_lock.json` 仅用于兼容性读取和显式严格审计。
- `scripts/docs/ppt-text-normalize.md` 记录当前内置 `ppt_text_normalize` Safe MVP；本发布线公开支持 `scan` / `apply`。
- 当前发布只承诺 `ppt_text_normalize` 的 `scan` / `apply` 能力。
