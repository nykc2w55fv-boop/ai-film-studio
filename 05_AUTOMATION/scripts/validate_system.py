"""Read-only structural validation for AI-Film-Studio v1.0."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIRECTOR = Path(".agents/skills/ai-film-director")
RAW_RESEARCH = "14位电影大师"
REQUIRED = [
    "README.md", "AGENTS.md", "PORTABILITY.md", "SYSTEM_STATUS.md",
    "VERSION.json", "CHANGELOG.md", ".gitignore", ".env.example",
    "HANDOFF_TEMPLATE.json", "CHATGPT_PROJECT_INIT.md", "deployment/README.md",
    "deployment/hermes-local.example.yaml", "deployment/hermes-vps.example.yaml",
    ".github/workflows/verify.yml",
    ".github/workflows/release.yml",
    "CHATGPT_PROJECT_INSTRUCTIONS.md", "CHATGPT_STARTER_PACK.md",
    "CHATGPT_METHODS_LIBRARY.md", "PRODUCTION_START_PROMPT.md",
    f"{DIRECTOR}/SKILL.md",
    *[f"{DIRECTOR}/routing/{name}.md" for name in
      ("ROUTING", "PRODUCTION_WORKFLOW", "DECISION_POLICY", "MASTER_ROUTING")],
    f"{DIRECTOR}/specialists/SPECIALIST_ROLES.md",
    *[f"{DIRECTOR}/specialists/{name}/ROLE.md" for name in
      ("research", "screenwriting", "directing", "cinematography", "storyboard",
       "art-direction", "sound-design", "editing", "continuity", "production",
       "visual-effects")],
    f"{DIRECTOR}/specialists/DOMAIN_STAGE_MAP.md",
    *[f"{DIRECTOR}/masters/{name}.md" for name in
      ("MASTER_INDEX", "MASTER_QUEUE", "MASTER_DISTILLATION_TEMPLATE",
       "MASTER_PACKAGE_SCHEMA", "MASTER_SKILL_SPEC", "BATCH_IMPORT_GUIDE")],
    f"{DIRECTOR}/workflows/WORKFLOW_OVERVIEW.md",
    *[f"{DIRECTOR}/workflows/{name}/WORKFLOW.md" for name in
      ("historical-film", "character-film", "documentary", "buddhist-story", "short-video")],
    *[f"02_PROJECT_TEMPLATES/{section}/{name}" for section, name in
      (("00_admin", "PROJECT_STATE.md"), ("00_admin", "CREATIVE_BRIEF.md"),
       ("01_research", "RESEARCH_LOG.md"), ("02_story", "STORY_BIBLE.md"),
       ("03_script", "SCREENPLAY.md"), ("04_visual-bible", "VISUAL_BIBLE.md"),
       ("05_storyboards", "STORYBOARD_PLAN.md"), ("06_shotlists", "SHOTLIST.csv"),
       ("07_assets", "ASSET_MANIFEST.csv"), ("08_audio", "AUDIO_CUES.csv"),
       ("09_edit", "EDIT_PLAN.md"), ("10_quality-control", "QA_REPORT.md"),
       ("11_output", "DELIVERY_MANIFEST.md"))],
    *[f"{DIRECTOR}/quality-control/{name}.md" for name in
      ("QUALITY_GATE", "CONTINUITY_CHECKLIST", "FACTUALITY_AND_COPYRIGHT",
       "SKILL_VALIDATION_CHECKLIST")],
    "06_QA/SYSTEM_SMOKE_TEST.md", "06_QA/fixtures/walter-murch.md",
    "05_AUTOMATION/scripts/import_master.py", "05_AUTOMATION/scripts/validate_system.py",
    "05_AUTOMATION/scripts/master_assets.py", "05_AUTOMATION/scripts/evidence_audit.py",
    "05_AUTOMATION/scripts/build_release.py", "05_AUTOMATION/scripts/install_runtime.py",
    "05_AUTOMATION/scripts/project_runtime.py", "05_AUTOMATION/scripts/route_methods.py",
    "05_AUTOMATION/scripts/handoff.py", "05_AUTOMATION/scripts/export_plugin.py",
    "05_AUTOMATION/scripts/hermes_release.py", "05_AUTOMATION/scripts/version_report.py",
]
DIRECTORIES = [
    "03_KNOWLEDGE/master-research/inbox",
    "03_KNOWLEDGE/master-research/ready-for-skill",
    "03_KNOWLEDGE/master-research/processed",
]
CSV_COLUMNS = {
    "02_PROJECT_TEMPLATES/06_shotlists/SHOTLIST.csv":
        ("镜头编号", "场景编号", "时长秒", "人物编号", "地点编号", "景别", "角度", "运镜",
         "画面动作", "对白", "视觉提示词", "参考素材", "连续性要求", "制作状态", "验收状态"),
    "02_PROJECT_TEMPLATES/07_assets/ASSET_MANIFEST.csv":
        ("素材编号", "类型", "名称", "版本", "文件路径", "关联场景", "关联镜头",
         "人物或场景编号", "连续性要求", "制作状态", "验收状态"),
    "02_PROJECT_TEMPLATES/08_audio/AUDIO_CUES.csv":
        ("音频编号", "类型", "关联场景", "关联镜头", "开始时间秒", "结束时间秒",
         "内容", "生成要求", "音量优先级", "制作状态"),
}


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty file: {rel}")
    for rel in DIRECTORIES:
        if not (ROOT / rel).is_dir():
            errors.append(f"missing directory: {rel}")
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.relative_to(ROOT).parts[0] == RAW_RESEARCH:
            continue  # Existing read-only user research is checked by master_assets.
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", rel):
            errors.append(f"non-English path: {rel}")
        if path.suffix in {".md", ".csv", ".py"}:
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeError, OSError) as exc:
                errors.append(f"cannot read UTF-8: {rel}: {exc}")
                continue
            if not text.strip():
                errors.append(f"no substantive content: {rel}")
            if path.suffix == ".py":
                try:
                    compile(text, rel, "exec")
                except SyntaxError as exc:
                    errors.append(f"Python syntax error: {rel}: {exc}")
    for path in (ROOT / ".agents/skills").glob("*/SKILL.md"):
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
        if not match or not re.search(r"^name: .+", match.group(1), re.MULTILINE) or not re.search(
            r"^description: .+", match.group(1), re.MULTILINE
        ):
            errors.append(f"invalid Skill frontmatter: {path.relative_to(ROOT)}")
    for rel, needed in CSV_COLUMNS.items():
        path = ROOT / rel
        if not path.is_file():
            continue
        with path.open(encoding="utf-8", newline="") as stream:
            header = next(csv.reader(stream), [])
        missing = set(needed) - set(header)
        if missing or len(header) != len(set(header)):
            errors.append(f"CSV columns invalid: {rel}; missing={sorted(missing)}")
    index = ROOT / DIRECTOR / "masters/MASTER_INDEX.md"
    if index.is_file():
        rows = [line for line in index.read_text(encoding="utf-8").splitlines()
                if line.startswith("| ") and not line.startswith(("| slug ", "| ---"))]
        candidates = [line.split("|")[1].strip() for line in rows]
        if len(candidates) != 14 or len(set(candidates)) != 14:
            errors.append("MASTER_INDEX must list 14 distinct candidates")
        routes_text = (ROOT / DIRECTOR / "routing/MASTER_ROUTING.md").read_text(encoding="utf-8")
        methods_text = (ROOT / "CHATGPT_METHODS_LIBRARY.md").read_text(encoding="utf-8")
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) != 9 or cells[6] not in {"pending", "provisional", "verified"}:
                errors.append(f"invalid candidate row: {row}")
                continue
            slug, state, source_rel, skill_rel = cells[0], cells[6], cells[7], cells[8]
            if state == "provisional":
                source_path = ROOT / source_rel
                if source_rel == "—" or not source_path.is_file() or not source_path.resolve().is_relative_to(ROOT.resolve()):
                    errors.append(f"provisional candidate has invalid source: {slug}")
            if state != "verified":
                if skill_rel != "—":
                    errors.append(f"non-verified candidate has Skill path: {slug}")
                continue
            expected_skill = f".agents/skills/master-{slug}"
            safe_source = (
                bool(re.fullmatch(r"[A-Za-z0-9._/-]+", source_rel))
                and not Path(source_rel).is_absolute()
                and ".." not in Path(source_rel).parts
            )
            if skill_rel != expected_skill or not safe_source or not (ROOT / source_rel).is_file():
                errors.append(f"verified candidate has invalid source or Skill path: {slug}")
            for part in ("SKILL.md", "references/methods.md", "references/evidence-ledger.md",
                         "references/case-studies.md", "references/limitations.md", "evals/test-cases.md"):
                if not (ROOT / expected_skill / part).is_file():
                    errors.append(f"master Skill file missing: {slug}/{part}")
            if f"| {slug} |" not in routes_text or f"| {slug} |" not in methods_text:
                errors.append(f"master route or ChatGPT methods missing: {slug}")
    for rel in (
        "routing/ROUTING.md", "routing/PRODUCTION_WORKFLOW.md", "routing/DECISION_POLICY.md",
        "routing/MASTER_ROUTING.md", "masters/MASTER_INDEX.md",
        "quality-control/QUALITY_GATE.md", "workflows/WORKFLOW_OVERVIEW.md",
    ):
        if not (ROOT / DIRECTOR / rel).is_file():
            errors.append(f"Skill reference missing: {rel}")
    try:
        from master_assets import inspect_all

        inventory = inspect_all()
        if len(inventory) != 14:
            errors.append("research intake must contain 14 distinct masters")
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"research intake invalid: {exc}")
    print(f"Checked {len(REQUIRED)} required files, {len(DIRECTORIES)} intake directories and 3 CSV headers")
    if errors:
        for error in errors:
            print("FAIL " + error, file=sys.stderr)
        return 1
    print("PASS: local structure, encoding, Python syntax, frontmatter and template columns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
