"""Focused checks for routing, project continuity and installation lifecycle."""

from __future__ import annotations

import json
import sys
import unittest
from contextlib import nullcontext
from uuid import uuid4
from pathlib import Path
from zipfile import ZipFile


SCRIPTS = Path(__file__).resolve().parents[2] / "05_AUTOMATION" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from install_runtime import disable, install, rollback, verify_release  # noqa: E402
from build_release import build  # noqa: E402
from evidence_audit import method_verdict  # noqa: E402
from master_assets import Asset, read_asset  # noqa: E402
from project_runtime import check_project, init_project, reconcile  # noqa: E402
from handoff import inspect as inspect_handoff, apply as apply_handoff, restore as restore_handoff  # noqa: E402
from route_methods import classify, route  # noqa: E402


def fixture_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "dist" / "test-runs" / uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


class RuntimeTests(unittest.TestCase):
    def test_handoff_confirmation_conflict_idempotency_and_rollback(self) -> None:
        with nullcontext(fixture_root()) as root:
            project = init_project("handoff-film", root)
            original = (project / "story_bible.md").read_bytes()
            import hashlib
            handoff = root / "handoff.json"
            payload = {
                "schema_version": 1, "handoff_id": "draft-one", "project_slug": "handoff-film",
                "source": "ChatGPT Project test", "source_version": "1",
                "confirmation": {"status": "pending", "confirmed_by": "", "confirmed_at": ""},
                "changes": [{"file": "story_bible.md", "operation": "append",
                             "base_sha256": hashlib.sha256(original).hexdigest(),
                             "content": "## 新决定\nCHAR001 在 LOC001 等待。"}],
            }
            handoff.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(inspect_handoff(project, handoff)["status"], "blocked")
            payload["confirmation"] = {"status": "accepted", "confirmed_by": "user", "confirmed_at": "2026-11-06"}
            handoff.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(apply_handoff(project, handoff)["applied"])
            result = apply_handoff(project, handoff, operator_confirmed=True)
            self.assertTrue(result["applied"])
            self.assertEqual(result["affected_stages"], list(range(4, 17)))
            self.assertEqual(inspect_handoff(project, handoff)["status"], "already_imported")
            self.assertEqual(check_project(project), ([], []))
            restore_handoff(project, project / result["snapshot"])
            self.assertEqual((project / "story_bible.md").read_bytes(), original)
            payload["handoff_id"] = "draft-two"
            handoff.write_text(json.dumps(payload), encoding="utf-8")
            (project / "story_bible.md").write_text("changed", encoding="utf-8")
            self.assertEqual(inspect_handoff(project, handoff)["conflicts"], ["story_bible.md"])

    def test_twelve_routing_scenarios(self) -> None:
        cases = [
            ("写人物动机与剧本", "screenwriting"),
            ("设计导演调度", "directing"),
            ("讨论摄影光影", "cinematography"),
            ("绘制分镜和轴线", "storyboard"),
            ("设计服装道具", "art-direction"),
            ("确定剪辑节奏", "editing"),
            ("制作环境音和配音", "sound-design"),
            ("评估视效合成", "visual-effects"),
            ("整理研究来源", None),
            ("核对连续性", None),
            ("安排生产批次和成本", None),
            ("查询天气预报", None),
        ]
        for task, expected in cases:
            with self.subTest(task=task):
                fields = classify(task)
                self.assertIn(expected, fields) if expected else self.assertEqual(fields, [])

    def test_route_keeps_sandbox_and_excludes_blocked(self) -> None:
        index = [
            {"id": "A", "master_slug": "x", "field": "screenwriting", "skill_path": "x", "name": "故事结构", "problem": "", "trigger": "", "evidence_state": "UNVERIFIED", "call_permission": "SANDBOX"},
            {"id": "B", "master_slug": "y", "field": "screenwriting", "skill_path": "y", "name": "故事结构", "problem": "", "trigger": "", "evidence_state": "CONFLICTED", "call_permission": "BLOCKED"},
        ]
        result = route("请处理故事结构", index)
        self.assertEqual([row["method_id"] for row in result["selected"]], ["A"])
        self.assertEqual(result["selected"][0]["call_permission"], "SANDBOX")

    def test_project_change_propagates_and_acceptance_requires_file(self) -> None:
        with nullcontext(fixture_root()) as folder:
            project = init_project("small-film", folder)
            with (project / "story_bible.md").open("a", encoding="utf-8") as out:
                out.write("\nCHAR001 在 LOC001 丢失 PROP001。\n")
            pending = reconcile(project)
            self.assertEqual(pending["affected_stages"], list(range(4, 17)))
            applied = reconcile(project, apply=True)
            self.assertTrue(applied["applied"])
            self.assertEqual(check_project(project), ([], []))
            report = (project / "continuity_report.md").read_text(encoding="utf-8")
            self.assertIn("CHAR001", report)
            self.assertIn("LOC001", report)
            shots = {"schema_version": 1, "shots": [{"id": "S001", "scene_id": "SC001", "status": "accepted", "file_path": "missing.mp4"}]}
            (project / "shot_list.json").write_text(json.dumps(shots), encoding="utf-8")
            errors, _ = check_project(project)
            self.assertTrue(any("real file required" in row for row in errors))
            self.assertTrue(any("acceptance evidence required" in row for row in errors))

    def test_time_space_and_costume_references(self) -> None:
        with nullcontext(fixture_root()) as folder:
            project = init_project("continuity-film", folder)
            shots = {"schema_version": 1, "shots": [{
                "id": "S001", "time_id": "TIME001", "space_id": "SPACE001",
                "costume_ids": ["COST001"], "status": "planned",
            }]}
            (project / "shot_list.json").write_text(json.dumps(shots), encoding="utf-8")
            errors, _ = check_project(project)
            self.assertEqual(sum("unknown" in row for row in errors), 3)
            with (project / "visual_bible.md").open("a", encoding="utf-8") as out:
                out.write("\nTIME001 雨夜；SPACE001 站台；COST001 深色外套。\n")
            errors, _ = check_project(project)
            self.assertFalse(errors)

    def test_zip_path_escape_rejected(self) -> None:
        with nullcontext(fixture_root()) as root:
            source = root / "bad.zip"
            with ZipFile(source, "w") as archive:
                archive.writestr("../escape.md", "unsafe")
            with self.assertRaisesRegex(ValueError, "unsafe ZIP path"):
                read_asset(Asset("test", "Test", "screenwriting", "bad.zip", "1"), root)

    def test_failed_build_is_preserved_outside_release_name(self) -> None:
        with nullcontext(fixture_root()) as root:
            with self.assertRaisesRegex(ValueError, "missing audit verdict"):
                build("9.9.9", {"methods": []}, root)
            self.assertFalse((root / "ai-film-system-9.9.9").exists())
            failed = list((root / "failed-builds").iterdir())
            self.assertEqual(len(failed), 1)
            self.assertTrue(failed[0].is_dir())

    def test_existing_release_is_not_overwritten(self) -> None:
        with nullcontext(fixture_root()) as root:
            existing = root / "ai-film-system-9.9.9"
            existing.mkdir()
            (existing / "note.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                build("9.9.9", {"methods": []}, root)
            self.assertEqual((existing / "note.txt").read_text(encoding="utf-8"), "preserve")

    def test_unresolved_citation_and_permission_narrowing(self) -> None:
        method = {"id": "M01", "evidence_ids": ["A1", "A2"], "source_file": "research.md", "source_heading": "方法"}
        sources = {"A1": ["https://example.org/source"]}
        fetched = {"https://example.org/source": {"reachable": True}}
        verdict = method_verdict(method, sources, fetched)
        self.assertEqual(verdict["unresolved_evidence_ids"], ["A2"])
        self.assertEqual((verdict["evidence_state"], verdict["call_permission"]), ("PARTIAL", "LIMITED"))
        narrowed = method_verdict(method, sources, fetched, {"evidence_state": "PARTIAL", "call_permission": "SANDBOX"})
        self.assertEqual(narrowed["call_permission"], "SANDBOX")
        with self.assertRaisesRegex(ValueError, "SUPPORTED requires"):
            method_verdict(method, sources, fetched, {"evidence_state": "SUPPORTED"})

    def test_install_upgrade_rollback_and_disable(self) -> None:
        with nullcontext(fixture_root()) as root:
            target = root / "skills"
            names = ["ai-film-director"] + [
                "master-" + name for name in (
                    "lu-wei", "shinobu-hashimoto", "robert-towne", "william-goldman",
                    "charlie-kaufman", "steven-spielberg", "akira-kurosawa",
                    "alfred-hitchcock", "roger-deakins", "harold-michelson",
                    "rick-carter", "thelma-schoonmaker", "randy-thom", "john-knoll",
                )
            ]
            def make_release(version: str, director_text: str) -> Path:
                release = root / version
                files = {}
                import hashlib
                def add_file(path: Path, content: str) -> None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                    files[path.relative_to(release).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
                for name in names:
                    path = release / "skills" / name / "SKILL.md"
                    add_file(path, director_text if name == "ai-film-director" else name)
                    if name.startswith("master-"):
                        add_file(release / "skills" / name / "references" / "methods.json", "[]")
                add_file(release / "skills" / "ai-film-director" / "routing" / "methods-index.json", "[]")
                add_file(release / "skills" / "ai-film-director" / "assets" / "evidence-audit.json", '{"methods": []}')
                for role in ("research", "screenwriting", "directing", "cinematography", "storyboard",
                             "art-direction", "sound-design", "editing", "continuity", "production", "visual-effects"):
                    add_file(release / "skills" / "ai-film-director" / "specialists" / role / "ROLE.md", role)
                if version == "0.1.1":
                    add_file(release / "skills" / "ai-film-director" / "scripts" / "new.py", "new")
                add_file(release / "chatgpt" / "METHOD_INDEX.json", "[]")
                add_file(release / "chatgpt" / "METHODS_LIBRARY.json", "[]")
                (release / "manifest.json").write_text(json.dumps({"version": version, "master_count": 14,
                                                                     "method_count": 0, "files": files}), encoding="utf-8")
                return release
            first = make_release("0.1.0", "original")
            second = make_release("0.1.1", "upgraded")
            verify_release(first)
            install(first, target)
            result = install(second, target)
            self.assertEqual((target / "ai-film-director" / "SKILL.md").read_text(encoding="utf-8"), "upgraded")
            restored = rollback(Path(result["backup"]), target)
            self.assertEqual((target / "ai-film-director" / "SKILL.md").read_text(encoding="utf-8"), "original")
            self.assertFalse((target / "ai-film-director" / "scripts" / "new.py").exists())
            self.assertEqual(restored["quarantined_new_files"], 1)
            self.assertTrue((Path(restored["quarantine"]) / "ai-film-director" / "scripts" / "new.py").is_file())
            disabled = disable(target)
            self.assertEqual(len(disabled["disabled_skills"]), 15)
            self.assertFalse((target / "ai-film-director" / "SKILL.md").exists())
            self.assertTrue((target / "ai-film-director" / "SKILL.disabled.md").exists())


if __name__ == "__main__":
    unittest.main()
