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
- GitHub：本地 Git `main` 和 SSH 远程已建立。仓库最初没有引用；Hermes 只读 Deploy key 与 Codex 可写 Deploy key 均通过 Git 自带用户态 `ssh-agent` 临时解锁后的 `git ls-remote`。已对 98 个暂存文件（含 16 个构建研究输入）扫描常见密钥特征、媒体类型及体积，结果无发现；提交 `2e4ef4c` 已推送 `main`。Hermes 只读 key 又从远程克隆同一提交。GitHub ChatGPT 应用对新仓库仍返回 404，需单独授权。
- 密钥事件：生成时 PowerShell 将两个引号当成私钥口令，导致非交互 SSH 认证失败。GitHub 接受公钥但客户端不能签名；永久移除口令被自动审批以安全弱化为由拒绝，未绕过。Windows 系统 `ssh-agent` 禁用；Git 自带用户态 `ssh-agent` 的一次性解锁已验证可用。私钥未上传、打印或写入项目。
- Hermes 本机：v0.16.0；官方 `skills.external_dirs` 配置已备份并接入独立 0.2.0 副本，`hermes skills list` 发现总导演及 14 位大师。一次真实创作调用返回“no final response”，所以调用验收失败。项目内版本副本切换及回滚模拟通过；VPS 未连接或验收。
- 版本报告：Codex 已安装标记、Plugin 本地包、本机 Hermes active 指针均报 0.2.0；ChatGPT 真实安装与 Hermes 真实调用未通过，因此不能说三平台正式版本一致。
- 私有 Plugin：用户确认研究包的私有上传权限后，Plugin Creator 已保存个人私有 0.2.0；回读 15 个顶层 Skill。未完成桌面、网页、手机端安装和调用。

## 发布边界

- 14 位研究包共有 127 条方法；审计为 50 条 `PARTIAL/LIMITED`、77 条 `UNVERIFIED/SANDBOX`，未提升可信度。
- 用户已明确确认 14 份原研究包及摘录可上传到自己的私有 GitHub 仓库和私有 ChatGPT Plugin。提交白名单只含构建所需 16 个顶层研究文件，排除展开副本、影片项目、媒体和构建产物；暂存内容的常见密钥特征扫描无发现。
- GitHub Actions 验证与标签发布工作流已推送；连接器尚不能读取新仓库，实际 Actions 结果待确认。独立只读克隆的首次本地 CI 复演中，完整单元测试通过，`validate_system.py` 发现远程缺少旧 `SYSTEM_SMOKE_TEST.md` 和 `fixtures/walter-murch.md`，没有降低校验要求；两文件已检查并加入下一次提交。`v0.2.0` 标签、私有 Release 及 VPS Hermes 部署未执行。
- ChatGPT 桌面、网页、手机端、Project 内 Plugin 调用及 GitHub 应用私库读取均未实测；不能把本地包或模板当作这些验收结果。
- 《红线》原稿未提供；没有真实媒体或成片验收。
