#!/usr/bin/env python3
"""Search selected reference caches or the bundled design knowledge."""

from __future__ import annotations

import argparse
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
import re
from pathlib import Path

from bootstrap_motion_libraries import DEFAULT_ROOT, LIBRARIES, PRIMARY_SOURCES, WEB_SOURCES, library_kind, reference_origin
from check_installation import FEATURES

LIBS = tuple(LIBRARIES)
ALLOWED = {".md", ".json", ".tsx", ".ts", ".jsx", ".js", ".css"}


def terms(value: str) -> list[str]:
    return [item.lower() for item in re.findall(r"[\w\-]+", value, flags=re.UNICODE) if len(item) > 1]


def talkcraft_search(query: str, input_type: str | None = None, energy: str | None = None,
                     limit: int = 8) -> dict:
    """Search attributed metadata, never imply upstream code is bundled or runnable."""
    from query_knowledge import read, cues
    catalog = read("references/talkcraft-motions.json")
    needles = cues(query)
    matches = []
    for card in catalog["cards"]:
        if input_type and not any(input_type.casefold() in item.casefold() for item in card["inputs"]):
            continue
        if energy and energy.casefold() not in card["energy"].casefold():
            continue
        body = " ".join(str(card.get(k, "")) for k in
                        ("id", "name", "category", "semantics", "purpose")).casefold()
        score = sum(1 for needle in needles if needle in body)
        if needles and not score:
            continue
        matches.append(dict(card, score=score))
    matches.sort(key=lambda item: (-item["score"], item["id"]))
    return {"ok": True, "source": catalog["source"], "license": catalog["license"],
            "catalog_count": len(catalog["cards"]), "match_count": len(matches),
            "scope": "Local card/code paths are available; adapt selected components and dependencies. Upstream license applies.",
            "results": matches[:max(1, limit)]}


def analysis_catalog(root: Path) -> dict:
    """Full analysis inventory, independent of installed packages or cached text."""
    from bootstrap_motion_libraries import valid_repo
    from query_knowledge import sources, read
    inventory = sources()
    aliases = read("references/research-sources.json")["aliases"]
    entries = []
    for name in inventory:
        if name in aliases:
            continue
        source = inventory[name]
        entries.append({"source_id": name, "url": source["url"],
                        "scope": "primary" if name in PRIMARY_SOURCES or name in WEB_SOURCES else "supplementary",
                        "role": source.get("adoption", source.get("role", "See source routing")),
                        "integration": source.get("integration", "existing_reference"),
                        "cache_ready": valid_repo(root / name, name) if name in LIBS else False,
                        "analysis_status": "unassessed"})
    return {"scope": "Capability inventory; not proof of source reading, code adaptation or render validation.",
            "aliases": aliases, "sources": entries}


