"""Build a self-contained, versioned Codex film system release.

The builder reads, but never edits, the original research folder. It creates
one new release directory and one ZIP. Re-running the same version refuses
to overwrite existing output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from evidence_audit import PERMISSION
from master_assets import ASSETS, ROOT, normalized_methods, read_asset, sha256, source_index


DIRECTOR = ROOT / ".agents" / "skills" / "ai-film-director"
SCRIPTS = ROOT / "05_AUTOMATION" / "scripts"
DIST = ROOT / "dist"
DESCRIPTION = {
    "lu-wei": "在影视编剧中处理人物处境、历史压力与文学改编时，按证据边界参考芦苇的方法。",
    "shinobu-hashimoto": "在群像剧本、多视角叙事和信息控制问题中，按证据边界参考桥本忍的方法。",
    "robert-towne": "在人物行为、场景因果与剧本修改问题中，按证据边界参考罗伯特·汤的方法。",
    "william-goldman": "在故事结构、小说改编和结尾取舍问题中，按证据边界参考威廉·戈德曼的方法。",
    "charlie-kaufman": "在主观叙事、高概念与非线性编剧问题中，按证据边界参考查理·考夫曼的方法。",
    "steven-spielberg": "在观众视点、延迟揭示与场面导演问题中，按证据边界参考斯皮尔伯格的方法。",
    "akira-kurosawa": "在多人群像、空间调度和动作连续性问题中，按证据边界参考黑泽明的方法。",
    "alfred-hitchcock": "在悬念、观众信息与镜头认知顺序问题中，按证据边界参考希区柯克的方法。",
    "roger-deakins": "在摄影光影、构图与视觉连续性问题中，按证据边界参考狄金斯的方法。",
    "harold-michelson": "在剧本转分镜、机位投影和空间预演问题中，按证据边界参考米歇尔森的方法。",
    "rick-carter": "在美术世界构建、空间叙事和制作设计问题中，按证据边界参考卡特的方法。",
    "thelma-schoonmaker": "在表演选择、剪辑节奏与声画关系问题中，按证据边界参考斯库梅克的方法。",
    "randy-thom": "在声音视角、声场叙事与声音前置设计问题中，按证据边界参考兰迪·汤姆的方法。",
    "john-knoll": "在视效选型、素材采集和合成协作问题中，按证据边界参考约翰·诺尔的方法。",
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _skill_text(slug: str, name: str) -> str:
    description = json.dumps(DESCRIPTION[slug], ensure_ascii=False)
    return (
        f"---\nname: master-{slug}\ndescription: {description}\n---\n\n"
        f"# {name}：证据约束的方法参考\n\n"
        "本 Skill 仅在总导演选中具体创作问题时使用。先读取 "
        "references/methods.json 中命中的方法及其 call_permission，"
        "再按 source_file 和 source_heading 读取 references/research/ 中的原文。\n\n"
        "- NORMAL：限于来源支持的范围使用，并列明证据。\n"
        "- LIMITED：可以参考方法，须标明缺口；不得称为创作者明确确认的规则。\n"
        "- SANDBOX：只供构思试验，不作事实引用，不冒充创作者观点。\n"
        "- BLOCKED：不得使用该方法；可说明冲突并改用其他方法。\n\n"
        "原包保留在构建资料库；本 Skill 附带运行时所需的研究文本副本和审计记录，"
        "不依赖构建目录。创作者本人陈述、合作者贡献和 AI 工程适配不得混称。"
        "不要模仿个人可识别风格。涉及媒体生成时，只有真实工具和真实文件才能标 generated。\n"
    )


def _audit_map(audit: dict[str, object]) -> dict[str, dict[str, object]]:
    methods = audit.get("methods", [])
    if not isinstance(methods, list):
        raise ValueError("audit methods must be an array")
    result: dict[str, dict[str, object]] = {}
    for row in methods:
        if not isinstance(row, dict) or "method_id" not in row:
            raise ValueError("invalid audit method row")
        result[str(row["method_id"])] = row
    return result


def _build_unchecked(version: str, audit: dict[str, object], output_root: Path = DIST) -> tuple[Path, Path]:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9]+)?", version):
        raise ValueError("version must be a semantic version, optionally with a simple suffix")
    release = output_root / f"ai-film-system-{version}"
    archive_path = output_root / f"ai-film-system-{version}.zip"
    checksum_path = output_root / f"ai-film-system-{version}.zip.sha256"
    if release.exists() or archive_path.exists() or checksum_path.exists():
        raise FileExistsError(f"release already exists: {version}")
    output_root.mkdir(parents=True, exist_ok=True)
    release.mkdir()
    skills = release / "skills"
    director = skills / "ai-film-director"
    shutil.copytree(DIRECTOR, director, symlinks=False)
    (director / "scripts").mkdir(parents=True, exist_ok=True)
    for name in ("project_runtime.py", "route_methods.py", "handoff.py"):
        shutil.copy2(SCRIPTS / name, director / "scripts" / name)
    shutil.copytree(ROOT / "02_PROJECT_TEMPLATES", director / "assets" / "project_templates")
    shutil.copy2(ROOT / "PRODUCTION_START_PROMPT.md", director / "assets" / "PRODUCTION_START_PROMPT.md")
    shutil.copy2(ROOT / "HANDOFF_TEMPLATE.json", director / "assets" / "HANDOFF_TEMPLATE.json")
    shutil.copy2(ROOT / "CHATGPT_PROJECT_INIT.md", director / "assets" / "CHATGPT_PROJECT_INIT.md")
    chatgpt = release / "chatgpt"
    chatgpt.mkdir()
    for name in ("CHATGPT_PROJECT_INSTRUCTIONS.md", "CHATGPT_STARTER_PACK.md", "CHATGPT_METHODS_LIBRARY.md", "PRODUCTION_START_PROMPT.md", "CHATGPT_PROJECT_INIT.md", "HANDOFF_TEMPLATE.json"):
        shutil.copy2(ROOT / name, chatgpt / name)
    audit_by_method = _audit_map(audit)
    inventory = []
    route_index = []
    chatgpt_methods = []
    for asset in ASSETS:
        files, metadata = read_asset(asset)
        methods = normalized_methods(asset, files)
        text_files = {
            name: data.decode("utf-8-sig")
            for name, data in files.items() if name.endswith(".md")
        }
        sources = source_index(text_files)
        master = skills / f"master-{asset.slug}"
        research = master / "references" / "research"
        research.mkdir(parents=True)
        for name, data in files.items():
            target = research / name
            if target.exists():
                raise ValueError(f"duplicate research file: {asset.slug}/{name}")
            target.write_bytes(data)
        normalized = []
        for method in methods:
            method_id = str(method["id"])
            verdict = audit_by_method.get(method_id)
            if verdict is None:
                raise ValueError(f"missing audit verdict: {method_id}")
            state = str(verdict.get("evidence_state"))
            permission = str(verdict.get("call_permission"))
            if state not in PERMISSION or permission not in {"NORMAL", "LIMITED", "SANDBOX", "BLOCKED"}:
                raise ValueError(f"invalid audit verdict: {method_id}")
            row = dict(method)
            row["master_slug"] = asset.slug
            row["field"] = asset.field
            row["source_file"] = f"references/research/{method['source_file']}"
            row["evidence_state"] = state
            row["call_permission"] = permission
            row["audit_rationale"] = verdict.get("rationale", "")
            normalized.append(row)
            chatgpt_row = dict(row)
            chatgpt_row["source_file"] = asset.filename
            chatgpt_methods.append(chatgpt_row)
            route_index.append({
                "id": method_id,
                "name": method["name"],
                "problem": method["problem"],
                "trigger": method["trigger"],
                "master_slug": asset.slug,
                "field": asset.field,
                "skill_path": f"../../master-{asset.slug}/SKILL.md",
                "evidence_state": state,
                "call_permission": permission,
            })
        _write(master / "SKILL.md", _skill_text(asset.slug, asset.name))
        _write(master / "references" / "methods.json", _json(normalized))
        _write(master / "references" / "evidence-sources.json", _json(sources))
        _write(master / "references" / "audit.json", _json([
            audit_by_method[str(method["id"])] for method in methods
        ]))
        _write(master / "evals" / "test-cases.md", (
            f"# {asset.name}方法验收\n\n"
            "以 references/research/ 中原包所附的测试案例或验证计划为准。"
            "本文件不声称测试已经执行；真实创作调用须另记输入、方法、理由与结果。\n"
        ))
        metadata["method_count"] = len(methods)
        metadata["runtime_skill"] = f"skills/master-{asset.slug}/SKILL.md"
        inventory.append(metadata)
    _write(director / "routing" / "methods-index.json", _json(route_index))
    _write(director / "masters" / "MASTER_INDEX.md", _master_index(inventory))
    _write(director / "routing" / "MASTER_ROUTING.md", _master_routing())
    _write(director / "assets" / "evidence-audit.json", _json(audit))
    _write(release / "asset-inventory.json", _json(inventory))
    _write(release / "chatgpt" / "METHOD_INDEX.json", _json([
        {**{key: value for key, value in row.items() if key != "skill_path"},
         "method_file": "METHODS_LIBRARY.json"} for row in route_index
    ]))
    _write(release / "chatgpt" / "METHODS_LIBRARY.json", _json(chatgpt_methods))
    _write(release / "chatgpt" / "EVIDENCE_AUDIT.json", _json(audit))
    for name in ("install_runtime.py", "hermes_release.py", "version_report.py", "export_plugin.py"):
        shutil.copy2(SCRIPTS / name, release / name)
    files_manifest = {}
    for path in sorted(release.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"release contains symlink: {path}")
        if path.is_file():
            rel = path.relative_to(release).as_posix()
            files_manifest[rel] = sha256(path.read_bytes())
    manifest = {
        "schema_version": 1,
        "version": version,
        "master_count": len(ASSETS),
        "method_count": len(route_index),
        "files": files_manifest,
    }
    _write(release / "manifest.json", _json(manifest))
    with ZipFile(archive_path, "x", compression=ZIP_DEFLATED) as archive:
        for path in sorted(release.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(release).as_posix())
    _write(checksum_path, f"{hashlib.sha256(archive_path.read_bytes()).hexdigest()}  {archive_path.name}\n")
    return release, archive_path


def build(version: str, audit: dict[str, object], output_root: Path = DIST) -> tuple[Path, Path]:
    """Keep failed outputs for inspection without blocking a same-version retry."""
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9]+)?", version):
        raise ValueError("version must be a semantic version, optionally with a simple suffix")
    release = output_root / f"ai-film-system-{version}"
    archive = output_root / f"ai-film-system-{version}.zip"
    checksum = output_root / f"ai-film-system-{version}.zip.sha256"
    preexisting = release.exists() or archive.exists() or checksum.exists()
    try:
        return _build_unchecked(version, audit, output_root)
    except Exception:
        if not preexisting:
            failed_root = output_root / "failed-builds"
            failed_root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            for path in (release, archive, checksum):
                if path.exists():
                    if not path.resolve().is_relative_to(output_root.resolve()):
                        raise ValueError("failed output escaped build directory")
                    shutil.move(str(path), str(failed_root / f"{path.name}-{stamp}"))
        raise


def _master_index(inventory: list[dict[str, object]]) -> str:
    lines = [
        "# 大师方法索引", "",
        "研究包结构已接入；证据与调用权限以各 Skill 的 references/methods.json 为准。"
        "索引并不代表全部方法已获来源核实。", "",
        "| slug | 姓名 | 岗位 | 研究包原文件 | 标注版本 | 方法数 | Skill |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for item in inventory:
        slug = item["slug"]
        lines.append(
            f"| {slug} | {item['name']} | {item['field']} | "
            f"{item['source_filename']} | {item['declared_version']} | "
            f"{item['method_count']} | ../../master-{slug}/SKILL.md |"
        )
    return "\n".join(lines) + "\n"


def _master_routing() -> str:
    return (
        "# 大师方法路由\n\n"
        "先由总导演识别创作问题与岗位，再运行 scripts/route_methods.py 的候选过滤，"
        "最后只读取命中 Skill 的方法、限制与证据。methods-index.json 是候选索引，"
        "不是 Skill-to-Skill 函数调用。\n\n"
        "NORMAL 可按证据范围使用；LIMITED 必须披露缺口；SANDBOX 只作构思参考且"
        "不得声称是大师本人确认的方法；BLOCKED 不得调用。"
        "重要冲突或关键归因不明时暂停相关决策，其他工作可继续。\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=DIST)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    release, archive = build(args.version, audit, args.output_root)
    print(f"BUILT {release} and {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
