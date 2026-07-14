from __future__ import annotations

import json
import os
from pathlib import Path

from .model import TodoTree

SCHEMA_VERSION = 1

def data_path() -> Path:
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "tree-todo" / f"tasks-v{SCHEMA_VERSION}.json"

def save(tree: TodoTree, path: Path | None = None) -> Path:
    path = path or data_path(); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": SCHEMA_VERSION, **tree.snapshot()}, indent=2) + "\n")
    return path

def load(path: Path | None = None) -> TodoTree:
    path = path or data_path()
    if not path.exists(): return TodoTree()
    payload = json.loads(path.read_text())
    if payload.get("version") != SCHEMA_VERSION: raise ValueError("Unsupported task file version")
    return TodoTree.restore(payload)

def export_json(tree: TodoTree, path: Path) -> None: save(tree, path)

def import_json(path: Path) -> TodoTree: return load(path)
