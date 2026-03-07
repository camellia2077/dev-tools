from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dev_tools.file_scan import FileScanOptions, display_path, iter_files

from . import core, fs_utils


@dataclass(frozen=True)
class BatchProcessorOptions:
    scan_dir: Path
    relative_to: Path
    extensions: tuple[str, ...]
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    mode: str


@dataclass
class BatchProcessorReport:
    scanned: int = 0
    added: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0

    @property
    def changes(self) -> int:
        return self.added + self.updated


class BatchProcessor:
    def __init__(self, options: BatchProcessorOptions):
        self.options = options
        self.stats = BatchProcessorReport()

    def process(self) -> int:
        if not self.options.scan_dir.is_dir():
            raise FileNotFoundError(f"Directory not found: {self.options.scan_dir}")
        if not self.options.relative_to.exists():
            raise FileNotFoundError(
                f"Relative-base path not found: {self.options.relative_to}"
            )

        print(f"[SCAN] {self.options.scan_dir}")
        print(f"[MODE] {self.options.mode}")
        print(f"[RELATIVE_TO] {self.options.relative_to}")

        scan_options = FileScanOptions(
            scan_dir=self.options.scan_dir,
            extensions=self.options.extensions,
            include=self.options.include,
            exclude=self.options.exclude,
        )
        for file_path in iter_files(scan_options):
            self._handle_single_file(file_path)

        self._print_summary()
        if self.stats.errors:
            return 2
        if self.options.mode != "fix" and self.stats.changes:
            return 1
        return 0

    def _handle_single_file(self, file_path: Path) -> None:
        self.stats.scanned += 1
        rel_path = display_path(file_path, self.options.scan_dir)

        try:
            lines = fs_utils.read_file_lines(file_path)
            expected_comment = core.calculate_header_comment(
                file_path=file_path,
                relative_to=self.options.relative_to,
            )
            status, new_lines, old_comment = core.analyze_and_update_content(
                lines,
                expected_comment,
            )
        except OSError as error:
            print(f"[ERROR] {rel_path}: {error}")
            self.stats.errors += 1
            return

        if status == "added":
            self.stats.added += 1
            self._report_change(
                rel_path=rel_path,
                label="ADD",
                old_comment=None,
                new_comment=expected_comment.strip(),
            )
            if self.options.mode == "fix":
                fs_utils.write_file_lines(file_path, new_lines)
        elif status == "updated":
            self.stats.updated += 1
            self._report_change(
                rel_path=rel_path,
                label="UPDATE",
                old_comment=old_comment,
                new_comment=expected_comment.strip(),
            )
            if self.options.mode == "fix":
                fs_utils.write_file_lines(file_path, new_lines)
        else:
            self.stats.skipped += 1

    def _report_change(
        self,
        *,
        rel_path: str,
        label: str,
        old_comment: str | None,
        new_comment: str,
    ) -> None:
        prefix = {
            "fix": "[FIX]",
            "check": "[CHECK]",
            "dry-run": "[DRY-RUN]",
        }[self.options.mode]
        print(f"{prefix} [{label}] {rel_path}")
        if old_comment is not None and self.options.mode in {"fix", "dry-run"}:
            print(f"    Old: {old_comment}")
        if self.options.mode in {"fix", "dry-run"} or label == "UPDATE":
            print(f"    New: {new_comment}")

    def _print_summary(self) -> None:
        print("\n================== Summary ==================")
        print(f"Scanned files : {self.stats.scanned}")
        print(f"Added comments: {self.stats.added}")
        print(f"Updated lines : {self.stats.updated}")
        print(f"Skipped files : {self.stats.skipped}")
        print(f"Errors        : {self.stats.errors}")
        print("=============================================")
