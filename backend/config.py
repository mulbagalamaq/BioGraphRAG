"""Configuration loader — single YAML file + env var expansion."""

from __future__ import annotations

import dataclasses
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclasses.dataclass
class AppConfig:
    """Thin wrapper around a nested dict with dotted-path access."""

    raw: Dict[str, Any]

    def get(self, dotted_path: str, default: Optional[Any] = None) -> Any:
        node: Any = self.raw
        for part in dotted_path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load config from YAML, expanding ``${ENV_VAR}`` placeholders."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "config.yaml"
    cfg_path = Path(path).expanduser().resolve()

    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as fh:
        data: Dict[str, Any] = yaml.safe_load(fh) or {}

    _expand_env_vars(data)
    return AppConfig(raw=data)


def _expand_env_vars(obj: Any) -> None:
    """Recursively replace ``${VAR}`` with ``os.environ[VAR]``."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = re.sub(
                    r"\$\{([^}]+)\}",
                    lambda m: os.environ.get(m.group(1), m.group(0)),
                    value,
                )
            elif isinstance(value, (dict, list)):
                _expand_env_vars(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = re.sub(
                    r"\$\{([^}]+)\}",
                    lambda m: os.environ.get(m.group(1), m.group(0)),
                    item,
                )
            elif isinstance(item, (dict, list)):
                _expand_env_vars(item)
