# AI Film Studio 0.2.0

统一知识源为本仓库。发布包包含总导演、14 位大师独立 Skill、11 个岗位模块、16 个阶段及 4 个确认点。127 条方法保留原审计状态：50 条 `PARTIAL/LIMITED`、77 条 `UNVERIFIED/SANDBOX`。

本版本新增标准化影片交接、冲突预览、幂等导入、六文件快照与回滚，以及版本化 Codex 安装包、Skills-only ChatGPT Plugin 包和 Hermes 发布副本。两个 ZIP 分别附 SHA-256 文件。正式影片记录仍以单片项目目录中的六个事实文件为准。

已验收：Codex 用户级安装及项目外新会话调用、ChatGPT 网页端普通聊天中的个人 Plugin 调用、仓库读取与写入、`main` 的验证工作流、隔离交接和安装回滚。

尚未验收或未通过：ChatGPT Project 内、桌面端及手机端分别调用；Hermes 本机能通过版本包装器发现 Skill，但真实 `hermes -z` 调用未产生最终答复；Hermes VPS 未接入。Skill 版本一致不意味着影片项目文件自动同步。

本 Release 的系统包和 Plugin 包随 GitHub 仓库公开分发，依据用户 2026-11-23 对完整仓库和 Release 的公开授权。个人 ChatGPT Plugin 仍为私有，下载 GitHub 包不会自动安装到他人账户；各人需按其客户端可用的官方安装流程操作。安装与回滚见 `deployment/README.md`，使用话术见 `USAGE_FOR_OTHERS.md`。影片项目文件和媒体素材不在本仓库。
