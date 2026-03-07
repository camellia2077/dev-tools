from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dev_tools.file_scan import FileScanOptions, iter_files

from . import worker


@dataclass(frozen=True)
class ScanOptions:
    scan_dir: Path
    relative_to: Path
    extensions: tuple[str, ...]
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    mode: str


def scan_and_process_directory(options: ScanOptions) -> int:
    print(f"[SCAN] {options.scan_dir}")
    print(f"[MODE] {options.mode}")
    print(f"[RELATIVE_TO] {options.relative_to}")

    stats = {
        "MATCH": 0,
        "MISMATCH": 0,
        "FIXED": 0,
        "SKIP": 0,
        "ERROR": 0,
    }

    files = list(
        iter_files(
            FileScanOptions(
                scan_dir=options.scan_dir,
                extensions=options.extensions,
                include=options.include,
                exclude=options.exclude,
            )
        )
    )

    for file_path in files:
        status = worker.process_single_file(
            file_path,
            scan_dir=options.scan_dir,
            relative_to=options.relative_to,
            mode=options.mode,
        )
        stats[status] += 1

    print("\n================== Summary ==================")
    print(f"Scanned files : {len(files)}")
    print(f"Matched guards: {stats['MATCH']}")
    print(f"Mismatches    : {stats['MISMATCH']}")
    print(f"Fixed guards  : {stats['FIXED']}")
    print(f"Skipped files : {stats['SKIP']}")
    print(f"Errors        : {stats['ERROR']}")
    print("=============================================")

    if stats["ERROR"]:
        return 2
    if options.mode != "fix" and stats["MISMATCH"]:
        return 1
    return 0
