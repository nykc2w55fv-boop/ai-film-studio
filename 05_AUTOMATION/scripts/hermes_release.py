"""Stage and select immutable Hermes skill copies without deleting old versions."""

from __future__ import annotations

import argparse
import json
import os
import stat
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from install_runtime import verify_release


def stage(release: Path, root: Path) -> dict[str, str]:
    root = root.absolute()
    manifest = verify_release(release)
    version = manifest["version"]
    target = root / "releases" / version
    if target.exists():
        raise FileExistsError(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(release, target)
    verify_release(target)
    for path in sorted(target.rglob("*"), reverse=True):
        if path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        elif os.name != "nt" and path.is_dir():
            path.chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    if os.name != "nt":
        target.chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    return {"version": version, "path": str(target / "skills")}


def select(root: Path, version: str) -> dict[str, str]:
    root = root.absolute()
    release = root / "releases" / version
    manifest = verify_release(release)
    active = root / "active.json"
    if active.exists():
        old = root / "history" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
        old.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(active, old)
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_text(json.dumps({"version": manifest["version"], "skills_dir": str(release / "skills")},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"version": version, "skills_dir": str(release / "skills"),
            "config_entry": "${AI_FILM_SKILLS_DIR}"}


def report(root: Path) -> dict[str, str]:
    root = root.absolute()
    active = json.loads((root / "active.json").read_text(encoding="utf-8"))
    release = root / "releases" / active["version"]
    verify_release(release)
    if active["skills_dir"] != str(release / "skills"):
        raise ValueError("active skills path mismatch")
    return active


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("stage", "select", "report", "run"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--version")
    args, rest = parser.parse_known_args()
    if args.command == "stage":
        if not args.release:
            parser.error("stage requires --release")
        result = stage(args.release, args.root)
    elif args.command == "select":
        if not args.version:
            parser.error("select requires --version")
        result = select(args.root, args.version)
    else:
        result = report(args.root)
        if args.command == "run":
            if not rest:
                parser.error("run requires a Hermes command after --")
            command = rest[1:] if rest[0] == "--" else rest
            env = os.environ.copy()
            env["AI_FILM_SKILLS_DIR"] = result["skills_dir"]
            return subprocess.call(command, env=env)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
