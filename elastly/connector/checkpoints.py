"""Checkpoint stores: cursor persistence so an interrupted sync resumes, not restarts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional, Union


class InMemoryCheckpointStore:
    def __init__(self) -> None:
        self._cursors: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self._cursors.get(key)

    def set(self, key: str, cursor: Optional[str]) -> None:
        if cursor is None:
            self._cursors.pop(key, None)
        else:
            self._cursors[key] = cursor


class FileCheckpointStore:
    """JSON-file store; writes go to a temp file then an atomic rename."""

    def __init__(self, file_path: Union[str, "os.PathLike[str]"]) -> None:
        self._path = Path(file_path)

    def get(self, key: str) -> Optional[str]:
        return self._read().get(key)

    def set(self, key: str, cursor: Optional[str]) -> None:
        cursors = self._read()
        if cursor is None:
            cursors.pop(key, None)
        else:
            cursors[key] = cursor
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_name(f"{self._path.name}.tmp")
        temporary_path.write_text(json.dumps(cursors, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary_path, self._path)

    def _read(self) -> Dict[str, str]:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            return {}
        return {key: value for key, value in parsed.items() if isinstance(value, str)}
