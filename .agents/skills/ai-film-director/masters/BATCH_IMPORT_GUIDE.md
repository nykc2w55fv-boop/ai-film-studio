# 大师研究包批量导入

1. 本轮 14 位资料位于只读 `14位电影大师/`。新资料由 ChatGPT 按 `MASTER_DISTILLATION_TEMPLATE.md` 交付；原包不由程序修改。
2. 待检查包放入 `03_KNOWLEDGE/master-research/ready-for-skill/`；`inbox/` 可放尚未核实的交接包，`processed/` 仅供人工归档。程序不搬移原包。
3. 旧格式 Markdown 仍可用 `python 05_AUTOMATION/scripts/import_master.py check --all` 检查；本轮 Markdown／ZIP 使用 `python 05_AUTOMATION/scripts/import_master.py assets` 查看资产清单。
4. 单包预览：`python 05_AUTOMATION/scripts/import_master.py preview --package <slug>.md`。确认生成文件和索引变更后，运行 `python 05_AUTOMATION/scripts/import_master.py import --package <slug>.md`。macOS 用 `python3`。
5. 本轮资料走 `audit` 与 `build-release` 入口，逐方法记录 `SUPPORTED`、`PARTIAL`、`UNVERIFIED` 或 `CONFLICTED`，并独立记录调用权限。已有审计记录在 `06_QA/`；用户要求优先完成系统搭建，后续不以逐人深审为日常关卡。
6. 构建后运行结构校验和 `install_runtime.py preview`，再安装、模拟升级与回滚。ChatGPT Project 需要单独上传适配包并实测，不能假设本地 Skill 自动同步。

旧导入器继续用于旧格式包；新构建器不覆盖同版本产物。安装器不删除文件，停用时重命名 Skill 入口并列出手工清理清单。
