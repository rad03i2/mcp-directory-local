from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
TRANSPORTS = {"stdio", "http", "https"}

class DirectoryError(ValueError):
    """Raised for invalid registry data or operations."""

@dataclass(frozen=True)
class Server:
    name: str
    description: str
    transport: str
    command: str | None = None
    args: tuple[str, ...] = ()
    url: str | None = None
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["args"] = list(self.args)
        data["tags"] = list(self.tags)
        return data


def validate_server(data: dict[str, Any]) -> Server:
    if not isinstance(data, dict):
        raise DirectoryError("server must be an object")
    name = data.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise DirectoryError("name must be 1-64 safe characters: letters, digits, dot, underscore, hyphen")
    description = data.get("description", "")
    if not isinstance(description, str) or len(description) > 500:
        raise DirectoryError("description must be a string up to 500 characters")
    transport = data.get("transport")
    if transport not in TRANSPORTS:
        raise DirectoryError("transport must be stdio, http, or https")
    command, url = data.get("command"), data.get("url")
    args, tags = data.get("args", []), data.get("tags", [])
    if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
        raise DirectoryError("args must be an array of strings")
    if not isinstance(tags, list) or not all(isinstance(x, str) and x.strip() for x in tags):
        raise DirectoryError("tags must be an array of non-empty strings")
    if transport == "stdio":
        if not isinstance(command, str) or not command.strip() or url is not None:
            raise DirectoryError("stdio requires command and forbids url")
    else:
        if command is not None or not isinstance(url, str) or not url.startswith(transport + "://"):
            raise DirectoryError(f"{transport} requires a matching URL and forbids command")
    return Server(name, description.strip(), transport, command, tuple(args), url, tuple(sorted(set(t.strip().lower() for t in tags))))

class Directory:
    def __init__(self, servers: list[Server] | None = None):
        self._servers = {s.name: s for s in (servers or [])}

    @classmethod
    def load(cls, path: str | Path) -> "Directory":
        p = Path(path)
        if not p.exists():
            return cls()
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DirectoryError(f"cannot read registry: {exc}") from exc
        if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("servers"), list):
            raise DirectoryError("registry must contain version 1 and a servers array")
        servers = [validate_server(x) for x in raw["servers"]]
        if len({s.name for s in servers}) != len(servers):
            raise DirectoryError("duplicate server name")
        return cls(servers)

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "servers": [s.to_dict() for s in sorted(self._servers.values(), key=lambda x: x.name.lower())]}
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(p)

    def add(self, server: Server, replace: bool = False) -> None:
        if server.name in self._servers and not replace:
            raise DirectoryError(f"server already exists: {server.name}")
        self._servers[server.name] = server

    def remove(self, name: str) -> Server:
        try:
            return self._servers.pop(name)
        except KeyError as exc:
            raise DirectoryError(f"server not found: {name}") from exc

    def get(self, name: str) -> Server:
        if name not in self._servers:
            raise DirectoryError(f"server not found: {name}")
        return self._servers[name]

    def search(self, query: str = "", tag: str | None = None, transport: str | None = None) -> list[Server]:
        q = query.casefold().strip()
        tag_norm = tag.casefold().strip() if tag else None
        result = []
        for server in self._servers.values():
            haystack = " ".join((server.name, server.description, *server.tags)).casefold()
            if q and q not in haystack:
                continue
            if tag_norm and tag_norm not in server.tags:
                continue
            if transport and server.transport != transport:
                continue
            result.append(server)
        return sorted(result, key=lambda x: x.name.casefold())

    def export_client_config(self, names: list[str] | None = None) -> dict[str, Any]:
        selected = [self.get(n) for n in names] if names else self.search()
        out: dict[str, Any] = {}
        for s in selected:
            if s.transport == "stdio":
                out[s.name] = {"command": s.command, "args": list(s.args)}
            else:
                out[s.name] = {"url": s.url}
        return {"mcpServers": out}
