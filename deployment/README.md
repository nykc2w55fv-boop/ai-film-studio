# 私有仓库、Plugin 与 Hermes 部署

## 权限与正式发布

`main` 是开发分支。用户已确认 14 份原包可上传到自己的私有 GitHub 仓库和私有 ChatGPT Plugin；只纳入构建实际引用的 16 个顶层研究文件，排除展开副本、影片项目和媒体素材。只有敏感信息检查、仓库权限、完整回归和目标客户端验收通过后，才创建 `v0.2.0` 标签与私有 Release。`VERSION.json`、发布包 `manifest.json` 和 ZIP 的 SHA-256 必须对应。Actions 会从私有仓库重建发布包，但不能代替桌面、手机和 VPS 的真实调用。

Codex 使用仓库专用可写 SSH Deploy key；私钥仅在本机 SSH 目录，不能提交或贴入聊天。第一次克隆后用 `git remote -v`、`git fetch` 验证读权限；通过无敏感内容的小提交和 `git push origin main` 验证写权限，记录提交 SHA。回滚用既有安装器的备份 ZIP，仓库回滚使用经审查的恢复提交或选择旧标签，不强推。

## ChatGPT

`export_plugin.py` 从同一版本发布包生成 Agent Plugins 1.0 的 Skills-only Plugin，内含总导演与 14 位大师 Skill，并用 `policy.products: [CHAT]` 限定插件 Skill 在 ChatGPT 端，避免与 Codex 用户级 Skill 同名发现。Plugin 运行不实时下载 GitHub；需单独更新已安装 Plugin，并在桌面、网页、手机端及单片 Project 各做真实调用。`plugin.json` 版本只证明包版本，不证明客户端已更新。

个人账户可通过 Plugin Creator 保存私有包；不假设具备工作区管理员的 GitHub Marketplace 自动同步。ChatGPT GitHub 应用的授权另走 **Settings → Plugins → GitHub → Manage repositories**（界面名称以实际显示为准），在 GitHub 中为 ChatGPT 应用选择该私有仓库。该应用只提供获授权仓库的读取、搜索和引用；不能代替本机 Git 的提交与推送。新仓库授权后可能需等待搜索索引刷新。当前连接器对目标仓库返回 404，尚未验证授权。

## Hermes 本机与 VPS

官方机制为在 Hermes 配置 `skills.external_dirs` 中添加 `${AI_FILM_SKILLS_DIR}`。本机配置路径以 `hermes config path` 为准，VPS 在其实际用户配置下单独检查。将 `deployment/hermes-local.example.yaml` 或 `hermes-vps.example.yaml` 的 `skills` 项合并进现有配置，保留原有内容。运行时环境变量必须指向 `releases/<version>/skills` 的绝对路径。

```text
python 05_AUTOMATION/scripts/hermes_release.py stage --root <Hermes专用目录> --release dist/ai-film-system-0.2.0
python 05_AUTOMATION/scripts/hermes_release.py select --root <Hermes专用目录> --version 0.2.0
python 05_AUTOMATION/scripts/hermes_release.py run --root <Hermes专用目录> -- hermes skills list
```

`stage` 复制并校验完整发布包；旧版本保留。`select` 只改 `active.json`，先前指针备份到 `history/`，回滚时 `select --version <旧版本>`；重新启动 Hermes 服务后再验证发现、路由和真实调用。文件只读属性防误改，不是同账户的安全边界；正式 VPS 部署应由独立只读 Deploy key 克隆私有仓库，以只读挂载或独立服务账户保护 Skill 副本。VPS 必须单独验证 DNS、GitHub SSH 认证、`hermes --version`、`hermes skills list` 与真实任务。

更新顺序：GitHub 私有 Release 与 SHA-256 核对 → Codex 从指定版本更新本地仓库和用户级 Skill → ChatGPT Plugin Creator 更新同版本包并在客户端复测 → Hermes 本机与 VPS 分别 stage/select/重启/复测。三方分别读版本，不推断影片事实文件已同步。