def main() -> int:
    parser = argparse.ArgumentParser(description="Search external motion libraries.")
    parser.add_argument("query", nargs="?")
    parser.add_argument("--knowledge", action="store_true", help="Search the bundled synthesized knowledge without an upstream cache.")
    parser.add_argument("--capabilities", action="store_true", help="Compact complete capability map for script analysis.")
    parser.add_argument("--card", help="Read one synthesized knowledge card by ID.")
    parser.add_argument("--source", help="Inspect an assessed source or alias; no download.")
    parser.add_argument("--materials", action="store_true", help="Search original material recipes instead of knowledge cards.")
    parser.add_argument("--talkcraft", action="store_true", help="Search the attributed TalkCraft motion-card metadata index.")
    parser.add_argument("--input", dest="input_type", help="TalkCraft input filter, e.g. 文 or 图.")
    parser.add_argument("--energy", help="TalkCraft energy filter, e.g. 低 or 中.")
    parser.add_argument("--catalog", action="store_true", help="List all analysis candidates without downloading or filtering by installed support.")
    parser.add_argument("--library", choices=("all",) + LIBS, default="all")
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--feature", action="append", choices=tuple(FEATURES), default=[],
                        help="Search only sources assigned to the selected content feature.")
    args = parser.parse_args()
    if args.talkcraft:
        if args.knowledge or args.capabilities or args.card or args.source or args.materials or args.catalog or args.feature or args.library != "all":
            parser.error("--talkcraft uses its own metadata index; do not combine it with other lookup modes.")
        try:
            result = talkcraft_search(args.query or "", args.input_type, args.energy, args.limit)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.input_type or args.energy:
        parser.error("--input and --energy require --talkcraft.")
    if args.knowledge or args.capabilities:
        from query_knowledge import search, capabilities
        if args.catalog or args.library != "all" or args.feature:
            parser.error("Knowledge lookup cannot be combined with upstream-cache filters or --catalog.")
        if args.capabilities and (args.knowledge or args.query or args.card or args.source or args.materials):
            parser.error("--capabilities is an unfiltered compact map.")
        if sum(bool(x) for x in (args.card, args.source, args.materials)) > 1:
            parser.error("Choose at most one of --card, --source, --materials.")
        try:
            result = {"capabilities": capabilities()} if args.capabilities else search(
                args.query or "", card_id=args.card, source_id=args.source,
                materials=args.materials, limit=args.limit)
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.card or args.source or args.materials:
        parser.error("--card, --source and --materials require --knowledge.")
    if args.catalog:
        if args.query or args.library != "all" or args.feature:
            parser.error("--catalog is an unfiltered inventory; do not combine with a query, --library or --feature.")
        print(json.dumps(analysis_catalog(args.cache_root.expanduser().resolve()), ensure_ascii=False, indent=2))
        return 0
    if not args.query:
        parser.error("Provide a query or --catalog.")
    needles = terms(args.query)
    if not needles:
        raise SystemExit("query has no searchable terms")
    selected = LIBS if args.library == "all" else (args.library,)
    if args.feature:
        relevant = {name for feature in args.feature for name in FEATURES[feature]["sources"]}
        selected = tuple(name for name in selected if name in relevant)
        if not selected:
            parser.error("No selected library belongs to these features.")
    hits = []
    root = args.cache_root.expanduser().resolve()
    for lib in selected:
        base = root / lib
        if not base.is_dir():
            continue
        if lib in WEB_SOURCES:
            index_path = base / "index.json"
            if not index_path.is_file():
                continue
            for entry in json.loads(index_path.read_text(encoding="utf-8")).get("entries", []):
                body = " ".join([entry.get("title", ""), entry.get("creator", ""), *entry.get("tags", [])]).lower()
                score = sum(min(body.count(n), 4) for n in needles)
                if score:
                    hits.append({"library":lib, "kind":"web-reference-index", "origin":"user_supplied",
                                 "score":score, "path":str(index_path), "relative_path":"index.json#" + entry["id"], **entry})
            continue
        if (base / "reference-snapshot" / "source.json").is_file():
            base = base / "reference-snapshot"
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in ALLOWED or any(p in path.parts for p in (".git", "node_modules", ".venv")):
                continue
            rel = path.relative_to(base).as_posix()
            try:
                body = path.read_text(encoding="utf-8", errors="ignore")[:12000].lower()
            except OSError:
                continue
            score = sum(8 for n in needles if n in rel.lower()) + sum(min(body.count(n), 4) for n in needles)
            if score:
                metadata = PRIMARY_SOURCES.get(lib, {})
                hits.append({"library": lib, "kind": library_kind(lib), "origin": reference_origin(lib), "score": score, "path": str(path), "relative_path": rel, "source_url": metadata.get("url", LIBRARIES[lib]), "license": metadata.get("license", "check upstream"), "audited_commit": metadata.get("audited_commit", "")})
    hits.sort(key=lambda item: (item["library"] not in PRIMARY_SOURCES and item["library"] not in WEB_SOURCES, -item["score"], item["library"], item["relative_path"]))
    missing = [lib for lib in selected if not (root / lib).is_dir()]
    print(json.dumps({"query": args.query, "features": args.feature, "selected_libraries": selected,
                      "scope": "cached text only, not live upstream search", "missing_cache": missing, "results": hits[: max(1, args.limit)]}, ensure_ascii=False, indent=2))
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
