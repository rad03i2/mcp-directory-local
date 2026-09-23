from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from .core import Directory, DirectoryError, validate_server

VERSION = "1.0.0"
DEFAULT = Path.home() / ".mcp-directory.json"

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mcp-directory", description="Local MCP server configuration registry")
    p.add_argument("--registry", type=Path, default=DEFAULT, help="registry JSON path")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="action", required=True)
    a = sub.add_parser("add", help="add a server from a JSON object/file"); a.add_argument("source"); a.add_argument("--replace", action="store_true")
    r = sub.add_parser("remove", help="remove a server"); r.add_argument("name")
    s = sub.add_parser("show", help="show one server"); s.add_argument("name")
    f = sub.add_parser("find", help="search servers"); f.add_argument("query", nargs="?", default=""); f.add_argument("--tag"); f.add_argument("--transport", choices=["stdio","http","https"]); f.add_argument("--json", action="store_true")
    e = sub.add_parser("export", help="export MCP client configuration"); e.add_argument("names", nargs="*"); e.add_argument("--output", type=Path)
    sub.add_parser("validate", help="validate the registry")
    return p

def _source(value: str) -> dict:
    path = Path(value)
    text = path.read_text(encoding="utf-8") if path.is_file() else value
    try: return json.loads(text)
    except json.JSONDecodeError as exc: raise DirectoryError(f"invalid server JSON: {exc}") from exc

def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        directory = Directory.load(args.registry)
        if args.action == "add":
            server = validate_server(_source(args.source)); directory.add(server, args.replace); directory.save(args.registry); print(f"Added {server.name}")
        elif args.action == "remove":
            server = directory.remove(args.name); directory.save(args.registry); print(f"Removed {server.name}")
        elif args.action == "show": print(json.dumps(directory.get(args.name).to_dict(), indent=2, ensure_ascii=False))
        elif args.action == "find":
            rows = directory.search(args.query, args.tag, args.transport)
            if args.json: print(json.dumps([x.to_dict() for x in rows], indent=2, ensure_ascii=False))
            else:
                for x in rows: print(f"{x.name}\t{x.transport}\t{', '.join(x.tags) or '-'}\t{x.description}")
        elif args.action == "export":
            payload = json.dumps(directory.export_client_config(args.names or None), indent=2, ensure_ascii=False) + "\n"
            if args.output:
                args.output.write_text(payload, encoding="utf-8"); print(f"Wrote {args.output}")
            else: print(payload, end="")
        elif args.action == "validate": print(f"OK: {len(directory.search())} server(s)")
        return 0
    except (DirectoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
