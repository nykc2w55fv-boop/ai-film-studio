# 独立大师 Skill 规格

合格研究包一人一份，输出到 `.agents/skills/master-<slug>/`：

```text
SKILL.md
references/methods.md
references/evidence-ledger.md
references/case-studies.md
references/limitations.md
evals/test-cases.md
```

`SKILL.md` 必须含有效 YAML frontmatter（`name`、面向任务的 `description`），仅写适用任务、读取顺序和使用边界；详细方法与来源在 references，测试在 evals。方法文本保留“本人明确表达”和“研究者归纳”的区分，证据路径指向原包。索引、总导演路由与 ChatGPT 方法库需要同步更新。

不合格、`provisional` 或 `simulation` 包不得生成正式 Skill；既有目标目录不得覆盖。程序只做结构转换，人工仍须核实来源和权限。
