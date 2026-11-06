# AI Film Studio 0.2.0（私有发布）

统一知识源为本私有仓库。发布包包含总导演、14 位大师独立 Skill、11 个岗位模块、16 个阶段及 4 个确认点。127 条方法保留原审计状态：50 条 `PARTIAL/LIMITED`、77 条 `UNVERIFIED/SANDBOX`。

本版本新增标准化影片交接、冲突预览、幂等导入、六文件快照与回滚，以及版本化 Codex 安装包、Skills-only ChatGPT Plugin 包和 Hermes 发布副本。两个 ZIP 分别附 SHA-256 文件。正式影片记录仍以单片项目目录中的六个事实文件为准。

已验收：Codex 用户级安装及项目外新会话调用、ChatGPT 网页端普通聊天中的私有 Plugin 调用、私有仓库读取与写入、`main` 的验证工作流、隔离交接和安装回滚。

尚未验收或未通过：ChatGPT Project 内、桌面端及手机端分别调用；Hermes 本机能通过版本包装器发现 Skill，但真实 `hermes -z` 调用未产生最终答复；Hermes VPS 未接入。Skill 版本一致不意味着影片项目文件自动同步。

本 Release 仅供仓库授权用户使用，不公开 Plugin、研究包或媒体素材。安装与回滚步骤见 `deployment/README.md`。
