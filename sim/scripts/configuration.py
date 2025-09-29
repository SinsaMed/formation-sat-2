"""Utilities for discovering and loading mission scenario configurations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO_DIR = PROJECT_ROOT / "config" / "scenarios"
_SUPPORTED_SUFFIXES = (".yaml", ".yml", ".json")
_REQUIRED_TOP_LEVEL_KEYS = ("metadata", "orbital_elements", "timing", "payload_constraints")


def resolve_scenario_path(
    identifier: Union[str, Path],
    base_directory: Optional[Union[str, Path]] = None,
    *,
    allow_missing: bool = False,
) -> Path:
    """Return the file path corresponding to a named scenario."""

    base_path = Path(base_directory) if base_directory else DEFAULT_SCENARIO_DIR
    if isinstance(identifier, Path):
        candidate = identifier
    else:
        candidate = Path(identifier)

    if candidate.exists():
        return candidate

    stem = candidate.stem
    for suffix in _SUPPORTED_SUFFIXES:
        scenario_path = base_path / f"{stem}{suffix}"
        if scenario_path.exists():
            return scenario_path

    if allow_missing:
        return base_path / f"{stem}.json"

    raise FileNotFoundError(
        f"Scenario '{identifier}' was not found under '{base_path}'."
    )


def _load_mapping_from_path(path: Path) -> MutableMapping[str, Any]:
    """Load a mapping object from a JSON or YAML file."""

    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        payload = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError(
                "PyYAML is required to parse YAML scenario files but is not installed."
            )
        payload = yaml.safe_load(text)
    else:  # pragma: no cover - guard should be unreachable due to suffix checks
        raise ValueError(f"Unsupported scenario file format: {path.suffix}")

    if not isinstance(payload, MutableMapping):
        raise TypeError("Scenario configuration must decode to a mutable mapping.")

    return payload


def _validate_top_level_keys(data: Mapping[str, Any], required_keys: Iterable[str]) -> None:
    """Ensure that mandatory sections are present in the scenario data."""

    missing = [key for key in required_keys if key not in data]
    if missing:
        raise ValueError(
            "Scenario configuration missing required sections: " + ", ".join(missing)
        )


def load_scenario(identifier: Union[str, Path, Mapping[str, Any]]) -> MutableMapping[str, Any]:
    """Load a scenario configuration from a name, path, or existing mapping."""

    if isinstance(identifier, Mapping):
        data = dict(identifier)
    else:
        scenario_path = resolve_scenario_path(identifier)
        data = _load_mapping_from_path(scenario_path)

    _validate_top_level_keys(data, _REQUIRED_TOP_LEVEL_KEYS)
    return data


__all__ = ["load_scenario", "resolve_scenario_path"]
