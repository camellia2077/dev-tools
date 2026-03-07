from __future__ import annotations

from pathlib import Path

from . import logic


def process_single_file(
    file_path: Path,
    *,
    scan_dir: Path,
    relative_to: Path,
    mode: str,
) -> str:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read()

        current_guard, has_endif_comment = logic.extract_guard_info(content)
        rel_path = file_path.relative_to(scan_dir).as_posix()

        if not current_guard:
            print(f"[SKIP] {rel_path} (no standard include guard found)")
            return "SKIP"

        expected_guard = logic.calculate_expected_guard(file_path, relative_to)
        if current_guard == expected_guard:
            return "MATCH"

        if mode == "fix":
            print(f"[FIX] {rel_path}")
            print(f"    Old: {current_guard}")
            print(f"    New: {expected_guard}")
            new_content = logic.replace_guard_content(
                content,
                current_guard,
                expected_guard,
                has_endif_comment,
            )
            with file_path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(new_content)
            return "FIXED"

        prefix = "[DRY-RUN]" if mode == "dry-run" else "[CHECK]"
        print(f"{prefix} [MISMATCH] {rel_path}")
        print(f"    Expected: {expected_guard}")
        print(f"    Found   : {current_guard}")
        return "MISMATCH"
    except Exception as error:
        print(f"[ERROR] {file_path}: {error}")
        return "ERROR"
