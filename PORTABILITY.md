# Windows → macOS 迁移

- 当前主要环境：Windows，项目根目录由当前工作区决定。
- 未来目标环境：macOS，保持相同相对目录结构与 UTF-8/LF 文件。
- Windows 入口：在项目根目录运行 `python 05_AUTOMATION/scripts/validate_system.py`；构建、安装、交接、Plugin 导出及 Hermes 版本命令见 `README.md`、`deployment/README.md`。
- macOS/Linux 预留入口：将 README 中的 `python` 换成 `python3`，使用同一批标准库脚本；Codex 安装位置由 `Path.home()` 定位到 `~/.agents/skills/`。Hermes 的 `AI_FILM_SKILLS_DIR` 指向所选发布副本的绝对路径。
- 核心跨平台逻辑：`05_AUTOMATION/scripts/` 的 Python 3.11 标准库脚本；交接通过 SHA-256 基准和项目相对路径定位文件。运行包通过包内相对路径定位 Skill、references、配置和模板。项目输出默认相对当前工作目录。
- Windows 专属内容：无脚本、注册表、COM 或服务依赖。工作区所在盘符仅用于本机交互，不写入自动化逻辑。
- 迁移风险：macOS/Linux 文件名可能区分大小写；ZIP 内文件名、Skill 引用与模板大小写需逐一匹配。`hermes_release.py` 的只读文件属性不能替代独立服务账户或只读挂载；Hermes 配置及服务环境变量须按目标机器重设。Codex 用户级 Skill 发现、Plugin 客户端调用与 Hermes VPS 真实调用须在目标环境分别验收；媒体工具与中文字体另行选型。
- 未来迁移步骤：复制 Git 工作区或版本化 ZIP；在 macOS/Linux 确认 Python 3.11、Codex 与 Hermes；运行结构校验和安装包 `preview`；安装到用户级 Skill 位置；用独立目录实测总导演、交接导入与回滚；为 Hermes 配置 `skills.external_dirs` 与只读发布副本；最后分别验证 ChatGPT 客户端。私钥不能从 Windows 文档中直接复制到新机器，应单独安全配置。
- 最近一次迁移影响记录（2026-11-06，0.2.0）：新增标准库交接、Plugin 导出、Hermes 版本副本和报告脚本；未在项目代码中新增 Windows 盘符、Windows 专属脚本或平台依赖。本机 SSH 与 Hermes 安装操作使用了 Windows 环境，但不作为跨平台入口；macOS/Linux 需分别配置 Git SSH、Hermes 环境变量和文件权限。
