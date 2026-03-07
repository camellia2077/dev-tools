from __future__ import annotations

from pathlib import Path
from typing import List


def read_file_lines(file_path: Path) -> List[str]:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.readlines()
    except OSError as error:
        raise OSError(f"Error reading {file_path}: {error}") from error


def write_file_lines(file_path: Path, lines: List[str]) -> None:
    try:
        with file_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.writelines(lines)
    except OSError as error:
        raise OSError(f"Error writing {file_path}: {error}") from error
