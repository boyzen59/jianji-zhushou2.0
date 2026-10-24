#!/usr/bin/env python3
"""Check/cache selected upstream reference text for Remotion production."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import hashlib
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError
from prompt_motion_index import cache_index, valid_index
from datetime import datetime
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "references" / "motion-sources.json"
PRIMARY_SOURCES = {item["id"]: item for item in json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["sources"]}
WEB_SOURCES = {item["id"]: item for item in json.loads(REGISTRY_PATH.read_text(encoding="utf-8")).get("web_sources", [])}
LIBRARIES = {**{name: item["url"] for name, item in PRIMARY_SOURCES.items()},
             **{name: item["url"] for name, item in WEB_SOURCES.items()}}
DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "modules" / "upstream"
def library_kind(name: str) -> str:
    if name in WEB_SOURCES:
        return "web-reference-index"
    return "motion-reference"


def reference_origin(name: str) -> str:
    if name in PRIMARY_SOURCES or name in WEB_SOURCES:
        return "user_supplied"
    return "supplementary"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=180)


def valid_repo(path: Path, name: str = "") -> bool:
    if name in WEB_SOURCES:
        return valid_index(path)
    for snapshot in (path, path / "reference-snapshot"):
        marker = snapshot / "source.json"
        if name in PRIMARY_SOURCES and marker.is_file():
            try:
                record = json.loads(marker.read_text(encoding="utf-8"))
                files = record["files"]
                return (record.get("url") == PRIMARY_SOURCES[name]["url"] and
                        bool(files) and all(item in files for item in PRIMARY_SOURCES[name]["required_files"]) and
                        all((snapshot / item).is_file() and
                            hashlib.sha256((snapshot / item).read_bytes()).hexdigest() == digest
                            for item, digest in files.items()))
            except (OSError, ValueError, KeyError, TypeError):
                return False
    if not (path / ".git").exists():
        return False
    if name in PRIMARY_SOURCES:
        return all((path / item).is_file() for item in PRIMARY_SOURCES[name]["required_files"])
    useful = list(path.rglob("*.tsx")) + list(path.rglob("*.jsx")) + list(path.rglob("*.md"))
    return len(useful) >= 3


def download_reference_snapshot(name: str, target: Path) -> dict:
    """Pinned text-only cache; no code execution, media download, or overwrite of Git files."""
    source = PRIMARY_SOURCES[name]
    if (target / "source.json").is_file():
        return {"action": "local-module-retained", "error": "" if valid_repo(target, name) else "Local module changed; preserve edits and use sync_sources.py."}
    snapshot = target / "reference-snapshot"
    marker = snapshot / "source.json"
    if marker.is_file():
        return {"action": "snapshot-retained", "error": "" if valid_repo(target, name) else
                "Snapshot differs from its recorded hashes; preserve edits and use a fresh --cache-root."}
    snapshot.mkdir(parents=True, exist_ok=True)
    base = source["url"].removeprefix("https://github.com/").removesuffix(".git")
    files, downloaded = {}, {}
    for relative in source["reference_files"]:
        destination = snapshot / relative
        # Preserve partially downloaded or locally edited files rather than overwrite them.
        if destination.exists():
            return {"action": "snapshot-partial", "error": f"Partial file already exists: {destination}; use a fresh --cache-root."}
        url = f"https://raw.githubusercontent.com/{base}/{source['audited_commit']}/{quote(relative, safe='/')}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "jianji-reference-cache/3.1"}), timeout=25) as response:
                body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise ValueError(f"Reference exceeds 2 MB: {relative}")
            body.decode("utf-8")  # This cache intentionally excludes binary media.
        except (OSError, URLError, ValueError) as exc:
            return {"action": "snapshot-partial", "error": f"{relative}: {exc}"}
        downloaded[relative] = body
        files[relative] = hashlib.sha256(body).hexdigest()
    for relative, body in downloaded.items():
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
    record = {"url": source["url"], "head": source["audited_commit"], "license": source["license"], "files": files}
    marker.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"action": "snapshot-downloaded", "error": ""}


def main() -> int:
    parser = argparse.ArgumentParser(description="Cache/check selected upstream reference text; final composition uses Remotion.")
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--library", choices=("all",) + tuple(LIBRARIES), default="all")
    parser.add_argument("--install-missing", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--text-only", action="store_true", help="Cache a small pinned reference snapshot over HTTPS, without Git or media.")
    parser.add_argument("--git", help="Explicit git executable")
    args = parser.parse_args()

    if args.library == "all" and (args.install_missing or args.update):
        parser.error("Select one --library for download/update after reading its reference and license; all is read-only")
    if args.text_only and (args.library not in PRIMARY_SOURCES or not args.install_missing or args.update):
        parser.error("--text-only requires one primary --library and --install-missing, without --update")

    git = args.git or shutil.which("git")
    if not git and not args.text_only and args.library not in WEB_SOURCES:
        raise SystemExit("git is required; install Git or pass --git with an absolute path")
    root = args.cache_root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in LIBRARIES.items():
        if args.library != "all" and name != args.library:
            continue
        target = root / name
        action = "checked"
        error = ""
        if name in WEB_SOURCES and (args.install_missing or args.update):
            try:
                snapshot_result = cache_index(target)
                action, error = snapshot_result["action"], snapshot_result["error"]
            except (OSError, ValueError) as exc:
                action, error = "web-index-failed", str(exc)
        elif args.text_only:
            snapshot_result = download_reference_snapshot(name, target)
            action, error = snapshot_result["action"], snapshot_result["error"]
        elif not target.exists() and args.install_missing:
            metadata = PRIMARY_SOURCES.get(name, {})
            patterns = metadata.get("sparse_patterns", [])
            commands = [[git, "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", url, str(target)],
                        [git, "-C", str(target), "sparse-checkout", "set", "--no-cone", *patterns],
                        [git, "-C", str(target), "checkout"]] if patterns else [[git, "clone", "--depth", "1", url, str(target)]]
            action = "sparse-cloned" if patterns else "cloned"
            try:
                for command in commands:
                    result = run(command)
                    if result.returncode:
                        error = result.stderr.strip() or result.stdout.strip()
                        break
            except subprocess.TimeoutExpired:
                error = "Download timed out; partial cache retained for inspection, not marked ready."
        elif target.exists() and args.update:
            state = run([git, "-C", str(target), "status", "--porcelain"])
            remote = run([git, "-C", str(target), "remote", "get-url", "origin"])
            if state.returncode or state.stdout.strip():
                error = "Refusing update: not a clean Git checkout; preserve local changes."
            elif remote.returncode or remote.stdout.strip().removesuffix(".git").rstrip("/") != url.removesuffix(".git"):
                error = "Refusing update: origin does not match the registered source."
            else:
                try:
                    result = run([git, "-C", str(target), "pull", "--ff-only"])
                    action = "updated"
                    if result.returncode:
                        error = result.stderr.strip() or result.stdout.strip()
                except subprocess.TimeoutExpired:
                    error = "Update timed out; inspect the retained checkout before retrying."
        ok = valid_repo(target, name) and not error
        head = ""
        if ok and (target / "source.json").is_file():
            head = json.loads((target / "source.json").read_text(encoding="utf-8")).get("revision", "")
        elif ok and (target / "reference-snapshot" / "source.json").is_file():
            head = json.loads((target / "reference-snapshot" / "source.json").read_text(encoding="utf-8"))["head"]
        elif ok and name not in WEB_SOURCES:
            result = run([git, "-C", str(target), "rev-parse", "HEAD"])
            if result.returncode == 0:
                head = result.stdout.strip()
        record = {"name": name, "kind": library_kind(name), "origin": reference_origin(name), "url": url, "path": str(target), "ok": ok, "action": action, "head": head, "error": error}
        if name in PRIMARY_SOURCES:
            source = PRIMARY_SOURCES[name]
            record.update({"license": source["license"], "audited_commit": source["audited_commit"],
                           "matches_audit": head == source["audited_commit"] if head else None,
                           "cache_scope": "reference files; upstream demos may need additional assets",
                           "direct_import_ready": False})
        if name in WEB_SOURCES:
            record.update({"license": WEB_SOURCES[name]["license"], "cache_scope": "entry metadata only; no media copied",
                           "direct_import_ready": False})
        records.append(record)

    manifest = {
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "cache_root": str(root),
        "libraries": records,
    }
    # Independent selected caches can be prepared concurrently without clobbering each other's manifests.
    manifest_path = root / ("motion-libraries.json" if args.library == "all" else f"{args.library}.cache.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] for item in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
