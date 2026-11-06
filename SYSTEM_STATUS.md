# 系统状态

- 当前本地候选版：`0.2.0`；最后核对：2026-11-06。
- 已初始化本地 Git `main` 并配置私有仓库 SSH 远程；尚无提交、标签或推送。用户已手动创建目标私有仓库。

## 本轮已实现并验证

- 保留总导演、14 位大师独立 Skill、11 个岗位、16 阶段、四个确认点及 127 条方法；沿用审计记录中的 50 条 `PARTIAL/LIMITED`、77 条 `UNVERIFIED/SANDBOX`，没有升级证据状态。
- 0.2.0 发布包与 ZIP 已本地构建；用户级 `~/.agents/skills` 安装 0.2.0，升级前备份了 0.1.4。独立系统临时目录完成 0.1.4 → 0.2.0 → 0.1.4 回滚。
- 新 Codex CLI 会话在项目外目录读取用户级 0.2.0，按 AUTO 路由到导演岗位和 `alfred-hitchcock-M01`，正确保留 `UNVERIFIED/SANDBOX` 边界；没有写入项目或生成媒体。
- 标准交接支持待确认阻断、基准哈希冲突、重复导入、六文件快照、导入后 `check/reconcile` 和回滚；相关单元测试通过。单片 ChatGPT Project 精简初始化模板已建立。
- Skills-only Plugin 本地包包含 15 个 Skill，标记仅供 ChatGPT 使用；尚未安装到 ChatGPT 客户端。
- 本机 Hermes v0.16.0 使用官方 `skills.external_dirs` 发现了 15 个 Skill；0.1.4/0.2.0 版本副本选择与回滚在项目内模拟通过。一次本机 Hermes 真实创作调用未返回最终答复，需排查模型连接或运行日志。
- 用户确认 14 份研究包可用于自己的私有 GitHub 与私有 ChatGPT Plugin。待提交文件含构建实际读取的 16 个顶层研究文件；密钥特征扫描无发现，展开副本与媒体仍排除。
- 两把本机私钥因生成时的 PowerShell 引号问题意外带口令；Windows 自带 ssh-agent 禁用。Git 自带用户态 ssh-agent 已临时解锁两把密钥，分别通过 `git ls-remote` 实际读取仓库。自动审批拒绝永久移除私钥口令，未绕过；提交与推送仍需验证。
- 私有 ChatGPT Plugin 0.2.0 已保存到个人账户，回读确认 15 个顶层 Skill；客户端安装与调用仍未验收。

## 发布与客户端缺口

- 用户已确认研究包的两处私有上传授权；当前仅 Plugin 已保存到个人账户，GitHub 待提交、推送、Actions 和私有 Release 验证。原始影片项目、媒体及 `dist/` 仍由 `.gitignore` 排除。
- ChatGPT GitHub 应用尚未授权新私有仓库，连接器读取目标仓库返回 404；该应用的读取权限不能代替 Git 提交与推送。
- ChatGPT Plugin 桌面、网页、手机端和单片 Project 内真实调用尚未验收；VPS Hermes 地址与访问权限未提供，VPS 网络、密钥和调用均未验收。
- 项目内 `.agents/skills/ai-film-director` 源入口与用户级安装同名；项目外 Codex 调用通过，但项目内自动发现优先级与重复入口仍需确认。
- 《红线》原稿未提供；无真实媒体或成片验收。macOS/Linux 客户端发现和部署仍需目标机器验证。

详细旧版证据见 `06_QA/INTEGRATION_ACCEPTANCE_20261106.md`；本轮记录见 `06_QA/ACCEPTANCE_0.2.0_20261106.md`。
