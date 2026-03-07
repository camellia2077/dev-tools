from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


VALID_MODES = {"check", "fix", "dry-run"}


@dataclass(frozen=True)
class ToolConfig:
    scan_dir: str | None = None
    relative_to: str | None = None
    extensions: tuple[str, ...] = ()
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    mode: str | None = None


@dataclass(frozen=True)
class FindHppConfig:
    scan_dir: str | None = None
    extensions: tuple[str, ...] = ()
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    top: int | None = None
    extra_libs: tuple[str, ...] = ()
    exclude_names: tuple[str, ...] = ()
    output: str | None = None


@dataclass(frozen=True)
class DevToolsConfig:
    path: Path | None
    auto_comments: ToolConfig = field(default_factory=ToolConfig)
    hpp_guard: ToolConfig = field(default_factory=ToolConfig)
    fix_include: ToolConfig = field(default_factory=ToolConfig)
    find_hpp: FindHppConfig = field(default_factory=FindHppConfig)


def find_config(start_dir: Path) -> Path | None:
    current = start_dir.resolve()
    for candidate_dir in (current, *current.parents):
        candidate = candidate_dir / "dev-tools.toml"
        if candidate.is_file():
            return candidate
    return None


def load_config(explicit_path: str | None, start_dir: Path) -> DevToolsConfig:
    if explicit_path:
        config_path = Path(explicit_path).resolve()
        if not config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")
    else:
        config_path = find_config(start_dir)
        if config_path is None:
            return DevToolsConfig(path=None)

    with config_path.open("rb") as handle:
        payload = tomllib.load(handle)

    return DevToolsConfig(
        path=config_path,
        auto_comments=_parse_tool_config(payload.get("auto_comments")),
        hpp_guard=_parse_tool_config(payload.get("hpp_guard")),
        fix_include=_parse_tool_config(payload.get("fix_include")),
        find_hpp=_parse_find_hpp_config(payload.get("find_hpp")),
    )


def resolve_path(value: str | None, *, cwd: Path, config_path: Path | None) -> Path | None:
    if not value:
        return None
    raw_path = Path(value)
    if raw_path.is_absolute():
        return raw_path.resolve()
    base_dir = config_path.parent if config_path is not None else cwd
    return (base_dir / raw_path).resolve()


def normalize_extensions(
    values: tuple[str, ...] | list[str] | None,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    if not values:
        return default
    normalized: list[str] = []
    for item in values:
        value = item.strip().lower()
        if not value:
            continue
        if not value.startswith("."):
            value = f".{value}"
        normalized.append(value)
    return tuple(dict.fromkeys(normalized)) or default


def normalize_patterns(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    cleaned = [item.strip() for item in values if item and item.strip()]
    return tuple(dict.fromkeys(cleaned))


def normalize_names(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    return tuple(dict.fromkeys(item.strip().lower() for item in values if item and item.strip()))


def validate_mode(value: str | None, default: str) -> str:
    mode = (value or default).strip().lower()
    if mode not in VALID_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    return mode


def _parse_tool_config(section: object) -> ToolConfig:
    if section is None:
        return ToolConfig()
    if not isinstance(section, dict):
        raise ValueError("Tool config section must be a table")

    scan_dir = _as_optional_str(section.get("scan_dir"))
    relative_to = _as_optional_str(section.get("relative_to"))
    extensions = tuple(_as_str_list(section.get("extensions")))
    include = tuple(_as_str_list(section.get("include")))
    exclude = tuple(_as_str_list(section.get("exclude")))
    mode = _as_optional_str(section.get("mode"))
    if mode is not None:
        mode = validate_mode(mode, "check")

    return ToolConfig(
        scan_dir=scan_dir,
        relative_to=relative_to,
        extensions=extensions,
        include=include,
        exclude=exclude,
        mode=mode,
    )


def _parse_find_hpp_config(section: object) -> FindHppConfig:
    if section is None:
        return FindHppConfig()
    if not isinstance(section, dict):
        raise ValueError("find_hpp config section must be a table")

    top = section.get("top")
    if top is not None and (not isinstance(top, int) or top <= 0):
        raise ValueError("find_hpp.top must be a positive integer")

    return FindHppConfig(
        scan_dir=_as_optional_str(section.get("scan_dir")),
        extensions=tuple(_as_str_list(section.get("extensions"))),
        include=tuple(_as_str_list(section.get("include"))),
        exclude=tuple(_as_str_list(section.get("exclude"))),
        top=top,
        extra_libs=tuple(_as_str_list(section.get("extra_libs"))),
        exclude_names=tuple(_as_str_list(section.get("exclude_names"))),
        output=_as_optional_str(section.get("output")),
    )


def _as_optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a non-empty string value")
    return value.strip()


def _as_str_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Expected a list of strings")
    output: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("Expected a list of non-empty strings")
        output.append(item.strip())
    return output
