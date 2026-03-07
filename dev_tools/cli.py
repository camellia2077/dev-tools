from __future__ import annotations

import argparse

from apps.auto_comments.header_tool.cli import add_arguments as add_auto_comments_arguments
from apps.auto_comments.header_tool.cli import run_from_namespace as run_auto_comments
from apps.find_hpp.pch_gen.main import add_arguments as add_find_hpp_arguments
from apps.find_hpp.pch_gen.main import run_from_namespace as run_find_hpp
from apps.fix_include.fix_include.main import add_arguments as add_fix_include_arguments
from apps.fix_include.fix_include.main import run_from_namespace as run_fix_include
from apps.hpp_guard.hpp_guard.main import add_arguments as add_hpp_guard_arguments
from apps.hpp_guard.hpp_guard.main import run_from_namespace as run_hpp_guard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified CLI for reusable development tools."
    )
    subparsers = parser.add_subparsers(dest="command")

    auto_comments_parser = subparsers.add_parser(
        "auto-comments",
        help="Check or update source header path comments.",
    )
    add_auto_comments_arguments(auto_comments_parser)
    auto_comments_parser.set_defaults(handler=run_auto_comments)

    hpp_guard_parser = subparsers.add_parser(
        "hpp-guard",
        help="Check or fix header include guards.",
    )
    add_hpp_guard_arguments(hpp_guard_parser)
    hpp_guard_parser.set_defaults(handler=run_hpp_guard)

    fix_include_parser = subparsers.add_parser(
        "fix-include",
        help="Check or fix relative project include paths.",
    )
    add_fix_include_arguments(fix_include_parser)
    fix_include_parser.set_defaults(handler=run_fix_include)

    find_hpp_parser = subparsers.add_parser(
        "find-hpp",
        help="Generate a PCH/include recommendation report.",
    )
    add_find_hpp_arguments(find_hpp_parser)
    find_hpp_parser.set_defaults(handler=run_find_hpp)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    return int(handler(args))
