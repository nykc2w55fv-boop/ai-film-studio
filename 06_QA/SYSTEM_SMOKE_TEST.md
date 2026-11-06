# 系统冒烟测试

本记录只包含本地结构检查与合成模拟；不等同于 ChatGPT Project、Codex 自动触发或真实媒体引擎验收。实际运行结果见下表；若某项尚未运行，必须写“未运行”。

| 场景 | 输入与预期 | 实际结果 |
| --- | --- | --- |
| 历史人物故事 | 历史人物、年代和待核事实；应选 research、screenwriting、directing，并在视觉阶段加入 art-direction/cinematography | **通过文档模拟**：路由表包含对应触发、岗位、事实边界与视觉阶段；未在真实 Codex 客户端验证自动触发。 |
| 佛学故事 | 原典名称与现代改编目标；原典核查应独立于创作改编 | **通过文档模拟**：路由与题材工作流分别要求原典核查、版本说明和创作改编标记；未做真实原典核查。 |
| 20 镜头短片 | S001–S020 按约 5—8 镜头分批；编号稳定、版本与连续性进入项目状态 | **通过规则模拟**：B01=S001–S006、B02=S007–S012、B03=S013–S018、B04=S019–S020；编号无遗漏，批次规则包含版本、连续性和三种产物状态。未生成媒体。 |
| 完整研究包 | 仅用合成 fixture 校验和预览六个 Skill 文件，正式导入应拒绝 simulation | **通过结构模拟**：`walter-murch.md` 标明 `simulation`，校验通过，内存预览六个 Skill 文件与三个同步文档；正式导入拒绝，目标目录不存在。此文件不代表真实大师研究。 |

## 结构验收

- 必需路径、UTF-8、文件名、Python 语法、YAML frontmatter、三个 CSV 列名：**通过本地结构校验**，共检查 57 个必需文件、3 个接收目录、3 份 CSV 表头。
- 总导演引用与工作流一致性：**通过静态核对与场景模拟**；真实 Skill 自动触发未运行。
- ChatGPT 交接文件可独立阅读：**已人工抽查** Project 指令、Starter Pack、方法库和启动提示词的独立说明；未在 ChatGPT Project 中上传试用。
- 真实客户端调用、研究来源真实性、外部媒体生成与播放：未运行，不在本地模拟范围内。

## 命令与日志

在项目根目录运行（2026-11-06）：

1. `python -B 05_AUTOMATION/scripts/validate_system.py` → 退出码 0；`PASS: local structure, encoding, Python syntax, frontmatter and template columns`。
2. `python -B 05_AUTOMATION/scripts/import_master.py check --all` → 退出码 0；ready 目录无真实研究包。
3. `python -B 05_AUTOMATION/scripts/import_master.py check --package walter-murch.md --fixture` → 退出码 0；仅结构合格。
4. `python -B 05_AUTOMATION/scripts/import_master.py preview --package walter-murch.md --fixture` → 退出码 0；列出六个 Skill 文件和三个同步文档，未写文件。
5. 用一次性内存测试检查历史/佛学路由文本、16 阶段、20 镜头编号、生成内容预览、`simulation` 禁止导入和 `../` 路径拒绝 → 退出码 0；无正式 Skill 目录。
6. `python -B 05_AUTOMATION/scripts/import_master.py import --package walter-murch.md --fixture` → 预期退出码 1；命令行拒绝测试资料正式导入。

本地静态和模拟验收通过；真实客户端、来源真实性与成片验收仍待后续实际执行。
