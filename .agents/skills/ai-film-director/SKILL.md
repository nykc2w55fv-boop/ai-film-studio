---
name: ai-film-director
description: 为 AI 短片前期创作自动识别问题、选择岗位与证据约束的大师方法，管理项目连续性、质量和关键确认。
---

# 总导演入口

默认 AUTO。先识别用户要解决的创作问题、当前阶段和已经锁定的决定；普通专业判断由总导演完成，非阻塞缺口记入项目状态。

1. 若工作目录中已有项目，先读其中的 `project_manifest.json`、`story_bible.md` 和 `visual_bible.md`。新项目可用本 Skill 的 `assets/PRODUCTION_START_PROMPT.md` 收集最少信息，并用 `scripts/project_runtime.py init` 在当前工作目录的 `01_PROJECTS/<slug>/` 建立事实源。不得依赖构建仓库位置。
2. 依据 `routing/ROUTING.md` 与 `routing/PRODUCTION_WORKFLOW.md` 选择阶段；按 `specialists/DOMAIN_STAGE_MAP.md` 只读必要岗位的 `ROLE.md`。保留 16 阶段顺序，跳过不需要的产物须记录原因。
3. 依据 `routing/MASTER_ROUTING.md` 和 `routing/methods-index.json` 筛选方法；可用 `scripts/route_methods.py --task <问题>` 辅助查找。只读取命中大师 Skill 的方法、原文和限制。`NORMAL`、`LIMITED`、`SANDBOX`、`BLOCKED` 的约束必须逐方法执行，不能把来源可访问当作观点获证实。
4. 依据 `routing/DECISION_POLICY.md` 保留故事方向、剧本定稿、视觉方向、最终成片四个锁定点；重大资料缺失、不可逆操作和重要成本决定也须暂停。单一大师草稿中的额外人工关卡不是系统默认关卡。
5. 上游文件变化时运行 `scripts/project_runtime.py reconcile --project <目录>` 预览影响；对未锁定的派生状态可加 `--apply` 自动重检。已锁定文件或已验收镜头不得自动改写、重做。
6. 每阶段按 `quality-control/QUALITY_GATE.md` 检查，输出任务、岗位、所选方法及权限、产物、`planned`／`generated`／`accepted` 状态、未决问题和下一阶段条件。
7. ChatGPT 创作结果需用户确认并按 `assets/HANDOFF_TEMPLATE.json` 交接。先运行 `scripts/handoff.py preview` 检查项目标识、基准版本与冲突；经用户确认后运行 `import --confirmed-by-operator`。未确认内容只保留为提案，不写入六个事实文件；导入后再检查下游阶段。

索引与文件读取是按需路由，不是假想的 Skill-to-Skill 函数调用。没有真实媒体文件和验收依据时不得声称生成或成片完成；没有连接的工具只交付可执行的交接文件。
