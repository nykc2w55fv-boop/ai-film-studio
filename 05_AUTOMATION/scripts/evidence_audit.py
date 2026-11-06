"""Conservative, reproducible public-source audit for master methods.

Reachability and citation resolution alone never prove a creative claim.
This tool can assign PARTIAL, UNVERIFIED or an explicit conflict override;
SUPPORTED requires a separate evidence record with an anchored quotation
and attribution review. The source package is never modified.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from master_assets import ASSETS, RAW, normalized_methods, read_asset, sha256, source_index


PERMISSION = {
    "SUPPORTED": "NORMAL",
    "PARTIAL": "LIMITED",
    "UNVERIFIED": "SANDBOX",
    "CONFLICTED": "BLOCKED",
}
RANK = {"BLOCKED": 0, "SANDBOX": 1, "LIMITED": 2, "NORMAL": 3}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("redirect requires a separate URL audit")


def _public_url(url: str) -> tuple[bool, str]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False, "unsupported URL"
    if parsed.username or parsed.password:
        return False, "URL contains credentials"
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, None)}
    except OSError as exc:
        return False, f"DNS unavailable: {type(exc).__name__}"
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        return False, "non-public destination"
    return True, ""


def fetch_public(url: str, timeout: float = 4.0) -> dict[str, object]:
    """Fetch a bounded public HTML page without redirects or credentials."""
    checked_at = datetime.now(timezone.utc).isoformat()
    allowed, reason = _public_url(url)
    if not allowed:
        return {"url": url, "checked_at": checked_at, "reachable": False, "reason": reason}
    request = Request(url, headers={"User-Agent": "AI-Film-Studio-Evidence-Audit/1.0"})
    opener = build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            kind = response.headers.get_content_type()
            raw = response.read(1_000_001)
            status = response.status
            charset = response.headers.get_content_charset() or "utf-8"
    except (HTTPError, URLError, OSError, ValueError, ssl.SSLError) as exc:
        return {
            "url": url, "checked_at": checked_at, "reachable": False,
            "reason": f"{type(exc).__name__}: {str(exc)[:160]}",
        }
    if len(raw) > 1_000_000:
        return {"url": url, "checked_at": checked_at, "reachable": False, "reason": "page exceeds size limit"}
    if kind not in {"text/html", "text/plain"}:
        return {
            "url": url, "checked_at": checked_at, "reachable": True,
            "http_status": status, "content_type": kind, "content_sha256": sha256(raw),
            "excerpt": "", "reason": "non-text source requires separate verification",
        }
    decoded = raw.decode(charset, errors="replace")
    if kind == "text/html":
        extractor = _TextExtractor()
        extractor.feed(decoded)
        decoded = " ".join(extractor.parts)
    normalized = " ".join(decoded.split())
    return {
        "url": url, "checked_at": checked_at, "reachable": True,
        "http_status": status, "content_type": kind, "content_sha256": sha256(raw),
        "excerpt": normalized[:320], "reason": "reachability and excerpt only; semantic support unverified",
    }


def method_verdict(
    method: dict[str, object],
    sources: dict[str, list[str]],
    fetched: dict[str, dict[str, object]],
    override: dict[str, object] | None = None,
) -> dict[str, object]:
    ids = [str(value) for value in method.get("evidence_ids", [])]
    unresolved = [source_id for source_id in ids if not sources.get(source_id)]
    urls = sorted({url for source_id in ids for url in sources.get(source_id, [])})
    reachable = [url for url in urls if fetched.get(url, {}).get("reachable")]
    state = "PARTIAL" if reachable else "UNVERIFIED"
    rationale = (
        "已定位至少一个公开来源；方法含义与人物归因仍需锚定核查"
        if reachable else "未取得可复核的公开来源正文"
    )
    if unresolved:
        rationale += f"；未解析引用编号：{', '.join(unresolved)}"
    if override:
        requested = str(override.get("evidence_state", ""))
        if requested not in PERMISSION:
            raise ValueError(f"invalid evidence override: {requested}")
        if requested == "SUPPORTED":
            if not override.get("anchored_excerpt") or not override.get("attribution_basis"):
                raise ValueError("SUPPORTED requires anchored_excerpt and attribution_basis")
            if not reachable:
                raise ValueError("SUPPORTED requires a reachable recorded source")
        if requested == "CONFLICTED" and not override.get("conflict_sources"):
            raise ValueError("CONFLICTED requires conflict_sources")
        state = requested
        rationale = str(override.get("rationale") or "explicit audit record")
    permission = PERMISSION[state]
    if override and override.get("call_permission"):
        requested_permission = str(override["call_permission"])
        if requested_permission not in RANK or RANK[requested_permission] > RANK[permission]:
            raise ValueError("call permission may only be narrowed")
        permission = requested_permission
    return {
        "method_id": method["id"],
        "evidence_state": state,
        "call_permission": permission,
        "evidence_ids": ids,
        "unresolved_evidence_ids": unresolved,
        "source_urls": urls,
        "reachable_urls": reachable,
        "rationale": rationale,
        "source_file": method["source_file"],
        "source_heading": method["source_heading"],
        "critical_review": bool(override and override.get("critical_review")),
    }


def audit_all(
    raw_root: Path = RAW,
    online: bool = False,
    max_urls: int = 0,
    overrides: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    overrides = overrides or {}
    fetched: dict[str, dict[str, object]] = {}
    pending: list[tuple[str, dict[str, object], dict[str, list[str]]]] = []
    for asset in ASSETS:
        files, metadata = read_asset(asset, raw_root)
        texts = {
            name: data.decode("utf-8-sig")
            for name, data in files.items() if name.endswith(".md")
        }
        sources = source_index(texts)
        methods = normalized_methods(asset, files)
        for method in methods:
            urls = sorted({
                url
                for source_id in method["evidence_ids"]
                for url in sources.get(str(source_id), [])
            })
            for url in urls:
                if url in fetched:
                    continue
                fetched[url] = {
                    "url": url, "checked_at": None, "reachable": False,
                    "reason": "not fetched in this audit run",
                }
            pending.append((asset.slug, method, sources))
        metadata["method_count"] = len(methods)
    if online and max_urls:
        with ThreadPoolExecutor(max_workers=6) as pool:
            jobs = {pool.submit(fetch_public, url): url for url in list(fetched)[:max_urls]}
            for job in as_completed(jobs):
                url = jobs[job]
                try:
                    fetched[url] = job.result()
                except Exception as exc:
                    fetched[url] = {
                        "url": url, "checked_at": datetime.now(timezone.utc).isoformat(),
                        "reachable": False, "reason": f"unexpected {type(exc).__name__}",
                    }
    results: list[dict[str, object]] = []
    for slug, method, sources in pending:
        verdict = method_verdict(method, sources, fetched, overrides.get(str(method["id"])))
        verdict["master_slug"] = slug
        results.append(verdict)
    return {
        "schema_version": 1,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "online": online,
        "methods": results,
        "sources": sorted(fetched.values(), key=lambda item: str(item["url"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true", help="fetch cited public URLs")
    parser.add_argument("--max-urls", type=int, default=40)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overrides", type=Path, help="explicit, reviewable method verdicts")
    args = parser.parse_args()
    if args.max_urls < 0:
        parser.error("--max-urls must be non-negative")
    overrides = json.loads(args.overrides.read_text(encoding="utf-8")) if args.overrides else None
    result = audit_all(online=args.online, max_urls=args.max_urls, overrides=overrides)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            raise SystemExit(f"refusing to overwrite audit: {args.output}")
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded)
    states: dict[str, int] = {}
    for item in result["methods"]:
        states[item["evidence_state"]] = states.get(item["evidence_state"], 0) + 1
    print(f"audited {len(result['methods'])} methods, {len(result['sources'])} source URLs: {states}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
