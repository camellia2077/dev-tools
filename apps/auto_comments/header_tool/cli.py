from __future__ import annotations

import argparse
from pathlib import Path

from dev_tools.config import (
    load_config,
    normalize_extensions,
    normalize_patterns,
    resolve_path,
    validate_mode,
)

from .processor import BatchProcessor, BatchProcessorOptions


DEFAULT_EXTENSIONS = (".hpp", ".cpp", ".h", ".c")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.description = "Check or update leading source-path comments."
    parser.add_argument(
        "scan_dir",
        nargs="?",
        default=None,
        help="Directory to scan. Falls back to dev-tools.toml or the current directory.",
    )
    parser.add_argument(
        "--relative-to",
        default=None,
        help="Base directory used to compute the relative header comment.",
    )
    parser.add_argument(
        "--extensions",
        "--ext",
        nargs="+",
        default=None,
        help="Target file extensions, e.g. .hpp .cpp .h .c",
    )
    parser.add_argument(
        "--include",
        nargs="+",
        default=None,
        help="Optional include glob patterns relative to scan_dir.",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=None,
        help="Optional exclude glob patterns relative to scan_dir.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--check", action="store_true", help="Check only.")
    mode_group.add_argument("--fix", action="store_true", help="Apply changes in place.")
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional dev-tools.toml path. Defaults to the nearest config from scan_dir/current directory.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="auto-comments")
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
        args.scan_dir or config.auto_comments.scan_dir,
        cwd=cwd,
        config_path=config.path,
    ) or cwd
    relative_to = resolve_path(
        args.relative_to or config.auto_comments.relative_to,
        cwd=cwd,
        config_path=config.path,
    ) or scan_dir
    extensions = normalize_extensions(
        args.extensions if args.extensions is not None else config.auto_comments.extensions,
        DEFAULT_EXTENSIONS,
    )
    include = normalize_patterns(
        args.include if args.include is not None else config.auto_comments.include
    )
    exclude = normalize_patterns(
        args.exclude if args.exclude is not None else config.auto_comments.exclude
    )
    mode = validate_mode(_resolve_mode(args, config.auto_comments.mode), "check")

    processor = BatchProcessor(
        BatchProcessorOptions(
            scan_dir=scan_dir,
            relative_to=relative_to,
            extensions=extensions,
            include=include,
            exclude=exclude,
            mode=mode,
        )
    )
    try:
        return processor.process()
    except Exception as error:
        print(f"[ERROR] {error}")
        return 2


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
