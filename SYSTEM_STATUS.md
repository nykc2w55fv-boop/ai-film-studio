# 系统状态

- 当前发布候选版：`0.2.0`；最后核对：2026-11-07。
- 本地 Git `main` 已推送到用户手动创建的私有仓库；当前远程提交为 `30e8080`。尚无 `v0.2.0` 标签或 Release。

## 本轮已实现并验证

- 保留总导演、14 位大师独立 Skill、11 个岗位、16 阶段、四个确认点及 127 条方法；沿用审计记录中的 50 条 `PARTIAL/LIMITED`、77 条 `UNVERIFIED/SANDBOX`，没有升级证据状态。
- 0.2.0 发布包与 ZIP 已本地构建；用户级 `~/.agents/skills` 安装 0.2.0，升级前备份了 0.1.4。独立系统临时目录完成 0.1.4 → 0.2.0 → 0.1.4 回滚。
- 新 Codex CLI 会话在项目外目录读取用户级 0.2.0，按 AUTO 路由到导演岗位和 `alfred-hitchcock-M01`，正确保留 `UNVERIFIED/SANDBOX` 边界；没有写入项目或生成媒体。
- 标准交接支持待确认阻断、基准哈希冲突、重复导入、六文件快照、导入后 `check/reconcile` 和回滚；相关单元测试通过。单片 ChatGPT Project 精简初始化模板已建立。
- Skills-only Plugin 本地包包含 15 个 Skill，标记仅供 ChatGPT 使用；个人私有 Plugin 已安装，用户提供的网页端普通聊天截图证明 0.2.0 总导演与大师方法调用。
- 本机 Hermes v0.16.0 在版本包装器设置 `skills.external_dirs` 环境后发现 15 个 Skill；2026-11-07 修正了本机 0.2.0 `active.json` 相对路径，`report` 与包装器下发现均通过。直接运行 `hermes skills list` 仍为 0 个本地 Skill，故普通启动尚未完成环境变量接入。真实 `hermes -z` 调用再次返回 `no final response was produced`，调用验收失败；需排查模型提供方或 Hermes 运行环境。
- 用户确认 14 份研究包可用于自己的私有 GitHub 与私有 ChatGPT Plugin。已提交文件含构建实际读取的 16 个顶层研究文件；密钥特征扫描无发现，展开副本与媒体仍排除。
- 两把本机私钥因生成时的 PowerShell 引号问题意外带口令；Windows 自带 ssh-agent 禁用。Git 自带用户态 ssh-agent 已临时解锁两把密钥，分别通过 `git ls-remote` 读取仓库；Codex 可写密钥已实际推送，Hermes 只读密钥已实际克隆。自动审批拒绝永久移除私钥口令，未绕过。
- 私有 ChatGPT Plugin 0.2.0 已保存到个人账户，回读确认 15 个顶层 Skill。用户确认已安装且可选用；2026-11-07 网页端普通聊天截图显示版本、方法 ID、证据状态和调用权限。截图引用了旧的 Codex 0.1.4 状态，不能作为本机版本证据。
- Hermes 只读 Deploy key 已从私有仓库 `main` 克隆源码到独立系统临时目录。补齐两份旧 QA 文件并推送 `30e8080` 后，重新从远程只读克隆，完整单元测试、结构校验、发布包构建、Plugin 导出与两个 ZIP 的 SHA-256 校验均通过；这属于远程源码的本地复演，不是 GitHub Actions 运行结果。

## 发布与客户端缺口

- 用户已确认研究包的两处私有上传授权；Plugin 已保存到个人账户，GitHub `main` 的提交和推送已通过。用户在 GitHub 页面确认 `30e8080` 的 “Verify safe source” 为绿色通过，作业日志尚未读取；私有 Release 未创建。原始影片项目、媒体及 `dist/` 仍由 `.gitignore` 排除。
- 当前 GitHub 连接器已能读取目标私有仓库元数据，确认 `visibility=private`、默认分支 `main`；不能用这项读取证明 ChatGPT Project 的 GitHub 应用调用或 Git 推送。
- ChatGPT Plugin 网页端普通聊天真实调用已由用户截图验收；Codex 桌面客户端内 ChatGPT 模式、手机端和单片 Project 内调用尚未分别验收。VPS Hermes 网络、密钥和调用均未验收。
- 项目内 `.agents/skills/ai-film-director` 源入口与用户级安装同名；项目外 Codex 调用通过，但项目内自动发现优先级与重复入口仍需确认。
- 《红线》原稿未提供；无真实媒体或成片验收。macOS/Linux 客户端发现和部署仍需目标机器验证。

详细旧版证据见 `06_QA/INTEGRATION_ACCEPTANCE_20261106.md`；本轮记录见 `06_QA/ACCEPTANCE_0.2.0_20261106.md`。
