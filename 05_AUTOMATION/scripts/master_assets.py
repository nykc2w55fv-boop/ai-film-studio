"""Read-only adapters for the fourteen supplied master research assets.

This module never changes a research package. A normalized method is a
locator and routing hint, not a new claim about the creator.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "14位电影大师"


@dataclass(frozen=True)
class Asset:
    slug: str
    name: str
    field: str
    filename: str
    version: str
    heading: str = ""
    draft: str = ""


ASSETS = (
    Asset("lu-wei", "芦苇", "screenwriting", "lu-wei-research-package.md", "unmarked", r"^### M\d"),
    Asset("shinobu-hashimoto", "桥本忍", "screenwriting", "hashimoto-shinobu-research-package.md", "1.0", r"^## 模型[一二三四五六七八九十]"),
    Asset("robert-towne", "罗伯特·汤", "screenwriting", "robert-towne-research-package.md", "0.9", r"^## 模型[一二三四五六七八九十]"),
    Asset("william-goldman", "威廉·戈德曼", "screenwriting", "william-goldman-research-package.md", "unmarked", r"^### 模型\d"),
    Asset("charlie-kaufman", "查理·考夫曼", "screenwriting", "charlie-kaufman-research-package.md", "unmarked", r"^### M\d"),
    Asset("steven-spielberg", "史蒂文·斯皮尔伯格", "directing", "steven-spielberg-research-package.md", "1.0", r"^### M\d", "steven-spielberg-directing-method-SKILL.md"),
    Asset("akira-kurosawa", "黑泽明", "directing", "akira-kurosawa-directing-method.zip", "unmarked", r"^### KM-M\d"),
    Asset("alfred-hitchcock", "阿尔弗雷德·希区柯克", "directing", "alfred-hitchcock-research-package.md", "unmarked", r"^## 方法 \d", "alfred-hitchcock-research-package-skill.md"),
    Asset("roger-deakins", "罗杰·狄金斯", "cinematography", "Roger_Deakins_Method_Pack.zip", "1.0.0"),
    Asset("harold-michelson", "哈罗德·米歇尔森", "storyboard", "harold-michelson-storyboarding-method.zip", "1.0-research"),
    Asset("rick-carter", "里克·卡特", "art-direction", "rick-carter-production-design-method.zip", "1.0"),
    Asset("thelma-schoonmaker", "西奥多玛·斯库梅克", "editing", "thelma-schoonmaker-editing-method.zip", "1.0"),
    Asset("randy-thom", "兰迪·汤姆", "sound-design", "randy-thom-sound-design-method-research-pack.zip", "1.0"),
    Asset("john-knoll", "约翰·诺尔", "visual-effects", "john-knoll-visual-effects-method.zip", "1.0"),
)

SOURCE_ID = re.compile(r"(?<![A-Z0-9])([A-Z]{1,3}\d{1,3})(?![A-Z0-9])")
URL = re.compile(r"https?://[^\s<>)\]】］\"']+", re.IGNORECASE)
MAX_ZIP_BYTES = 30_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_ids(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        value = " ".join(str(part) for part in value)
    elif isinstance(value, dict):
        value = json.dumps(value, ensure_ascii=False)
    return sorted(set(SOURCE_ID.findall(str(value))))


def source_index(texts: dict[str, str]) -> dict[str, list[str]]:
    """Keep only explicitly co-located source IDs and public URLs."""
    found: dict[str, set[str]] = {}
    for text in texts.values():
        for line in text.splitlines():
            ids = source_ids(line)
            urls = [url.rstrip(".,;:，。；：\\") for url in URL.findall(line)]
            for source_id in ids:
                found.setdefault(source_id, set()).update(urls)
    return {key: sorted(value) for key, value in sorted(found.items())}


def _safe_zip_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not name.startswith(("/", "\\"))
        and "\\" not in name
        and ":" not in name
        and ".." not in path.parts
        and all(part not in {"", "."} for part in path.parts)
    )


def read_asset(asset: Asset, raw_root: Path = RAW) -> tuple[dict[str, bytes], dict[str, object]]:
    path = raw_root / asset.filename
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"missing or linked source: {asset.filename}")
    original = path.read_bytes()
    files: dict[str, bytes] = {}
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"invalid ZIP CRC: {asset.filename}")
            entries = [entry for entry in archive.infolist() if not entry.is_dir()]
            if sum(entry.file_size for entry in entries) > MAX_ZIP_BYTES:
                raise ValueError(f"ZIP exceeds size limit: {asset.filename}")
            names: set[str] = set()
            for entry in entries:
                if not _safe_zip_name(entry.filename):
                    raise ValueError(f"unsafe ZIP path: {entry.filename}")
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(f"ZIP symlink: {entry.filename}")
                basename = PurePosixPath(entry.filename).name
                if basename in names:
                    raise ValueError(f"duplicate ZIP basename: {basename}")
                names.add(basename)
                files[basename] = archive.read(entry)
    else:
        files[asset.filename] = original
        if asset.draft:
            draft = raw_root / asset.draft
            if not draft.is_file() or draft.is_symlink():
                raise ValueError(f"missing Skill draft: {asset.draft}")
            files[asset.draft] = draft.read_bytes()
    for name, data in files.items():
        if Path(name).suffix.lower() in {".md", ".json", ".csv"}:
            data.decode("utf-8-sig")
    metadata: dict[str, object] = {
        "slug": asset.slug,
        "name": asset.name,
        "field": asset.field,
        "source_filename": asset.filename,
        "source_sha256": sha256(original),
        "declared_version": asset.version,
        "file_count": len(files),
        "draft_skill": asset.draft or ("SKILL.md" if "SKILL.md" in files else None),
    }
    return files, metadata


def _section_methods(text: str, pattern: str, slug: str, source_file: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    heading = re.compile(pattern)
    matches = [i for i, line in enumerate(lines) if heading.match(line)]
    methods: list[dict[str, object]] = []
    for number, start in enumerate(matches, 1):
        line = lines[start]
        level = len(line) - len(line.lstrip("#"))
        end = len(lines)
        for pos in range(start + 1, len(lines)):
            current = lines[pos]
            if current.startswith("#"):
                current_level = len(current) - len(current.lstrip("#"))
                if current_level <= level and current.startswith("#" * current_level + " "):
                    end = pos
                    break
        section = "\n".join(lines[start:end]).strip()
        title = re.sub(r"^#+\s*", "", line).strip()
        token = re.match(r"(?:KM-)?M(\d+)", title)
        method_id = f"{slug}-M{int(token.group(1)):02d}" if token else f"{slug}-M{number:02d}"
        methods.append({
            "id": method_id,
            "name": title,
            "problem": "",
            "trigger": "",
            "limitations": "",
            "evidence_ids": source_ids(section),
            "source_file": source_file,
            "source_heading": title,
            "source_excerpt": section[:900],
        })
    return methods


def normalized_methods(asset: Asset, files: dict[str, bytes]) -> list[dict[str, object]]:
    if asset.heading:
        source_file = "SKILL.md" if asset.slug == "akira-kurosawa" else asset.filename
        text = files[source_file].decode("utf-8-sig")
        methods = _section_methods(text, asset.heading, asset.slug, source_file)
    else:
        source_file = next((name for name in files if name.endswith("methods.json")), "")
        if not source_file:
            raise ValueError(f"missing methods JSON: {asset.slug}")
        payload = json.loads(files[source_file].decode("utf-8-sig"))
        rows = payload if isinstance(payload, list) else payload.get("methods", [])
        if not isinstance(rows, list):
            raise ValueError(f"methods must be a list: {asset.slug}")
        methods = []
        for number, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                raise ValueError(f"invalid method row: {asset.slug} #{number}")
            method_id = str(row.get("method_id") or row.get("id") or f"{asset.slug}-M{number:02d}")
            name = str(row.get("method_name_zh") or row.get("method_name_cn") or row.get("method_name") or row.get("name") or "")
            if not name:
                raise ValueError(f"method has no name: {method_id}")
            methods.append({
                "id": method_id,
                "name": name,
                "problem": str(row.get("problem") or ""),
                "trigger": str(row.get("trigger") or ""),
                "limitations": str(row.get("limitations") or row.get("limits") or ""),
                "evidence_ids": source_ids(row.get("evidence") or row.get("source_ids") or []),
                "source_file": source_file,
                "source_heading": method_id,
                "source_excerpt": str(row.get("procedure") or row.get("decision_rules") or "")[:900],
            })
    if not methods or len({str(item["id"]) for item in methods}) != len(methods):
        raise ValueError(f"missing or duplicate methods: {asset.slug}")
    return methods


def inspect_all(raw_root: Path = RAW) -> list[dict[str, object]]:
    inventory = []
    for asset in ASSETS:
        files, metadata = read_asset(asset, raw_root)
        methods = normalized_methods(asset, files)
        metadata["method_count"] = len(methods)
        metadata["source_id_count"] = len(source_index({
            name: data.decode("utf-8-sig")
            for name, data in files.items() if name.endswith(".md")
        }))
        inventory.append(metadata)
    return inventory
