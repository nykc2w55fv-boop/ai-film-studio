# AI-Film-Studio

本项目构建可独立安装的 AI 短片前期生产系统。当前版本为 0.2.0 发布候选版。14 位只读研究原包位于 `14位电影大师/`；构建结果位于 `dist/`；运行时总导演与各大师 Skill 安装到用户级 `~/.agents/skills/`。GitHub 私有仓库已作为统一知识源，`v0.2.0` 标签及私有 Release 仍待发布验收。单部影片的六个事实文件始终是该片正式记录。

## 从哪里开始

1. 在项目目录运行下述检查与构建命令；安装前先运行 `preview`。系统 Python 3.11 和 Codex 是宿主前提。
2. 在任意工作目录用已安装的 `ai-film-director` Skill 开始前期创作。新项目使用 `project_runtime.py init --slug <英文代号>`，在当前目录建立 `01_PROJECTS/<slug>/` 及六个统一事实文件。
3. 总导演默认 AUTO，按问题读取必要岗位和方法。四个确认点锁定故事方向、剧本、视觉方向与最终成片。没有真实媒体文件和验收依据时只交付规划或提示词。
4. ChatGPT 通过内嵌 15 个 Skill 的私有 Plugin 工作；每部影片按 `CHATGPT_PROJECT_INIT.md` 建独立 Project，确认后用 `HANDOFF_TEMPLATE.json` 交接。Plugin 不直接同步项目文件。网页、桌面与手机端分别实测。

## 目录

- `.agents/skills/ai-film-director/`：总导演入口、路由、岗位、工作流、大师索引和质量规则。
- `01_PROJECTS/`：实际短片项目。每个项目单独保存版本和批次。
- `02_PROJECT_TEMPLATES/`：从需求到交付的项目文件模板。
- `14位电影大师/`、`03_KNOWLEDGE/`：只读原始资料与新增研究包入口。
- `04_ASSET_LIBRARY/`：经过来源登记、可复用的跨项目素材。
- `05_AUTOMATION/scripts/`：Python 标准库构建、审计、安装、路由和项目连续性脚本。
- `dist/`：版本化安装包、ZIP 和本地模拟验收产物。
- `deployment/`：私有仓库权限、Plugin、Hermes 部署及回滚步骤。
- `06_QA/`：系统验收记录与合成测试资料。
- `07_ARCHIVE/`：经人工决定归档的项目，不自动移动或删除。

## 本地命令

需要 Python 3.11 或更新版本（仅标准库）。Windows 使用 `python`，macOS 使用 `python3`；以下命令在 macOS 替换解释器名称即可。

```text
python 05_AUTOMATION/scripts/validate_system.py
python 05_AUTOMATION/scripts/import_master.py assets
python 05_AUTOMATION/scripts/build_release.py --version <新版本> --audit 06_QA/evidence-audit-20261106.json
python 05_AUTOMATION/scripts/install_runtime.py preview --release dist/ai-film-system-<版本>
python 05_AUTOMATION/scripts/install_runtime.py install --release dist/ai-film-system-<版本>
python 05_AUTOMATION/scripts/export_plugin.py --release dist/ai-film-system-<版本>
python 05_AUTOMATION/scripts/version_report.py --release dist/ai-film-system-<版本> --plugin dist/ai-film-studio-plugin-<版本>
```

审计刷新只访问研究包列出的公开 URL：`python 05_AUTOMATION/scripts/evidence_audit.py --online --max-urls 100 --output 06_QA/<新文件名>.json`。证据状态与调用权限按方法记录；未核实方法可在受限范围内辅助构思。旧式 Markdown 包仍可走 `import_master.py check/preview/import`，不与本轮 14 人构建混用。

安装器的 `rollback --backup <zip>` 从快照恢复；`disable` 重命名全部包内 Skill 入口并输出手工清理清单，不删除文件。安装、升级和回滚先在独立目标目录预演。运行项目事实源可用 `project_runtime.py check --project <目录>` 与 `reconcile --project <目录> --apply` 检查和记录下游影响。

先运行 `handoff.py bases --project <项目目录>` 取得当前正式文件的基准 SHA-256。ChatGPT 确认后的交接再用 `handoff.py preview --project <项目目录> --handoff <文件>` 查冲突，由操作者运行 `handoff.py import --project <项目目录> --handoff <文件> --confirmed-by-operator`。重复导入只报告已处理；每次实际改写前保存六文件快照。回滚用 `handoff.py rollback --project <项目目录> --snapshot <history/...>`。Hermes 本机与 VPS 的独立部署见 `deployment/README.md`。

## 边界

`SYSTEM_STATUS.md` 区分已构建、模拟验收与真实客户端调用；`PORTABILITY.md` 记录迁移路径。Skill 版本一致不表示影片项目文件已自动同步。《红线》原稿未提供时，不能声称完成该项目端到端验收。
