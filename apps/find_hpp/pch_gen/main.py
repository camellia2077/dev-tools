from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from dev_tools.config import (
    load_config,
    normalize_extensions,
    normalize_names,
    normalize_patterns,
    resolve_path,
)
from dev_tools.file_scan import FileScanOptions, iter_files

from . import config
from .core.analyzer import ReportGenerator
from .core.classifier import HeaderClassifier
from .core.parser import HeaderParser
from .io.writer import write_pch_content


DEFAULT_EXTENSIONS = (".cpp", ".hpp", ".h", ".cc", ".cxx", ".c")
DEFAULT_EXCLUDE_NAMES = ("pch.hpp", "cmake_pch.hxx")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.description = "Generate a PCH recommendation report from include usage."
    parser.add_argument(
        "scan_dir",
        nargs="?",
        default=None,
        help="Source directory to analyze.",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=None,
        help="Number of top include entries to report.",
    )
    parser.add_argument(
        "--extensions",
        "--ext",
        nargs="+",
        default=None,
        help="Source file extensions to analyze.",
    )
    parser.add_argument("--include", nargs="+", default=None, help="Optional include globs.")
    parser.add_argument("--exclude", nargs="+", default=None, help="Optional exclude globs.")
    parser.add_argument(
        "--exclude-names",
        nargs="+",
        default=None,
        help="File names to ignore entirely, e.g. pch.hpp cmake_pch.hxx",
    )
    parser.add_argument(
        "--extra-libs",
        nargs="+",
        default=None,
        help="Additional third-party prefixes, e.g. mylib/",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output file path. Defaults to stdout.",
    )
    parser.add_argument("--config", default=None, help="Optional dev-tools.toml path.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="find-hpp")
    add_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_from_namespace(args)


def run_from_namespace(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    config_start_dir = _resolve_config_start_dir(args.scan_dir, cwd)
    loaded_config = load_config(args.config, config_start_dir)

    scan_dir = resolve_path(
        args.scan_dir or loaded_config.find_hpp.scan_dir,
        cwd=cwd,
        config_path=loaded_config.path,
    ) or cwd
    if not scan_dir.is_dir():
        print(f"[ERROR] Directory not found: {scan_dir}", file=sys.stderr)
        return 2

    top = args.top if args.top is not None else loaded_config.find_hpp.top or 50
    if top <= 0:
        print("[ERROR] --top must be a positive integer", file=sys.stderr)
        return 2

    extensions = normalize_extensions(
        args.extensions if args.extensions is not None else loaded_config.find_hpp.extensions,
        DEFAULT_EXTENSIONS,
    )
    include = normalize_patterns(
        args.include if args.include is not None else loaded_config.find_hpp.include
    )
    exclude = normalize_patterns(
        args.exclude if args.exclude is not None else loaded_config.find_hpp.exclude
    )
    exclude_names = normalize_names(
        args.exclude_names
        if args.exclude_names is not None
        else loaded_config.find_hpp.exclude_names
    ) or DEFAULT_EXCLUDE_NAMES
    extra_libs = tuple(
        args.extra_libs if args.extra_libs is not None else loaded_config.find_hpp.extra_libs
    )
    output_path = resolve_path(
        args.output or loaded_config.find_hpp.output,
        cwd=cwd,
        config_path=loaded_config.path,
    )

    return run_find_hpp(
        scan_dir=scan_dir,
        top=top,
        extensions=extensions,
        include=include,
        exclude=exclude,
        exclude_names=exclude_names,
        extra_libs=extra_libs,
        output_path=output_path,
    )


def run_find_hpp(
    *,
    scan_dir: Path,
    top: int,
    extensions: tuple[str, ...],
    include: tuple[str, ...],
    exclude: tuple[str, ...],
    exclude_names: tuple[str, ...],
    extra_libs: tuple[str, ...],
    output_path: Path | None,
) -> int:
    parser = HeaderParser()
    classifier = HeaderClassifier(
        config.CPP_STANDARD_HEADERS,
        config.DEFAULT_THIRD_PARTY_IDENTIFIERS + list(extra_libs),
    )
    analyzer = ReportGenerator(classifier)

    print(f"[SCAN] {scan_dir}", file=sys.stderr)

    stats = Counter()
    scan_options = FileScanOptions(
        scan_dir=scan_dir,
        extensions=extensions,
        include=include,
        exclude=exclude,
    )
    for file_path in iter_files(scan_options):
        if file_path.name.lower() in exclude_names:
            continue
        try:
            with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
                headers = parser.parse_content(handle.read())
        except OSError:
            continue
        stats.update(headers)

    if not stats:
        print("[WARN] No #include directives found.", file=sys.stderr)
        return 1

    report = analyzer.generate_report(stats.most_common(top))
    if output_path is None:
        write_pch_content(report, stream=sys.stdout)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        write_pch_content(report, stream=handle)
    print(f"[OUTPUT] {output_path}", file=sys.stderr)
    return 0


def _resolve_config_start_dir(scan_dir: str | None, cwd: Path) -> Path:
    if not scan_dir:
        return cwd
    candidate = Path(scan_dir)
    if not candidate.is_absolute():
        candidate = (cwd / candidate).resolve()
    else:
        candidate = candidate.resolve()
    return candidate if candidate.is_dir() else candidate.parent
