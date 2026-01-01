"""Configuration utilities for the dual bio graph rag project."""

from __future__ import annotations

import dataclasses
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclasses.dataclass
class AppConfig:
    raw: Dict[str, Any]

    def get(self, dotted_path: str, default: Optional[Any] = None) -> Any:
        node: Any = self.raw
        for part in dotted_path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node


def load_config(path: str | Path, overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    cfg_path = Path(path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as handle:
        data: Dict[str, Any] = yaml.safe_load(handle) or {}

    # Expand ${ENV_VAR} style variables in config values
    _expand_env_vars(data)

    env_prefix = "BIO_KG_"
    for key, value in os.environ.items():
        if not key.startswith(env_prefix):
            continue
        dotted = key.removeprefix(env_prefix).lower().replace("__", ".")
        _assign(data, dotted, value)

    if overrides:
        for dotted, value in overrides.items():
            _assign(data, dotted, value)

    return AppConfig(raw=data)


def _expand_env_vars(obj: Any) -> None:
    """Recursively expand ${ENV_VAR} style environment variables in config."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                # Replace ${VAR_NAME} with environment variable value
                obj[key] = re.sub(
                    r'\$\{([^}]+)\}',
                    lambda m: os.environ.get(m.group(1), m.group(0)),
                    value
                )
            elif isinstance(value, (dict, list)):
                _expand_env_vars(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = re.sub(
                    r'\$\{([^}]+)\}',
                    lambda m: os.environ.get(m.group(1), m.group(0)),
                    item
                )
            elif isinstance(item, (dict, list)):
                _expand_env_vars(item)


def _assign(tree: Dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = tree
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value
