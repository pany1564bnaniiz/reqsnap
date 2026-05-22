"""Configuration loader for reqsnap.

Supports reading settings from a ``reqsnap.toml`` or ``.reqsnap.toml`` file
in the current working directory, with sensible defaults.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

_CONFIG_FILENAMES = ["reqsnap.toml", ".reqsnap.toml"]

DEFAULTS: Dict[str, Any] = {
    "snapshot_dir": ".reqsnap",
    "default_environment": "default",
    "timeout": 30,
    "color_output": True,
}


def _find_config_file(start_dir: Optional[str] = None) -> Optional[Path]:
    """Search for a config file starting from *start_dir* (default: cwd)."""
    base = Path(start_dir or os.getcwd())
    for name in _CONFIG_FILENAMES:
        candidate = base / name
        if candidate.exists():
            return candidate
    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration, merging file values over defaults.

    Args:
        config_path: Explicit path to a TOML config file.  When *None* the
            current directory is searched automatically.

    Returns:
        Merged configuration dictionary.
    """
    config = dict(DEFAULTS)

    if tomllib is None:
        return config

    path: Optional[Path] = None
    if config_path:
        path = Path(config_path)
    else:
        path = _find_config_file()

    if path is None or not path.exists():
        return config

    with path.open("rb") as fh:
        file_config = tomllib.load(fh)

    reqsnap_section = file_config.get("reqsnap", file_config)
    config.update({k: v for k, v in reqsnap_section.items() if k in DEFAULTS})
    return config


def get(key: str, config_path: Optional[str] = None) -> Any:
    """Convenience helper to read a single config key."""
    return load_config(config_path).get(key)
