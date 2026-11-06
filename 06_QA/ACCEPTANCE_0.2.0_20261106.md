# AI Film Studio 0.2.0 验收记录｜2026-11-06

## 静态与自动化

- `python -m unittest discover -s 06_QA/tests -v`：10 项通过，覆盖 12 类路由、交接确认与冲突、幂等导入、快照回滚、安装升级回滚、连续性和失败保留。
- `python 05_AUTOMATION/scripts/validate_system.py`：80 个必需文件、3 个接收目录及 3 份 CSV 表头通过。
- `python -m compileall -q 05_AUTOMATION/scripts`：通过。
- 0.2.0 发布包 `manifest.json` 包含逐文件 SHA-256；安装器检查 15 个 Skill、127 条方法及审计状态、11 个岗位和研究引用。ZIP 整体 SHA-256 另存同名 `.sha256`。
- Skills-only Plugin 为 Agent Plugins 1.0 结构，内含 15 个 Skill，`policy.products: [CHAT]`。这只是包结构检查，**不是 ChatGPT 安装验收**。

## 真实本机验收

- 独立系统临时目录：安装 0.1.4、升级 0.2.0、回滚 0.1.4，15 个入口和安装标记核对通过；测试目录留存，未自动删除。
- 用户级 Codex：从 0.1.4 升到 0.2.0；升级前备份 ZIP 留存。新 Codex CLI 会话在项目外只读调用总导演，选中导演岗位和 `alfred-hitchcock-M01`；确认 `UNVERIFIED/SANDBOX`，未把方法说成已获证实。
- GitHub：本地 Git `main` 和 SSH 远程已建立。Hermes 只读 Deploy key 与 Codex 可写 Deploy key 均通过 Git 自带用户态 `ssh-agent` 临时解锁后的 `git ls-remote`。已对首批 98 个暂存文件（含 16 个构建研究输入）扫描常见密钥特征、媒体类型及体积，结果无发现；源码提交 `2e4ef4c` 和补齐 QA 文件的 `30e8080` 已推送 `main`。Hermes 只读 key 从远程重新克隆 `30e8080` 并完成本地 CI 复演。2026-11-07 GitHub 连接器已读取私库的 `VERSION.json`；这不是 ChatGPT Project 中 GitHub 应用调用的验收。
- 密钥事件：生成时 PowerShell 将两个引号当成私钥口令，导致非交互 SSH 认证失败。GitHub 接受公钥但客户端不能签名；永久移除口令被自动审批以安全弱化为由拒绝，未绕过。Windows 系统 `ssh-agent` 禁用；Git 自带用户态 `ssh-agent` 的一次性解锁已验证可用。私钥未上传、打印或写入项目。
- Hermes 本机：v0.16.0；官方 `skills.external_dirs` 配置已备份。2026-11-07 发现本机 0.2.0 `active.json` 为相对路径，版本包装器因路径不匹配拒绝运行；运行 `hermes_release.py select` 后保留旧指针备份，`report` 通过，包装器执行 `hermes skills list` 发现总导演及 14 位大师。直接执行 `hermes skills list` 仍为 0 个本地 Skill，说明普通启动未设置版本包装器所需环境变量。使用包装器真实调用 `hermes -z --skills ai-film-director` 在正常用户环境返回 `no final response was produced`，所以调用验收失败。项目内版本副本切换及回滚模拟通过；VPS 未连接或验收。
- 版本报告：Codex 已安装标记、Plugin 本地包、本机 Hermes active 指针均报 0.2.0；ChatGPT 真实安装与 Hermes 真实调用未通过，因此不能说三平台正式版本一致。
- 私有 Plugin：用户确认研究包的私有上传权限后，Plugin Creator 已保存个人私有 0.2.0；回读 15 个顶层 Skill。用户确认已安装且可选用。2026-11-07 提供的网页端普通聊天截图显示 `0.2.0`、总导演、四位大师的实际分析、方法 ID 和 `UNVERIFIED/SANDBOX`、`PARTIAL/LIMITED` 边界；未把缺失的“雨夜站台”剧本写成正式项目事实。截图中旧版 Codex `0.1.4` 陈述与本机安装验收冲突，应以本机安装标记和独立 CLI 调用为准。Project 内、桌面端与手机端仍未验收。

## 发布边界

- 14 位研究包共有 127 条方法；审计为 50 条 `PARTIAL/LIMITED`、77 条 `UNVERIFIED/SANDBOX`，未提升可信度。
- 用户已明确确认 14 份原研究包及摘录可上传到自己的私有 GitHub 仓库和私有 ChatGPT Plugin。提交白名单只含构建所需 16 个顶层研究文件，排除展开副本、影片项目、媒体和构建产物；暂存内容的常见密钥特征扫描无发现。
- GitHub Actions 验证与标签发布工作流已推送；当前连接器已读取仓库元数据并确认 `private`、`main`。用户在 GitHub Actions 页面确认 `30e8080` 的 “Verify safe source” 绿色通过，尚未读取作业日志。两份旧 QA 文件已通过提交 `30e8080` 推送；从该提交重新只读克隆后，本地 CI 复演的完整单元测试、结构校验、发布包构建、Plugin 导出及两个 ZIP 的 SHA-256 校验通过。`v0.2.0` 标签、私有 Release 及 VPS Hermes 部署未执行。
- ChatGPT 网页端普通聊天 Plugin 调用已由用户截图实测；ChatGPT Project 内、桌面端、手机端和 GitHub 应用在 Project 中读取该私库未实测。不能把普通聊天调用扩展为其他客户端验收。
- 《红线》原稿未提供；没有真实媒体或成片验收。
