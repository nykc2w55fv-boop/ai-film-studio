"""Report local platform versions without treating them as synchronized facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from install_runtime import verify_release


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--codex-skills", type=Path, default=Path.home() / ".agents" / "skills")
    parser.add_argument("--plugin", type=Path)
    parser.add_argument("--hermes-root", type=Path)
    args = parser.parse_args()
    release = verify_release(args.release)
    report: dict[str, object] = {"release": release["version"], "codex": None,
                                 "chatgpt_plugin_package": None, "hermes": None}
    marker = args.codex_skills / "ai-film-director" / "references" / "ai-film-installation.json"
    if marker.is_file():
        report["codex"] = json.loads(marker.read_text(encoding="utf-8")).get("version")
    if args.plugin:
        report["chatgpt_plugin_package"] = json.loads((args.plugin / "plugin.json").read_text(encoding="utf-8")).get("version")
    if args.hermes_root and (args.hermes_root / "active.json").is_file():
        report["hermes"] = json.loads((args.hermes_root / "active.json").read_text(encoding="utf-8")).get("version")
    report["available_package_versions_match"] = all(value == report["release"] for key, value in report.items()
                                                     if key in {"codex", "chatgpt_plugin_package", "hermes"} and value is not None)
    report["three_platforms_verified"] = False  # Requires live ChatGPT and Hermes client calls.
    report["note"] = "Package versions do not prove client installation or project-file sync."
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
