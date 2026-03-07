from __future__ import annotations

import argparse
import difflib
import re
from dataclasses import dataclass
from pathlib import Path

from dev_tools.config import (
    load_config,
    normalize_extensions,
    normalize_patterns,
    resolve_path,
    validate_mode,
)
from dev_tools.file_scan import FileScanOptions, display_path, iter_files


DEFAULT_EXTENSIONS = (".h", ".hpp", ".cpp", ".c", ".cc", ".hh")
INCLUDE_PATTERN = re.compile(r'#include\s+"([^/\\\s]+\.(?:hpp|h|cpp|c|cc|hh))"')


@dataclass(frozen=True)
class FixIncludeOptions:
    scan_dir: Path
    relative_to: Path
    extensions: tuple[str, ...]
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    mode: str


@dataclass
class FixIncludeReport:
    scanned: int = 0
    changed_files: int = 0
    mismatches: int = 0
    errors: int = 0


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.description = "Check or fix C/C++ include paths to be relative to a source root."
    parser.add_argument(
        "scan_dir",
        nargs="?",
        default=None,
        help="Directory containing source files to rewrite.",
    )
    parser.add_argument(
        "--relative-to",
        default=None,
        help="Base directory used to build the include path index and rewritten relative paths.",
    )
    parser.add_argument(
        "--extensions",
        "--ext",
        nargs="+",
        default=None,
        help="Target file extensions, e.g. .hpp .cpp .h .c",
    )
    parser.add_argument("--include", nargs="+", default=None, help="Optional include globs.")
    parser.add_argument("--exclude", nargs="+", default=None, help="Optional exclude globs.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--check", action="store_true", help="Check only.")
    mode_group.add_argument("--fix", action="store_true", help="Apply include fixes in place.")
    mode_group.add_argument("--dry-run", action="store_true", help="Preview diffs without writing.")
    parser.add_argument("--config", default=None, help="Optional dev-tools.toml path.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fix-include")
    add_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_from_namespace(args)


def run_from_namespace(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    config_start_dir = _resolve_config_start_dir(args.scan_dir, cwd)
    config = load_config(args.config, config_start_dir)

    scan_dir = resolve_path(
        args.scan_dir or config.fix_include.scan_dir,
        cwd=cwd,
        config_path=config.path,
    ) or cwd
    relative_to = resolve_path(
        args.relative_to or config.fix_include.relative_to,
        cwd=cwd,
        config_path=config.path,
    ) or scan_dir
    options = FixIncludeOptions(
        scan_dir=scan_dir,
        relative_to=relative_to,
        extensions=normalize_extensions(
            args.extensions if args.extensions is not None else config.fix_include.extensions,
            DEFAULT_EXTENSIONS,
        ),
        include=normalize_patterns(
            args.include if args.include is not None else config.fix_include.include
        ),
        exclude=normalize_patterns(
            args.exclude if args.exclude is not None else config.fix_include.exclude
        ),
        mode=validate_mode(_resolve_mode(args, config.fix_include.mode), "check"),
    )

    if not options.scan_dir.is_dir():
        print(f"[ERROR] Directory not found: {options.scan_dir}")
        return 2
    if not options.relative_to.is_dir():
        print(f"[ERROR] Relative-base directory not found: {options.relative_to}")
        return 2

    return run_fix_include(options)


def run_fix_include(options: FixIncludeOptions) -> int:
    print(f"[SCAN] {options.scan_dir}")
    print(f"[MODE] {options.mode}")
    print(f"[RELATIVE_TO] {options.relative_to}")

    file_map = build_file_map(options)
    report = FixIncludeReport()

    scan_options = FileScanOptions(
        scan_dir=options.scan_dir,
        extensions=options.extensions,
        include=options.include,
        exclude=options.exclude,
    )
    for file_path in iter_files(scan_options):
        report.scanned += 1
        status = process_single_file(file_path, options=options, file_map=file_map)
        if status == "changed":
            report.changed_files += 1
            report.mismatches += 1
        elif status == "mismatch":
            report.mismatches += 1
        elif status == "error":
            report.errors += 1

    print("\n================== Summary ==================")
    print(f"Scanned files : {report.scanned}")
    print(f"Mismatches    : {report.mismatches}")
    print(f"Changed files : {report.changed_files}")
    print(f"Errors        : {report.errors}")
    print("=============================================")

    if report.errors:
        return 2
    if options.mode != "fix" and report.mismatches:
        return 1
    return 0


def build_file_map(options: FixIncludeOptions) -> dict[str, str]:
    file_map: dict[str, str] = {}
    scan_options = FileScanOptions(
        scan_dir=options.relative_to,
        extensions=options.extensions,
        include=(),
        exclude=options.exclude,
    )
    for path in iter_files(scan_options):
        rel_path = path.relative_to(options.relative_to).as_posix()
        file_map[path.name] = rel_path
    return file_map


def process_single_file(
    file_path: Path,
    *,
    options: FixIncludeOptions,
    file_map: dict[str, str],
) -> str:
    try:
        content = read_source_file(file_path)
    except OSError as error:
        print(f"[ERROR] {display_path(file_path, options.scan_dir)}: {error}")
        return "error"

    old_lines, new_lines, modified = fix_include_lines(content, file_map)
    if not modified:
        return "ok"

    rel_path = display_path(file_path, options.scan_dir)
    prefix = {
        "fix": "[FIX]",
        "check": "[CHECK]",
        "dry-run": "[DRY-RUN]",
    }[options.mode]
    print(f"{prefix} {rel_path}")

    if options.mode in {"fix", "dry-run"}:
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path.name}",
            tofile=f"b/{file_path.name}",
        )
        print("".join(diff))

    if options.mode == "fix":
        try:
            file_path.write_text("".join(new_lines), encoding="utf-8", newline="\n")
        except OSError as error:
            print(f"[ERROR] {rel_path}: {error}")
            return "error"
        return "changed"
    return "mismatch"


def read_source_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="gbk")


def fix_include_lines(content: str, file_map: dict[str, str]) -> tuple[list[str], list[str], bool]:
    old_lines = content.splitlines(keepends=True)
    new_lines: list[str] = []
    modified = False

    for line in old_lines:
        match = INCLUDE_PATTERN.search(line)
        if match:
            filename = match.group(1)
            if filename in file_map:
                new_path = file_map[filename]
                if new_path != filename:
                    new_lines.append(line.replace(f'"{filename}"', f'"{new_path}"'))
                    modified = True
                    continue
        new_lines.append(line)
    return old_lines, new_lines, modified


def _resolve_mode(args: argparse.Namespace, config_mode: str | None) -> str | None:
    if args.fix:
        return "fix"
    if args.dry_run:
        return "dry-run"
    if args.check:
        return "check"
    return config_mode


def _resolve_config_start_dir(scan_dir: str | None, cwd: Path) -> Path:
    if not scan_dir:
        return cwd
    candidate = Path(scan_dir)
    if not candidate.is_absolute():
        candidate = (cwd / candidate).resolve()
    else:
        candidate = candidate.resolve()
    return candidate if candidate.is_dir() else candidate.parent
