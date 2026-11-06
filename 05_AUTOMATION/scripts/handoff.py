"""Preview, import and roll back a confirmed ChatGPT film handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from project_runtime import CANONICAL, INPUTS, SLUG, _json, check_project, reconcile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bases(project: Path) -> dict[str, object]:
    errors, warnings = check_project(project)
    if errors:
        raise ValueError(f"project check failed: {errors}")
    manifest = json.loads((project / "project_manifest.json").read_text(encoding="utf-8"))
    return {"project_slug": manifest["slug"], "project_version": manifest.get("version"),
            "base_sha256": {name: digest((project / name).read_bytes()) for name in INPUTS},
            "warnings": warnings}


def inspect(project: Path, handoff_file: Path) -> dict[str, object]:
    data = json.loads(handoff_file.read_text(encoding="utf-8"))
    manifest = json.loads((project / "project_manifest.json").read_text(encoding="utf-8"))
    errors, _ = check_project(project)
    if errors:
        raise ValueError(f"project check failed: {errors}")
    if data.get("schema_version") != 1 or data.get("project_slug") != manifest.get("slug"):
        raise ValueError("handoff schema or project slug mismatch")
    identity = data.get("handoff_id")
    if not isinstance(identity, str) or not SLUG.fullmatch(identity):
        raise ValueError("handoff_id must be a stable lowercase slug")
    if not isinstance(data.get("source"), str) or not data["source"].strip():
        raise ValueError("source is required")
    if not isinstance(data.get("source_version"), str) or not data["source_version"].strip():
        raise ValueError("source_version is required")
    changes = data.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ValueError("changes must be a nonempty array")
    fingerprint = digest(_json(data).encode("utf-8"))
    previous = next((row for row in manifest.get("imports", []) if row.get("handoff_id") == identity), None)
    if previous:
        if previous.get("sha256") != fingerprint:
            raise ValueError("handoff_id already imported with different content")
        return {"status": "already_imported", "handoff_id": identity, "changes": []}
    conflicts = []
    seen = set()
    for change in changes:
        if not isinstance(change, dict) or change.get("file") not in INPUTS:
            raise ValueError("only four canonical content files may be changed")
        name = change["file"]
        if name in seen:
            raise ValueError(f"duplicate file: {name}")
        seen.add(name)
        path = project / name
        if path.is_symlink():
            raise ValueError(f"linked project file: {name}")
        if change.get("base_sha256") != digest(path.read_bytes()):
            conflicts.append(name)
        if change.get("operation") not in {"append", "replace"}:
            raise ValueError(f"invalid operation: {name}")
        if change["operation"] == "append" and not name.endswith(".md"):
            raise ValueError("append is limited to Markdown facts")
        if not isinstance(change.get("content"), str) or not change["content"].strip():
            raise ValueError(f"empty content: {name}")
        if name.endswith(".json"):
            parsed = json.loads(change["content"])
            if not isinstance(parsed, dict) or parsed.get("schema_version") != 1:
                raise ValueError(f"invalid canonical JSON: {name}")
    confirmation = data.get("confirmation")
    confirmed = (isinstance(confirmation, dict) and confirmation.get("status") == "accepted"
                 and bool(confirmation.get("confirmed_by")) and bool(confirmation.get("confirmed_at")))
    locked = sorted(seen & set(manifest.get("locked_files", [])))
    if locked and not (isinstance(confirmation, dict) and confirmation.get("reapproval") is True):
        conflicts.extend(locked)
    return {"status": "ready" if confirmed and not conflicts else "blocked",
            "handoff_id": identity, "confirmed": bool(confirmed), "conflicts": sorted(set(conflicts)),
            "locked_files": locked, "changes": sorted(seen), "sha256": fingerprint}


def apply(project: Path, handoff_file: Path, operator_confirmed: bool = False) -> dict[str, object]:
    result = inspect(project, handoff_file)
    if result["status"] == "already_imported":
        return result
    if result["status"] != "ready" or not operator_confirmed:
        return {**result, "applied": False, "operator_confirmation_required": not operator_confirmed}
    data = json.loads(handoff_file.read_text(encoding="utf-8"))
    snapshot = project / "history" / ("handoff-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    snapshot.mkdir(parents=True, exist_ok=False)
    for name in CANONICAL:
        shutil.copy2(project / name, snapshot / name)
    shutil.copy2(handoff_file, snapshot / "handoff.json")
    try:
        for change in data["changes"]:
            path = project / change["file"]
            content = change["content"]
            if change["operation"] == "append":
                content = path.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + content.strip("\n") + "\n"
            path.write_text(content, encoding="utf-8", newline="\n")
        errors, _ = check_project(project)
        if errors:
            raise ValueError(f"imported facts failed check: {errors}")
        manifest_path = project / "project_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.setdefault("imports", []).append({
            "handoff_id": result["handoff_id"], "sha256": result["sha256"],
            "source": data["source"], "source_version": data["source_version"],
            "confirmation": data["confirmation"], "snapshot": snapshot.relative_to(project).as_posix(),
        })
        manifest_path.write_text(_json(manifest), encoding="utf-8", newline="\n")
        reconcile_result = reconcile(project, apply=True)
        if reconcile_result["errors"]:
            raise ValueError(f"reconcile failed: {reconcile_result['errors']}")
    except Exception:
        restore(project, snapshot)
        raise
    return {**result, "applied": True, "snapshot": snapshot.relative_to(project).as_posix(),
            "affected_stages": reconcile_result["affected_stages"],
            "needs_approval": reconcile_result["needs_approval"]}


def restore(project: Path, snapshot: Path) -> dict[str, object]:
    if not snapshot.resolve().is_relative_to((project / "history").resolve()):
        raise ValueError("snapshot must be inside project history")
    if any(not (snapshot / name).is_file() for name in CANONICAL):
        raise ValueError("incomplete snapshot")
    safety = project / "history" / ("before-rollback-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    safety.mkdir(parents=True, exist_ok=False)
    for name in CANONICAL:
        shutil.copy2(project / name, safety / name)
        shutil.copy2(snapshot / name, project / name)
    return {"restored_from": snapshot.relative_to(project).as_posix(),
            "previous_state": safety.relative_to(project).as_posix()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("bases", "preview", "import", "rollback"))
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--handoff", type=Path)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--confirmed-by-operator", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "bases":
            result = bases(args.project)
        elif args.command == "rollback":
            if not args.snapshot:
                raise ValueError("--snapshot required")
            result = restore(args.project, args.project / args.snapshot)
        else:
            if not args.handoff:
                raise ValueError("--handoff required")
            result = inspect(args.project, args.handoff) if args.command == "preview" else apply(
                args.project, args.handoff, args.confirmed_by_operator)
        print(_json(result), end="")
        return 0 if result.get("status") != "blocked" else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
