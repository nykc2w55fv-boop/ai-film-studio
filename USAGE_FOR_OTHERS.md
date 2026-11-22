# 别人如何使用 AI Film Studio

当前公开分发版本为 [`v0.2.0`](https://github.com/nykc2w55fv-boop/ai-film-studio/releases/tag/v0.2.0)。先安装到自己使用的智能体，再发送下方开片话术。只发一句提示词不会让未安装的智能体自动获得 14 位大师的方法、证据审计或项目文件。GitHub 公开也不会自动给任何人的 ChatGPT 安装 Plugin。

## 用 Codex 的人：下载、安装、验证

1. 从 Release 下载 `ai-film-system-0.2.0.zip` 和同名 `.sha256` 文件。Windows 可用 `Get-FileHash ai-film-system-0.2.0.zip -Algorithm SHA256`，macOS 可用 `shasum -a 256 ai-film-system-0.2.0.zip`，Linux 可用 `sha256sum ai-film-system-0.2.0.zip`，把结果与 `.sha256` 文件首列比较。
2. 解压 ZIP，进入包含 `manifest.json`、`install_runtime.py` 和 `skills/` 的目录。安装需要 Python 3.11 或更新版本。先在此目录预览：Windows 运行 `python install_runtime.py preview --release .`；macOS/Linux 运行 `python3 install_runtime.py preview --release .`。检查输出是 0.2.0、15 个 Skill，且目标是自己的用户级 `~/.agents/skills`。
3. 确认预览后，在同一目录运行 `python install_runtime.py install --release .`（macOS/Linux 用 `python3`）。安装器会为已有版本保存备份；不要手动覆盖已有同名 Skill。重启 Codex，在新聊天中使用下方话术，并要求报告版本、方法 ID、证据状态与调用权限。

## 用 ChatGPT 的人：建立自己的 Plugin

1. 从同一 Release 下载 `ai-film-studio-plugin-0.2.0.zip` 与同名 `.sha256`，按上面的方式校验 ZIP。
2. 只有在自己的 ChatGPT 账户支持 **Plugin Creator／创建 Plugin** 时，才能走这条路径。将 ZIP 上传到自己与 Plugin Creator 的对话，发送：“请从我上传的 `ai-film-studio-plugin-0.2.0.zip` 创建并保存一个我自己的私有 Skills-only Plugin；保留内嵌总导演和 14 位大师 Skill。完成后告诉我安装页面。”按该账户实际页面完成安装。
3. 在新聊天或单部影片的 Project 中**选用自己安装的 AI Film Studio Plugin**，发送下方话术；核对答复明确写出 `0.2.0`、方法 ID、证据状态和调用权限。若账户没有 Plugin Creator 或安装入口，此路径目前无法直接使用；公开 GitHub 链接不能代替安装。

你的现有个人 Plugin 是 `USER/PRIVATE`。别人不能直接选择你的实例；公开 Release 提供的是让合适账户自行安装的包。ChatGPT 的桌面、网页和手机端需各自确认 Plugin 可选用，不能把一个客户端的结果当成全平台通过。

## 可直接复制的开片话术

在已安装本系统的 Codex 中调用 `ai-film-director` Skill；在已安装 AI Film Studio Plugin 的 ChatGPT 客户端中先选用该 Plugin，再发送：

> 请使用 AI Film Studio 的 `ai-film-director` 总导演，报告当前 Skill 版本，并按 AUTO 路由启动一部短片的前期创作。项目代号：[英文小写]；类型：[填写]；目标时长与画幅：[填写]；故事原稿或一句话构思：[填写]；受众与发布场景：[填写]；预算、工具、时间和版权限制：[填写]；已经确认的决定：[无或逐条填写]。请先判断阶段、岗位和信息缺口，给出不超过三种故事方向。调用大师方法时列出方法 ID、证据状态、调用权限和适用边界。到“故事方向”确认点停下，等待我选择。不要把未确认创意写入正式项目文件，也不要声称已生成媒体。若你不能读取我的项目文件或未加载 Skill，请直接说明。

已有影片项目时，把项目代号、当前阶段、六个正式事实文件的版本、已确认决策及未确认问题一并提供。聊天记录和 Plugin 版本不等于项目文件已同步。

## 确认后的交接话术

> 我确认了上述第 [编号] 个故事方向。请依据 `HANDOFF_TEMPLATE.json` 输出标准化交接 JSON，写明项目标识、来源、版本、变更内容和确认状态。若你不知道正式文件的基准 SHA-256，请不要猜测，明确标出需由 Codex 取得。不要直接覆盖正式项目文件；先交给 Codex 预览冲突，再由操作者导入。

## 平台边界

- **Codex**：安装系统包后可调用用户级 Skill、创建项目、检查和导入交接。项目文件保存在使用者自己的目录。
- **ChatGPT**：每部影片使用独立 Project，项目指令见 `CHATGPT_PROJECT_INIT.md`；Plugin 无法自动读取或修改使用者电脑上的正式文件。
- **Hermes**：Release 提供版本化部署脚本和 `external_dirs` 示例；本机已验证 Skill 发现，真实模型调用仍未通过，VPS 未验收。不要向别人承诺 Hermes 已能稳定执行。

正式影片记录保存在各自项目目录的六个事实文件中。不要把私人的剧本、媒体、密钥或未经授权素材提交到本仓库。
