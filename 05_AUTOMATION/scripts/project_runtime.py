"""Create and check a film project's canonical continuity files.

The command never rewrites accepted creative material. Derived reports and
manifest state are backed up before an applied reconciliation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


SLUG = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
CANONICAL = (
    "project_manifest.json", "story_bible.md", "visual_bible.md",
    "shot_list.json", "asset_manifest.json", "continuity_report.md",
)
INPUTS = ("story_bible.md", "visual_bible.md", "shot_list.json", "asset_manifest.json")
IMPACT = {
    "story_bible.md": list(range(4, 17)),
    "visual_bible.md": list(range(8, 17)),
    "shot_list.json": list(range(10, 17)),
    "asset_manifest.json": list(range(12, 17)),
}
APPROVALS = ("story_direction", "screenplay_lock", "visual_direction", "final_film")
ID = re.compile(r"(?<![A-Z0-9])(?:CHAR|COST|LOC|PROP|SPACE|TIME|SC|S|A)[0-9]{3}(?![A-Z0-9])")


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_new(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def init_project(slug: str, output_root: Path) -> Path:
    if not SLUG.fullmatch(slug):
        raise ValueError("project slug must be lowercase English and hyphens")
    project = output_root / "01_PROJECTS" / slug
    if project.exists():
        raise FileExistsError(f"project already exists: {project}")
    project.mkdir(parents=True)
    _write_new(project / "story_bible.md", (
        "# 故事圣经\n\n状态：草稿。人物、场景和道具采用稳定编号，"
        "例如 CHAR001、LOC001、PROP001、SC001；未确认的事实标待核实。\n\n"
        "## 主题与人物\n\n## 场景、时间与因果\n\n## 来源与假设\n"
    ))
    _write_new(project / "visual_bible.md", (
        "# 视觉圣经\n\n状态：草稿。使用故事圣经中的稳定编号；"
        "分别记录角色外观、服装、地点、道具、光色与变化原因。\n\n"
        "## 人物与服装\n\n## 场景与空间\n\n## 道具与光色\n\n## 连续性例外\n"
    ))
    _write_new(project / "shot_list.json", _json({"schema_version": 1, "shots": []}))
    _write_new(project / "asset_manifest.json", _json({"schema_version": 1, "assets": []}))
    manifest = {
        "schema_version": 1,
        "slug": slug,
        "mode": "AUTO",
        "version": "0.1.0",
        "current_stage": 1,
        "approvals": {name: "pending" for name in APPROVALS},
        "locked_files": [],
        "accepted_shots": [],
        "stale_stages": [],
        "needs_approval": [],
        "input_hashes": {name: _sha(project / name) for name in INPUTS},
        "dependencies": {"story_bible.md": IMPACT["story_bible.md"],
                         "visual_bible.md": IMPACT["visual_bible.md"],
                         "shot_list.json": IMPACT["shot_list.json"],
                         "asset_manifest.json": IMPACT["asset_manifest.json"]},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_new(project / "project_manifest.json", _json(manifest))
    _write_new(project / "continuity_report.md", report_text(project, []))
    return project


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _unique_ids(items: list[dict[str, object]], label: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for row in items:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append(f"{label}: row missing string id")
            continue
        value = str(row["id"])
        if value in seen:
            errors.append(f"{label}: duplicate id {value}")
        seen.add(value)
    return seen


def _real_project_file(project: Path, value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return False
    path = project / relative
    return path.is_file() and not path.is_symlink()


def check_project(project: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for name in CANONICAL:
        if not (project / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        return errors, warnings
    manifest = _load_json(project / "project_manifest.json")
    shots_data = _load_json(project / "shot_list.json")
    assets_data = _load_json(project / "asset_manifest.json")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        errors.append("project_manifest.json: unsupported schema")
        return errors, warnings
    if manifest.get("mode") not in {"AUTO", "MANUAL"}:
        errors.append("project_manifest.json: invalid mode")
    shots = shots_data.get("shots") if isinstance(shots_data, dict) else None
    assets = assets_data.get("assets") if isinstance(assets_data, dict) else None
    if not isinstance(shots, list) or not isinstance(assets, list):
        errors.append("shot_list.json and asset_manifest.json require arrays")
        return errors, warnings
    shot_ids = _unique_ids(shots, "shot_list", errors)
    asset_ids = _unique_ids(assets, "asset_manifest", errors)
    story = (project / "story_bible.md").read_text(encoding="utf-8")
    visual = (project / "visual_bible.md").read_text(encoding="utf-8")
    defined = set(ID.findall(story + "\n" + visual))
    for shot in shots:
        if not isinstance(shot, dict):
            continue
        shot_id = str(shot.get("id", "?"))
        if not re.fullmatch(r"S[0-9]{3}", shot_id):
            errors.append(f"invalid shot id: {shot_id}")
        for key in ("scene_id", "location_id", "time_id", "space_id"):
            value = shot.get(key)
            if value and value not in defined:
                errors.append(f"{shot_id}: unknown {key} {value}")
        for key in ("character_ids", "costume_ids", "prop_ids"):
            values = shot.get(key, [])
            if not isinstance(values, list):
                errors.append(f"{shot_id}: {key} must be an array")
                continue
            for value in values:
                if value not in defined:
                    errors.append(f"{shot_id}: unknown {key} {value}")
        asset_refs = shot.get("asset_ids", [])
        if not isinstance(asset_refs, list):
            errors.append(f"{shot_id}: asset_ids must be an array")
            asset_refs = []
        for value in asset_refs:
            if value not in asset_ids:
                errors.append(f"{shot_id}: unknown asset {value}")
        if shot.get("status") in {"generated", "accepted"} and not _real_project_file(project, shot.get("file_path")):
            errors.append(f"{shot_id}: real file required for {shot['status']}")
        if shot.get("status") == "accepted" and not shot.get("acceptance_evidence"):
            errors.append(f"{shot_id}: acceptance evidence required")
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        asset_id = str(asset.get("id", "?"))
        for value in asset.get("shot_ids", []):
            if value not in shot_ids:
                errors.append(f"{asset_id}: unknown shot {value}")
        if asset.get("status") in {"generated", "accepted"} and not _real_project_file(project, asset.get("file_path")):
            errors.append(f"{asset_id}: real file required for {asset['status']}")
        if asset.get("status") in {"generated", "accepted"} and not asset.get("rights_source"):
            errors.append(f"{asset_id}: rights source required")
        if asset.get("status") == "accepted" and not asset.get("acceptance_evidence"):
            errors.append(f"{asset_id}: acceptance evidence required")
    accepted = set(manifest.get("accepted_shots", []))
    if not accepted <= shot_ids:
        errors.append(f"accepted shots absent from list: {sorted(accepted - shot_ids)}")
    for name in INPUTS:
        previous = manifest.get("input_hashes", {}).get(name)
        if previous != _sha(project / name):
            warnings.append(f"changed {name}; downstream stages need review")
    return errors, warnings


def report_text(project: Path, problems: list[str]) -> str:
    story = (project / "story_bible.md").read_text(encoding="utf-8")
    visual = (project / "visual_bible.md").read_text(encoding="utf-8")
    shots = _load_json(project / "shot_list.json")["shots"]
    assets = _load_json(project / "asset_manifest.json")["assets"]
    manifest = _load_json(project / "project_manifest.json")
    entities = sorted(set(ID.findall(story + "\n" + visual)))
    lines = [
        "# 连续性检查报告", "",
        f"项目：{project.name}", "",
        "本报告由项目文件生成；它不证明真实媒体已生成或验收。", "",
        "## 事实源摘要", "",
        f"- 稳定编号：{', '.join(entities) if entities else '暂无'}。",
        f"- 镜头：{len(shots)}；素材：{len(assets)}。",
        f"- 当前阶段：{manifest.get('current_stage')}；待确认：{', '.join(name for name, state in manifest.get('approvals', {}).items() if state != 'accepted') or '无'}。",
        f"- 待复查阶段：{', '.join(map(str, manifest.get('stale_stages', []))) or '无'}。", "",
    ]
    if problems:
        lines.extend(["## 待处理", ""])
        lines.extend(f"- {problem}" for problem in problems)
    else:
        lines.extend(["## 当前检查", "", "- 结构与引用检查未发现问题；创作质量仍需阶段验收。"])
    return "\n".join(lines) + "\n"


def reconcile(project: Path, apply: bool = False) -> dict[str, object]:
    errors, warnings = check_project(project)
    if errors:
        return {"applied": False, "errors": errors, "warnings": warnings}
    manifest_path = project / "project_manifest.json"
    manifest = _load_json(manifest_path)
    changed = [
        name for name in INPUTS
        if manifest.get("input_hashes", {}).get(name) != _sha(project / name)
    ]
    affected = sorted({stage for name in changed for stage in IMPACT[name]})
    locked = set(manifest.get("locked_files", []))
    approvals = set(manifest.get("accepted_shots", []))
    needs_approval = sorted(set(manifest.get("needs_approval", [])) | (set(changed) & locked))
    if approvals and any(name in changed for name in ("story_bible.md", "visual_bible.md", "shot_list.json")):
        needs_approval.append("accepted_shots")
    result = {
        "applied": False, "changed": changed, "affected_stages": affected,
        "needs_approval": sorted(set(needs_approval)), "errors": [], "warnings": warnings,
    }
    if not apply:
        return result
    backup = project / "history" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(manifest_path, backup / manifest_path.name)
    report_path = project / "continuity_report.md"
    shutil.copy2(report_path, backup / report_path.name)
    manifest["stale_stages"] = sorted(set(manifest.get("stale_stages", [])) | set(affected))
    manifest["needs_approval"] = sorted(set(needs_approval))
    manifest["input_hashes"] = {name: _sha(project / name) for name in INPUTS}
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(_json(manifest), encoding="utf-8", newline="\n")
    report_path.write_text(report_text(project, warnings), encoding="utf-8", newline="\n")
    result["applied"] = True
    result["backup"] = backup.relative_to(project).as_posix()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("init")
    create.add_argument("--slug", required=True)
    create.add_argument("--output-root", type=Path, default=Path.cwd())
    check = sub.add_parser("check")
    check.add_argument("--project", type=Path, required=True)
    update = sub.add_parser("reconcile")
    update.add_argument("--project", type=Path, required=True)
    update.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            print(init_project(args.slug, args.output_root))
        elif args.command == "check":
            errors, warnings = check_project(args.project)
            print(_json({"errors": errors, "warnings": warnings}))
            return 1 if errors else 0
        else:
            result = reconcile(args.project, args.apply)
            print(_json(result))
            return 1 if result["errors"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
