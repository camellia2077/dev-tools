from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple


def calculate_header_comment(file_path: Path, relative_to: Path) -> str:
    """Calculate the expected leading relative-path comment."""
    try:
        relative_path = os.path.relpath(file_path.resolve(), relative_to.resolve())
        normalized_path = relative_path.replace(os.sep, "/")
        return f"// {normalized_path}\n"
    except ValueError:
        return f"// {file_path.name}\n"


def analyze_and_update_content(
    lines: List[str],
    expected_comment: str,
) -> Tuple[str, List[str], Optional[str]]:
    if not lines:
        return "added", [expected_comment], None

    first_line = lines[0]
    is_comment = re.match(r"^\s*//", first_line) is not None
    is_correct = first_line.strip() == expected_comment.strip()

    if is_comment:
        if not is_correct:
            new_lines = lines[:]
            new_lines[0] = expected_comment
            return "updated", new_lines, first_line.strip()
        return "skipped", lines, None

    new_lines = [expected_comment] + lines
    return "added", new_lines, None
