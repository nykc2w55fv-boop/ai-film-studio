"""Validate and import one ChatGPT master package using only the standard library.

Run from any working directory. Import is deliberately one package at a time.
Source packages are never edited or moved. Structural validation is not fact checking.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
READY = ROOT / "03_KNOWLEDGE" / "master-research" / "ready-for-skill"
FIXTURES = ROOT / "06_QA" / "fixtures"
SKILLS = ROOT / ".agents" / "skills"
DIRECTOR = SKILLS / "ai-film-director"
INDEX = DIRECTOR / "masters" / "MASTER_INDEX.md"
ROUTES = DIRECTOR / "routing" / "MASTER_ROUTING.md"
METHODS = ROOT / "CHATGPT_METHODS_LIBRARY.md"
FIELDS = {
    "screenwriting": "编剧",
    "directing": "导演",
    "cinematography": "摄影",
    "editing": "剪辑",
    "art-direction": "美术设计",
    "sound-design": "声音设计",
    "storyboard": "分镜与视觉预演",
    "visual-effects": "视觉特效与合成",
}
META_KEYS = (
    "slug",
    "name_zh",
    "name_en",
    "field",
    "status",
    "representative_works",
    "summary",
)
SECTIONS = (
    "核心方法",
    "本人明确表达",
    "研究者归纳",
    "证据台账",
    "作品案例",
    "适用与局限",
    "可执行步骤",
    "AI 短片迁移规则",
    "测试案例",
    "来源列表",
)
SLUG = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
SOURCE = re.compile(r"\[S[1-9][0-9]*\]")


class PackageError(ValueError):
    """A package or its destination fails a controlled validation rule."""


def package_path(name: str, fixture: bool) -> Path:
    if Path(name).name != name or not name.endswith(".md") or name in {".", ".."}:
        raise PackageError("package must be a Markdown basename, with no path separators")
    base = FIXTURES if fixture else READY
    path = base / name
    if not path.is_file() or not path.resolve().is_relative_to(base.resolve()):
        raise PackageError("package is missing or escapes its allowed directory")
    return path


def parse_package(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "# MASTER_METHOD_PACKAGE":
        raise PackageError("first line must be # MASTER_METHOD_PACKAGE")
    meta: dict[str, str] = {}
    pos = 1
    while pos < len(lines) and lines[pos].startswith("- "):
        match = re.fullmatch(r"- ([a-z_]+): (.+)", lines[pos])
        if not match or match.group(1) in meta:
            raise PackageError(f"invalid or duplicate metadata at line {pos + 1}")
        meta[match.group(1)] = match.group(2).strip()
        pos += 1
    if tuple(meta) != META_KEYS:
        raise PackageError("metadata keys or order differ from MASTER_PACKAGE_SCHEMA.md")
    sections: dict[str, str] = {}
    current: str | None = None
    for line in lines[pos:]:
        if line.startswith("## "):
            current = line[3:].strip()
            if current in sections:
                raise PackageError(f"duplicate section: {current}")
            sections[current] = ""
        elif current is not None:
            sections[current] += line + "\n"
        elif line.strip():
            raise PackageError("unexpected text before first section")
    if tuple(sections) != SECTIONS:
        raise PackageError("section names or order differ from MASTER_PACKAGE_SCHEMA.md")
    for key, value in meta.items():
        if not value or "|" in value or "\n" in value or value in {"待核实", "待填写", "<填写>"}:
            raise PackageError(f"metadata {key} is empty, placeholder or contains a table delimiter")
    if not SLUG.fullmatch(meta["slug"]):
        raise PackageError("slug must use lowercase letters, digits and hyphens")
    if meta["field"] not in FIELDS:
        raise PackageError("unsupported field")
    if meta["status"] not in {"verified", "provisional", "simulation"}:
        raise PackageError("status must be verified, provisional or simulation")
    if path.stem != meta["slug"]:
        raise PackageError("filename must match slug")
    for heading, body in sections.items():
        if len(body.strip()) < 20:
            raise PackageError(f"section {heading} needs substantive text")
    sources = {
        match.group(1)
        for line in sections["来源列表"].splitlines()
        if (match := re.match(r"^- (\[S[1-9][0-9]*\]) .{12,}$", line))
    }
    if not sources:
        raise PackageError("source list needs locatable source entries")
    for heading in ("核心方法", "研究者归纳", "证据台账", "作品案例"):
        citations = set(SOURCE.findall(sections[heading]))
        if not citations or not citations <= sources:
            raise PackageError(f"section {heading} needs source IDs present in source list")
    for token in SOURCE.findall("\n".join(sections.values())):
        if token not in sources:
            raise PackageError(f"unknown source ID: {token}")
    test_body = sections["测试案例"]
    if not all(word in test_body for word in ("输入", "期望输出", "失败判据")):
        raise PackageError("test cases need input, expected output and failure criteria")
    return meta, {key: value.strip() for key, value in sections.items()}


def marked_rows(path: Path, start: str, end: str) -> tuple[str, list[str], str]:
    text = path.read_text(encoding="utf-8")
    a = text.find(start)
    b = text.find(end)
    if a < 0 or b < 0 or b <= a or text.count(start) != 1 or text.count(end) != 1:
        raise PackageError(f"missing or repeated managed markers in {path.name}")
    before = text[: a + len(start)]
    middle = text[a + len(start) : b]
    after = text[b:]
    return before, [line for line in middle.splitlines() if line.strip()], after


def table_cells(row: str) -> list[str]:
    if not row.startswith("|") or not row.endswith("|"):
        raise PackageError("invalid managed table row")
    return [cell.strip() for cell in row.strip("|").split("|")]


def updated_index(meta: dict[str, str], source: Path, skill_rel: str) -> str:
    before, rows, after = marked_rows(INDEX, "<!-- MASTER_INDEX_START -->", "<!-- MASTER_INDEX_END -->")
    matched = False
    for i, row in enumerate(rows):
        cells = table_cells(row)
        if len(cells) != 9:
            raise PackageError("MASTER_INDEX table must have nine columns")
        if cells[0] == meta["slug"]:
            if cells[1] != meta["name_zh"] or cells[3] != meta["field"]:
                raise PackageError("package name or field differs from MASTER_INDEX")
            if cells[6] not in {"pending", "provisional"}:
                raise PackageError("candidate is not pending or provisional")
            cells[2] = meta["name_en"]
            cells[4] = meta["representative_works"]
            cells[6] = "verified"
            cells[7] = source.relative_to(ROOT).as_posix()
            cells[8] = skill_rel
            rows[i] = "| " + " | ".join(cells) + " |"
            matched = True
    if not matched:
        raise PackageError("slug is not registered in MASTER_INDEX")
    return before + "\n" + "\n".join(rows) + "\n" + after


def appended_table(path: Path, start: str, end: str, slug: str, new_row: str) -> str:
    before, rows, after = marked_rows(path, start, end)
    if any(table_cells(row)[0] == slug for row in rows[2:]):
        raise PackageError(f"duplicate slug in {path.name}")
    rows.append(new_row)
    return before + "\n" + "\n".join(rows) + "\n" + after


def render(meta: dict[str, str], sec: dict[str, str], source: Path) -> dict[str, str]:
    slug = meta["slug"]
    name = meta["name_zh"]
    skill_name = f"master-{slug}"
    # JSON strings are valid YAML double-quoted scalars and escape punctuation safely.
    description = json.dumps(
        f"在 AI 短片{FIELDS[meta['field']]}任务中按证据使用{name}的可迁移方法；需先核对适用范围和局限。",
        ensure_ascii=False,
    )
    origin = source.relative_to(ROOT).as_posix()
    return {
        "SKILL.md": (
            f"---\nname: {skill_name}\ndescription: {description}\n---\n\n"
            f"# {name}方法 Skill\n\n适用于有明确{FIELDS[meta['field']]}任务、且本包证据与限制相符的 AI 短片工作。"
            "先读 `references/limitations.md`，再按需读 `references/methods.md`、"
            "`references/evidence-ledger.md`、`references/case-studies.md`；验收用 `evals/test-cases.md`。"
            f"\n\n原始研究包：`{origin}`。本人表述和研究者归纳不可混称。"
            "对在世创作者只迁移通用技法，不直接仿制可识别个人风格。\n"
        ),
        "references/methods.md": (
            f"# {name}：可执行方法\n\n## 核心方法\n{sec['核心方法']}\n\n"
            f"## 本人明确表达\n{sec['本人明确表达']}\n\n"
            f"## 研究者归纳\n{sec['研究者归纳']}\n\n"
            f"## 可执行步骤\n{sec['可执行步骤']}\n\n"
            f"## AI 短片迁移规则\n{sec['AI 短片迁移规则']}\n"
        ),
        "references/evidence-ledger.md": (
            f"# {name}：证据台账\n\n原包：`{origin}`\n\n"
            f"## 证据台账\n{sec['证据台账']}\n\n## 来源列表\n{sec['来源列表']}\n"
        ),
        "references/case-studies.md": f"# {name}：作品案例\n\n{sec['作品案例']}\n",
        "references/limitations.md": f"# {name}：适用与局限\n\n{sec['适用与局限']}\n",
        "evals/test-cases.md": f"# {name}：测试案例\n\n{sec['测试案例']}\n",
    }


def prepare(path: Path, fixture: bool) -> tuple[dict[str, str], dict[str, str], dict[Path, str]]:
    meta, sec = parse_package(path)
    skill_rel = f".agents/skills/master-{meta['slug']}"
    index = INDEX.read_text(encoding="utf-8") if fixture else updated_index(meta, path, skill_rel)
    route_row = f"| {meta['slug']} | {meta['field']} | {skill_rel}/SKILL.md | {meta['summary']} |"
    route = appended_table(ROUTES, "<!-- ROUTES_START -->", "<!-- ROUTES_END -->", meta["slug"], route_row)
    methods_row = (
        f"| {meta['slug']} | {meta['name_zh']} | {meta['field']} | {meta['summary']} | "
        f"{skill_rel}/references/evidence-ledger.md | {skill_rel}/SKILL.md |"
    )
    methods = appended_table(METHODS, "<!-- METHODS_START -->", "<!-- METHODS_END -->", meta["slug"], methods_row)
    rendered = render(meta, sec, path)
    output = {SKILLS / f"master-{meta['slug']}" / rel: content for rel, content in rendered.items()}
    output.update({INDEX: index, ROUTES: route, METHODS: methods})
    if fixture and meta["status"] != "simulation":
        raise PackageError("fixtures must have status: simulation")
    return meta, sec, output


def import_package(path: Path, meta: dict[str, str], output: dict[Path, str]) -> None:
    if meta["status"] != "verified":
        raise PackageError("only verified packages may be imported")
    dest = SKILLS / f"master-{meta['slug']}"
    if dest.exists():
        raise PackageError("target Skill already exists; no overwrite")
    # All content and managed sections were validated before creating any files.
    dest.mkdir()
    for target, content in output.items():
        if target in {INDEX, ROUTES, METHODS}:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    for target in (INDEX, ROUTES, METHODS):
        # Only managed rows change; the surrounding hand-written content is preserved.
        target.write_text(output[target], encoding="utf-8", newline="\n")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in {"assets", "audit", "build-release"}:
        action = sys.argv[1]
        if action == "assets":
            from master_assets import inspect_all

            print(json.dumps(inspect_all(), ensure_ascii=False, indent=2))
            return 0
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        if action == "audit":
            from evidence_audit import main as audit_main

            return audit_main()
        from build_release import main as build_main

        return build_main()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "preview", "import"))
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument("--package", help="Markdown basename under ready-for-skill")
    select.add_argument("--all", action="store_true", help="process every Markdown package in ready-for-skill")
    parser.add_argument("--fixture", action="store_true", help="preview synthetic fixture under 06_QA/fixtures")
    args = parser.parse_args()
    if args.fixture and (args.action == "import" or args.all):
        parser.error("fixtures are only for single-package check or preview")
    names = [p.name for p in sorted(READY.glob("*.md"))] if args.all else [args.package]
    if not names:
        print("No Markdown packages in ready-for-skill")
        return 0
    if args.action == "import" and args.all:
        # Preflight the whole batch before any writes. Re-prepare each package
        # during import so managed tables include earlier successful imports.
        failures = 0
        for name in names:
            try:
                path = package_path(name, False)
                meta, _, _ = prepare(path, False)
                if meta["status"] != "verified":
                    raise PackageError("only verified packages may be imported")
                if (SKILLS / f"master-{meta['slug']}").exists():
                    raise PackageError("target Skill already exists; no overwrite")
            except (OSError, UnicodeError, PackageError) as exc:
                failures += 1
                print(f"INVALID {name}: {exc}", file=sys.stderr)
        if failures:
            print("Batch aborted before writing any files", file=sys.stderr)
            return 1
    failures = 0
    for name in names:
        try:
            path = package_path(name, args.fixture)
            meta, _, output = prepare(path, args.fixture)
            if args.action == "import":
                import_package(path, meta, output)
                print(f"IMPORTED {name}: {len(output) - 3} Skill files and 3 managed documents")
            elif args.action == "preview":
                print(f"PREVIEW {name}: status={meta['status']}; no files written")
                for target in output:
                    print("  " + target.relative_to(ROOT).as_posix())
            else:
                print(f"VALID {name}: status={meta['status']}; structure only")
        except (OSError, UnicodeError, PackageError) as exc:
            failures += 1
            print(f"INVALID {name}: {exc}", file=sys.stderr)
            if args.action == "import":
                break  # Never continue a partially failed write batch.
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
