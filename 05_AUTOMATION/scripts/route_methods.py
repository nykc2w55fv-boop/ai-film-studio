"""Deterministic permission filter for the director's method index.

This is a narrow routing aid. The director still interprets creative intent
and reads a selected method's source and limitations before using it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FIELD_TERMS = {
    "screenwriting": ("故事", "剧情", "剧本", "人物动机", "结构", "改编", "对白", "角色", "因果"),
    "directing": ("导演", "调度", "群像", "悬念", "观众信息", "动作场面", "表演", "视角", "场面"),
    "cinematography": ("摄影", "光影", "机位", "构图", "曝光", "镜头运动", "画幅"),
    "storyboard": ("分镜", "预演", "镜头清单", "空间关系", "视线", "轴线"),
    "art-direction": ("美术", "服装", "场景设计", "道具", "材质", "世界观", "布景"),
    "editing": ("剪辑", "节奏", "转场", "素材选择", "粗剪", "时间码"),
    "sound-design": ("声音", "音效", "声场", "配音", "环境音", "声画", "音乐"),
    "visual-effects": ("特效", "视效", "合成", "抠像", "数字资产", "虚拟制作"),
}
STOP = ("天气预报", "股票", "代码报错", "报税", "购物", "快递")


def classify(task: str) -> list[str]:
    if any(token in task for token in STOP) and not any(
        token in task for terms in FIELD_TERMS.values() for token in terms
    ):
        return []
    scores = {
        field: sum(len(term) for term in terms if term in task)
        for field, terms in FIELD_TERMS.items()
    }
    best = max(scores.values(), default=0)
    if best == 0:
        return []
    return [
        field for field, score in sorted(scores.items(), key=lambda item: -item[1])
        if score and score >= max(2, best // 2)
    ][:3]


def route(task: str, index: list[dict[str, object]], limit: int = 3) -> dict[str, object]:
    fields = classify(task)
    if not fields:
        return {
            "fields": [], "selected": [], "needs_information": True,
            "reason": "未识别到足够明确的影视创作问题；先补充任务目标或场景",
        }
    selected = []
    for method in index:
        if method.get("field") not in fields or method.get("call_permission") == "BLOCKED":
            continue
        haystack = " ".join(str(method.get(key, "")) for key in ("name", "problem", "trigger"))
        words = set(re.findall(r"[\u4e00-\u9fff]{2,4}|[A-Za-z]{3,}", task))
        relevance = sum(1 for word in words if word in haystack)
        selected.append({
            "method_id": method["id"],
            "master_slug": method["master_slug"],
            "field": method["field"],
            "skill_path": method["skill_path"],
            "evidence_state": method["evidence_state"],
            "call_permission": method["call_permission"],
            "reason": "领域匹配；方法文本匹配" if relevance else "领域匹配，需由总导演核对适用条件",
            "score": relevance,
        })
    selected.sort(key=lambda item: (-int(item["score"]), fields.index(str(item["field"])), str(item["method_id"])))
    return {
        "fields": fields,
        "selected": selected[:limit],
        "needs_information": not bool(selected),
        "reason": "只提供候选方法；正式使用前须读取对应 Skill 的限制与证据",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--index", type=Path, default=Path(__file__).resolve().parents[1] / "routing" / "methods-index.json")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    data = json.loads(args.index.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        parser.error("method index must be a JSON array")
    print(json.dumps(route(args.task, data, args.limit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
