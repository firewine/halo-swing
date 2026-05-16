"""Local environment value helpers.

The runtime accepts both exported environment variables and ignored local
`.env` files. This module reads `.env` without mutating ``os.environ`` so tools
can treat configured secrets as boolean evidence without leaking values.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values


LOCAL_ENV_PATH = ".env"


def get_config_value(key: str) -> str | None:
    """Return one config value from exported env or the local `.env` file."""

    if key in os.environ:
        return os.environ[key]
    value = _local_env_values().get(key)
    return value if isinstance(value, str) else None


def get_first_config_value(*keys: str) -> str | None:
    """Return the first configured value using exported-env precedence."""

    for key in keys:
        value = get_config_value(key)
        if value is not None:
            return value
    return None


def clear_local_env_cache() -> None:
    """Clear cached `.env` values after tests or cwd changes."""

    _local_env_values.cache_clear()


@lru_cache(maxsize=1)
def _local_env_values() -> dict[str, str | None]:
    env_path = Path(LOCAL_ENV_PATH)
    if not env_path.is_file():
        return {}
    return dict(dotenv_values(env_path))
