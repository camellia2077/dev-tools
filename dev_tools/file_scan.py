from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class FileScanOptions:
    scan_dir: Path
    extensions: tuple[str, ...]
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()


def iter_files(options: FileScanOptions) -> Iterator[Path]:
    scan_dir = options.scan_dir.resolve()
    for current_root, dirs, files in os.walk(scan_dir):
        root_path = Path(current_root)
        dirs[:] = sorted(
            directory
            for directory in dirs
            if not _matches_path(root_path / directory, scan_dir, options.exclude)
        )
        for file_name in sorted(files):
            path = root_path / file_name
            if path.suffix.lower() not in options.extensions:
                continue
            if _matches_path(path, scan_dir, options.exclude):
                continue
            if options.include and not _matches_path(path, scan_dir, options.include):
                continue
            yield path


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _matches_path(path: Path, root: Path, patterns: tuple[str, ...]) -> bool:
    if not patterns:
        return False

    rel_path = display_path(path, root)
    rel_dir = f"{rel_path}/" if path.is_dir() else rel_path
    candidates = {
        rel_path,
        rel_dir,
        path.name,
    }
    candidates.update(_build_segment_candidates(rel_path))
    return any(
        fnmatch.fnmatch(candidate, pattern)
        for pattern in patterns
        for candidate in candidates
    )


def _build_segment_candidates(rel_path: str) -> set[str]:
    if not rel_path or rel_path == ".":
        return set()
    parts = [part for part in rel_path.split("/") if part]
    candidates: set[str] = set()
    for index in range(len(parts)):
        suffix = "/".join(parts[index:])
        prefix = "/".join(parts[: index + 1])
        candidates.add(parts[index])
        candidates.add(prefix)
        candidates.add(suffix)
        candidates.add(f"**/{suffix}")
    return candidates
