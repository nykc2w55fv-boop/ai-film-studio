"""Preview, install, roll back or disable a film-system user Skill release.

No command deletes files or directories. Disable is the agreed uninstall
behavior and prints a precise manual cleanup inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile


DEFAULT_TARGET = Path.home() / ".agents" / "skills"
INSTALL_MARKER = "ai-film-installation.json"
WINDOWS_ABSOLUTE = re.compile(r"(?i)(?<![A-Za-z])[A-Za-z]:[/\\]")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name) and not name.startswith(("/", "\\"))
        and "\\" not in name and ":" not in name
        and ".." not in path.parts
    )


def verify_release(release: Path) -> dict[str, object]:
    manifest_path = release / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("manifest.files must be an object")
    for rel, expected in files.items():
        if not _safe_relative(rel):
            raise ValueError(f"unsafe release path: {rel}")
        path = release / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or linked release file: {rel}")
        data = path.read_bytes()
        if _sha(data) != expected:
            raise ValueError(f"release checksum mismatch: {rel}")
        if path.suffix in {".md", ".json", ".py", ".csv", ".toml"}:
            text = data.decode("utf-8-sig")
            if WINDOWS_ABSOLUTE.search(text):
                raise ValueError(f"absolute local path in release: {rel}")
    actual = {
        path.relative_to(release).as_posix()
        for path in release.rglob("*") if path.is_file()
    } - {"manifest.json"}
    if actual != set(files):
        raise ValueError(f"unlisted release files: {sorted(actual - set(files))[:5]}")
    expected_skills = {
        f"skills/master-{slug}/SKILL.md" for slug in (
            "lu-wei", "shinobu-hashimoto", "robert-towne",
            "william-goldman", "charlie-kaufman", "steven-spielberg",
            "akira-kurosawa", "alfred-hitchcock", "roger-deakins",
            "harold-michelson", "rick-carter", "thelma-schoonmaker",
            "randy-thom", "john-knoll",
        )
    } | {"skills/ai-film-director/SKILL.md"}
    if not expected_skills <= set(files):
        raise ValueError("director or master Skill missing from release")
    skills_root = (release / "skills").resolve()
    routing_root = release / "skills" / "ai-film-director" / "routing"
    index = json.loads((routing_root / "methods-index.json").read_text(encoding="utf-8"))
    if len(index) != manifest.get("method_count") or len({row.get("id") for row in index}) != len(index):
        raise ValueError("method count or IDs differ from release manifest")
    audit = json.loads((release / "skills" / "ai-film-director" / "assets" / "evidence-audit.json").read_text(encoding="utf-8"))
    verdicts = {row["method_id"]: row for row in audit.get("methods", [])}
    for method in index:
        verdict = verdicts.get(method.get("id"))
        if not verdict or any(method.get(key) != verdict.get(key) for key in ("evidence_state", "call_permission")):
            raise ValueError(f"method evidence drift: {method.get('id')}")
    for method in index:
        reference = str(method.get("skill_path", ""))
        target = (routing_root / reference).resolve()
        if not target.is_relative_to(skills_root) or not target.is_file():
            raise ValueError(f"invalid master Skill reference: {reference}")
    for skill in (release / "skills").glob("master-*"):
        method_file = skill / "references" / "methods.json"
        for method in json.loads(method_file.read_text(encoding="utf-8")):
            reference = str(method.get("source_file", ""))
            target = (skill / reference).resolve()
            if not target.is_relative_to(skill.resolve()) or not target.is_file():
                raise ValueError(f"invalid research reference: {skill.name}/{reference}")
    if len(list((release / "skills").glob("master-*/SKILL.md"))) != manifest.get("master_count"):
        raise ValueError("master count differs from release manifest")
    roles = list((release / "skills" / "ai-film-director" / "specialists").glob("*/ROLE.md"))
    if len(roles) != 11:
        raise ValueError("expected 11 specialist roles")
    chatgpt = release / "chatgpt"
    for method in json.loads((chatgpt / "METHOD_INDEX.json").read_text(encoding="utf-8")):
        if "skill_path" in method:
            raise ValueError("ChatGPT index contains a local Skill path")
        reference = str(method.get("method_file", ""))
        if not _safe_relative(reference) or not (chatgpt / reference).is_file():
            raise ValueError(f"invalid ChatGPT method reference: {reference}")
    return manifest


def _managed_files(manifest: dict[str, object]) -> list[str]:
    return sorted(rel.removeprefix("skills/") for rel in manifest["files"] if rel.startswith("skills/"))


def preview(release: Path, target: Path) -> dict[str, object]:
    manifest = verify_release(release)
    files = _managed_files(manifest)
    existing = [rel for rel in files if (target / rel).exists()]
    marker = target / "ai-film-director" / "references" / INSTALL_MARKER
    names = {rel.split("/", 1)[0] for rel in files}
    if any((target / name).exists() for name in names) and not marker.is_file():
        raise ValueError("Skill name collision with an unmanaged directory")
    if marker.is_file():
        previous = json.loads(marker.read_text(encoding="utf-8"))
        old_files = previous.get("files", [])
        if not isinstance(old_files, list) or any(not isinstance(rel, str) or not _safe_relative(rel) for rel in old_files):
            raise ValueError("unsafe installation marker")
        old_names = {rel.split("/", 1)[0] for rel in old_files}
        if old_names != names:
            raise ValueError("Skill set changed; manual migration required to avoid stale Skills")
    return {
        "version": manifest["version"],
        "target": str(target),
        "skill_count": int(manifest["master_count"]) + 1,
        "file_count": len(files),
        "existing_files": len(existing),
        "action": "upgrade" if marker.is_file() else "install",
    }


def _backup_existing(target: Path, files: list[str]) -> Path | None:
    existing = [rel for rel in files if (target / rel).is_file()]
    if not existing:
        return None
    backup_root = target.parent / "ai-film-backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    path = backup_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".zip")
    with ZipFile(path, "x", compression=ZIP_DEFLATED) as archive:
        for rel in existing:
            archive.write(target / rel, rel)
        marker = target / "ai-film-director" / "references" / INSTALL_MARKER
        if marker.is_file():
            archive.write(marker, INSTALL_MARKER)
    return path


def install(release: Path, target: Path) -> dict[str, object]:
    info = preview(release, target)
    manifest = verify_release(release)
    files = _managed_files(manifest)
    names = sorted({rel.split("/", 1)[0] for rel in files})
    marker = target / "ai-film-director" / "references" / INSTALL_MARKER
    old_files = files
    if marker.is_file():
        old_files = json.loads(marker.read_text(encoding="utf-8"))["files"]
    backup = _backup_existing(target, old_files)
    copied: list[str] = []
    try:
        # Entrypoints are copied last so partially staged references are not advertised.
        ordered = sorted(files, key=lambda rel: rel.endswith("/SKILL.md"))
        for rel in ordered:
            source = release / "skills" / rel
            destination = target / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(rel)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps({
                "version": manifest["version"],
                "installed_at": datetime.now(timezone.utc).isoformat(),
                "files": files,
                "backup": str(backup) if backup else None,
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
    except Exception:
        if backup:
            rollback(backup, target)
        else:
            for name in names:
                entry = target / name / "SKILL.md"
                if entry.is_file():
                    entry.rename(target / name / "SKILL.disabled.md")
        raise
    info["backup"] = str(backup) if backup else None
    info["copied"] = len(copied)
    return info


def rollback(backup: Path, target: Path) -> dict[str, object]:
    if not backup.is_file():
        raise FileNotFoundError(backup)
    restored = []
    marker = target / "ai-film-director" / "references" / INSTALL_MARKER
    current_files: set[str] = set()
    if marker.is_file():
        current = json.loads(marker.read_text(encoding="utf-8"))
        current_files = {rel for rel in current.get("files", []) if isinstance(rel, str) and _safe_relative(rel)}
    with ZipFile(backup) as archive:
        if archive.testzip() is not None:
            raise ValueError("backup ZIP CRC failure")
        previous_marker = json.loads(archive.read(INSTALL_MARKER)) if INSTALL_MARKER in archive.namelist() else {}
        previous_list = previous_marker.get("files", [])
        if not isinstance(previous_list, list) or any(not isinstance(rel, str) or not _safe_relative(rel) for rel in previous_list):
            raise ValueError("unsafe backup marker")
        previous_files = set(previous_list)
        extra = sorted(current_files - previous_files)
        quarantine = None
        if extra:
            quarantine = target.parent / "ai-film-backups" / "quarantine" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            for rel in extra:
                source = target / rel
                if source.is_symlink():
                    raise ValueError(f"linked installed file: {rel}")
                if source.is_file():
                    destination = quarantine / rel
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(destination))
        for entry in archive.infolist():
            if entry.is_dir() or entry.filename == INSTALL_MARKER:
                continue
            if not _safe_relative(entry.filename):
                raise ValueError(f"unsafe backup entry: {entry.filename}")
            destination = target / entry.filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(entry))
            restored.append(entry.filename)
        if INSTALL_MARKER in archive.namelist():
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_bytes(archive.read(INSTALL_MARKER))
    return {"restored": len(restored), "backup": str(backup), "enabled": True,
            "quarantined_new_files": len(extra), "quarantine": str(quarantine) if quarantine else None}


def disable(target: Path) -> dict[str, object]:
    marker = target / "ai-film-director" / "references" / INSTALL_MARKER
    if not marker.is_file():
        raise FileNotFoundError("installation marker missing")
    data = json.loads(marker.read_text(encoding="utf-8"))
    files = data.get("files", [])
    names = sorted({str(rel).split("/", 1)[0] for rel in files})
    for name in names:
        entry = target / name / "SKILL.md"
        if entry.is_file():
            entry.rename(target / name / "SKILL.disabled.md")
    return {
        "disabled_skills": names,
        "manual_cleanup_files": [str(target / rel) for rel in files],
        "manual_cleanup_marker": str(marker),
        "backup": data.get("backup"),
        "note": "Entrypoints were renamed, not deleted. Restart Codex if discovery remains cached.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("preview", "install"):
        part = sub.add_parser(command)
        part.add_argument("--release", type=Path, required=True)
        part.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    roll = sub.add_parser("rollback")
    roll.add_argument("--backup", type=Path, required=True)
    roll.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    stop = sub.add_parser("disable")
    stop.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    try:
        if args.command == "preview":
            result = preview(args.release, args.target)
        elif args.command == "install":
            result = install(args.release, args.target)
        elif args.command == "rollback":
            result = rollback(args.backup, args.target)
        else:
            result = disable(args.target)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {type(exc).__name__}: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
