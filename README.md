# dev-tools

Reusable Python utilities for source-tree maintenance.

## Included tools

- `auto-comments`: check or update leading relative-path comments such as `// path/to/file.cpp`
- `hpp-guard`: check or fix header include guards for `.hpp` / `.h` style files
- `fix-include`: check or fix quoted include paths so they point to project-relative files
- `find-hpp`: analyze include frequency and emit a PCH recommendation report

## Unified CLI

Without installation:

```bash
python run.py auto-comments --help
python run.py hpp-guard --help
python run.py fix-include --help
python run.py find-hpp --help

python -m dev_tools auto-comments --help
python -m dev_tools hpp-guard --help
python -m dev_tools fix-include --help
python -m dev_tools find-hpp --help
```

After installation:

```bash
pip install -e .
dev-tools auto-comments --help
dev-tools hpp-guard --help
dev-tools fix-include --help
dev-tools find-hpp --help
```

## Common capabilities

`auto-comments`, `hpp-guard`, and `fix-include` support:

- `--check`: check only
- `--fix`: apply changes in place
- `--dry-run`: preview changes without writing files
- `scan_dir`: scan root
- `--relative-to`: separate base path used to calculate relative comments / guard names / include paths
- `--extensions`: file extensions to include
- `--include`: include glob patterns relative to `scan_dir`
- `--exclude`: exclude glob patterns relative to `scan_dir`
- `--config`: explicitly choose a `dev-tools.toml`

`find-hpp` supports:

- `scan_dir`
- `--extensions`
- `--include`
- `--exclude`
- `--top`
- `--extra-libs`
- `--exclude-names`
- `--output`
- `--config`

## `auto-comments`

Examples:

```bash
python run.py auto-comments src --check
python run.py auto-comments libs/bills_core/src --relative-to . --fix
python run.py auto-comments src --extensions .hpp .cpp --exclude build temp
```

## `hpp-guard`

Examples:

```bash
python run.py hpp-guard src --check
python run.py hpp-guard include --extensions .hpp .h --fix
python run.py hpp-guard src --relative-to . --dry-run
```

## `fix-include`

Examples:

```bash
python run.py fix-include src --check
python run.py fix-include src --relative-to src --fix
python run.py fix-include apps/bills_cli/src --relative-to . --dry-run
```

## `find-hpp`

Examples:

```bash
python run.py find-hpp src --top 80
python run.py find-hpp src --extra-libs mylib/ fmt/
python run.py find-hpp src --output temp/pch_report.hpp
```

## Configuration file

The CLI automatically searches for `dev-tools.toml` from the current directory or the chosen `scan_dir` upward.

Example file:

```toml
[auto_comments]
scan_dir = "src"
relative_to = "src"
extensions = [".hpp", ".cpp", ".h", ".c"]
include = []
exclude = [".git", "build", "out", "temp", "__pycache__"]
mode = "check"

[hpp_guard]
scan_dir = "src"
relative_to = "."
extensions = [".hpp", ".h"]
include = []
exclude = [".git", "build", "out", "temp", "__pycache__"]
mode = "check"

[fix_include]
scan_dir = "src"
relative_to = "src"
extensions = [".hpp", ".cpp", ".h", ".c", ".cc", ".hh"]
include = []
exclude = [".git", "build", "out", "temp", "__pycache__"]
mode = "check"

[find_hpp]
scan_dir = "src"
extensions = [".hpp", ".cpp", ".h", ".c", ".cc", ".cxx"]
include = []
exclude = [".git", "build", "out", "temp", "__pycache__"]
top = 50
extra_libs = []
exclude_names = ["pch.hpp", "cmake_pch.hxx"]
output = "temp/pch_report.hpp"
```

See `dev-tools.toml.example` for a ready-to-copy template.
