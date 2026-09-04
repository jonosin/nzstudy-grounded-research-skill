#!/usr/bin/env python3
"""Small deterministic citation ledger for evidence-first research.

Inspired by NousResearch/hermes-agent grounded-citations (MIT).
This standalone adaptation keeps the core guarantees needed by NZ Study:
- stable URL -> [n] source IDs
- exact evidence quote validation
- mechanical Sources rendering
- draft verification for hallucinated IDs, URL drift, and missing evidence
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag

CITE_RE = re.compile(r"\[(\d{1,4})\](?![(:])")
SOURCE_RE = re.compile(r"^\s*\[(\d{1,4})\]\s+(https?://\S+)", re.M)
SOURCES_HEADER_RE = re.compile(r"^\s*(?:#{1,6}\s*)?Sources:?\s*$", re.I | re.M)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((?:[^()\s]|\([^()]*\))*\)")
MD_NOISE_RE = re.compile(r"[*_`~]|\\(?=[^\w\s])")


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def norm_url(url: str) -> str:
    url = (url or "").strip()
    clean, _ = urldefrag(url)
    clean = clean.rstrip("/")
    return clean or url


def match_key(text: str) -> str:
    text = MD_LINK_RE.sub(r"\1", text or "")
    text = MD_NOISE_RE.sub("", text)
    return " ".join(text.split()).casefold()


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "sources": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"cannot read ledger {path}: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        die(f"invalid ledger shape: {path}")
    return data


def save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_source(path: Path, url: str, title: str = "") -> dict[str, Any]:
    data = load(path)
    key = norm_url(url)
    for src in data["sources"]:
        if src["url"] == key:
            if title and not src.get("title"):
                src["title"] = title
                save(path, data)
            return src
    src = {"id": len(data["sources"]) + 1, "url": key, "title": title.strip(), "quotes": []}
    data["sources"].append(src)
    save(path, data)
    return src


def attach_quote(path: Path, source_id: int, quote: str, evidence: str) -> dict[str, Any]:
    quote = quote.strip()
    if len(quote.split()) < 3:
        die("quote is too short; use at least 3 words")
    qkey = match_key(quote)
    if not qkey or qkey not in match_key(evidence):
        die("quote not found in evidence text; copy exact wording from the retrieved page")
    data = load(path)
    src = next((s for s in data["sources"] if s["id"] == source_id), None)
    if src is None:
        die(f"no source [{source_id}] in ledger")
    quotes = src.setdefault("quotes", [])
    if not any(match_key(q.get("text", "")) == qkey for q in quotes):
        quotes.append({"text": quote})
        save(path, data)
    return src


def split_sources(text: str) -> tuple[str, dict[int, str]]:
    matches = list(SOURCES_HEADER_RE.finditer(text))
    if not matches:
        return text, {}
    m = matches[-1]
    body = text[:m.start()].rstrip()
    block = text[m.end():]
    listed = {int(i): norm_url(url) for i, url in SOURCE_RE.findall(block)}
    return body, listed


def render(data: dict[str, Any], ids: set[int] | None = None, evidence: bool = False) -> str:
    selected = [s for s in data["sources"] if ids is None or s["id"] in ids]
    selected.sort(key=lambda s: s["id"])
    lines = ["## Sources", ""]
    for src in selected:
        suffix = f" - {src['title']}" if src.get("title") else ""
        lines.append(f"[{src['id']}] {src['url']}{suffix}")
        if evidence:
            for q in src.get("quotes", []):
                lines.append(f"> \"{q['text']}\"")
    return "\n".join(lines).rstrip()


def verify(path: Path, draft: Path, require_evidence: bool) -> int:
    data = load(path)
    by_id = {s["id"]: s for s in data["sources"]}
    text = draft.read_text(encoding="utf-8")
    body, listed = split_sources(text)
    cited = {int(x) for x in CITE_RE.findall(body)}
    errors: list[str] = []

    unknown = sorted(cited - set(by_id))
    if unknown:
        errors.append("unknown citation IDs: " + ", ".join(f"[{x}]" for x in unknown))

    if cited and not listed:
        errors.append("draft has citations but no Sources block")

    for sid in sorted(cited):
        if sid not in listed:
            errors.append(f"citation [{sid}] is missing from Sources block")
            continue
        if sid in by_id and listed[sid] != by_id[sid]["url"]:
            errors.append(f"Sources URL for [{sid}] does not match ledger")
        if require_evidence and sid in by_id and not by_id[sid].get("quotes"):
            errors.append(f"source [{sid}] has no accepted evidence quote")

    extra = sorted(set(listed) - cited)
    if extra:
        errors.append("Sources block contains uncited IDs: " + ", ".join(f"[{x}]" for x in extra))

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        print("verification failed")
        return 1

    print(f"citations OK: {len(cited)} cited source(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Deterministic citation ledger for grounded research")
    p.add_argument("--ledger", required=True, help="path to task-local ledger.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reset")

    a = sub.add_parser("add")
    a.add_argument("url")
    a.add_argument("--title", default="")

    q = sub.add_parser("quote")
    q.add_argument("id", type=int)
    q.add_argument("--text", required=True)
    q.add_argument("--from", dest="evidence", required=True)

    sub.add_parser("list")

    r = sub.add_parser("render")
    r.add_argument("--style", choices=["markdown", "evidence"], default="markdown")
    r.add_argument("--only", default="")
    r.add_argument("--cited-in")
    r.add_argument("--replace-in")

    v = sub.add_parser("verify")
    v.add_argument("draft")
    v.add_argument("--evidence", action="store_true")

    args = p.parse_args(argv)
    ledger = Path(args.ledger)

    if args.cmd == "reset":
        save(ledger, {"version": 1, "sources": []})
        print(f"ledger reset: {ledger}")
        return 0

    if args.cmd == "add":
        src = add_source(ledger, args.url, args.title)
        print(f"[{src['id']}] {src['url']}")
        return 0

    if args.cmd == "quote":
        evidence = Path(args.evidence).read_text(encoding="utf-8")
        src = attach_quote(ledger, args.id, args.text, evidence)
        print(f"[{src['id']}] evidence attached")
        return 0

    data = load(ledger)

    if args.cmd == "list":
        print(json.dumps(data["sources"], indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "render":
        ids: set[int] | None = None
        draft_path = args.replace_in or args.cited_in
        if draft_path:
            body, _ = split_sources(Path(draft_path).read_text(encoding="utf-8"))
            ids = {int(x) for x in CITE_RE.findall(body)}
        if args.only:
            only = {int(x) for x in args.only.split(",") if x.strip()}
            ids = only if ids is None else ids & only
        block = render(data, ids=ids, evidence=args.style == "evidence")
        if args.replace_in:
            target = Path(args.replace_in)
            body, _ = split_sources(target.read_text(encoding="utf-8"))
            target.write_text(body.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
            print(f"Sources block rewritten in {target}")
        else:
            print(block)
        return 0

    if args.cmd == "verify":
        return verify(ledger, Path(args.draft), args.evidence)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
