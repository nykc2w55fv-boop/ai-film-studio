"""Export a versioned, private, skills-only ChatGPT plugin from one release."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from install_runtime import verify_release


def export(release: Path, output_root: Path) -> tuple[Path, Path]:
    manifest = verify_release(release)
    version = manifest["version"]
    package = output_root / f"ai-film-studio-plugin-{version}"
    archive = output_root / f"ai-film-studio-plugin-{version}.zip"
    checksum = output_root / f"ai-film-studio-plugin-{version}.zip.sha256"
    if package.exists() or archive.exists() or checksum.exists():
        raise FileExistsError("plugin export already exists")
    package.mkdir(parents=True)
    shutil.copytree(release / "skills", package / "skills")
    for skill in (package / "skills").iterdir():
        if not (skill / "SKILL.md").is_file():
            continue
        agent = skill / "agents" / "openai.yaml"
        agent.parent.mkdir(exist_ok=True)
        agent.write_text("policy:\n  products: [CHAT]\n", encoding="utf-8", newline="\n")
    director = package / "skills" / "ai-film-director" / "SKILL.md"
    content = director.read_text(encoding="utf-8")
    content += ("\n## ChatGPT Plugin 运行边界\n\n"
                "本插件版本见 `references/plugin-version.json`。ChatGPT 中不能假定可运行随包 Python 脚本、"
                "读取本机影片目录或自动同步项目事实。需要文件更新时交付标准化交接文件，"
                "由用户确认后交 Codex 导入。\n")
    director.write_text(content, encoding="utf-8", newline="\n")
    version_file = director.parent / "references" / "plugin-version.json"
    version_file.parent.mkdir(exist_ok=True)
    version_file.write_text(json.dumps({"version": version, "source": "ai-film-system"},
                                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    plugin = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "ai-film-studio", "version": version,
        "description": "面向单部影片的总导演、14 位大师方法和 11 个岗位模块。",
        "author": {"name": "AI Film Studio"},
        "extensions": {"com.openai": {"interface": {
            "displayName": "AI Film Studio", "shortDescription": "影片创作与方法路由",
            "longDescription": "按阶段调用影视总导演、14 位大师方法和 11 个岗位模块。",
            "developerName": "AI Film Studio", "category": "Productivity",
            "capabilities": [], "defaultPrompt": "用 AI Film Studio 开始一部新影片。",
        }}},
    }
    (package / "plugin.json").write_text(json.dumps(plugin, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8", newline="\n")
    with ZipFile(archive, "x", compression=ZIP_DEFLATED) as zip_file:
        for path in sorted(package.rglob("*")):
            if path.is_file():
                zip_file.write(path, path.relative_to(package).as_posix())
    checksum.write_text(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n",
                        encoding="utf-8", newline="\n")
    return package, archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("dist"))
    args = parser.parse_args()
    package, archive = export(args.release, args.output_root)
    print(f"EXPORTED {package} and {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
