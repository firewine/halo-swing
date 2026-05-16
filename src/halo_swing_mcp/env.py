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
REPO_ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / LOCAL_ENV_PATH
DOTENV_DISABLED_ENV = "HALO_SWING_DISABLE_DOTENV"


def get_config_value(key: str) -> str | None:
    """Return one config value from exported env or the local `.env` file."""

    if key in os.environ:
        return os.environ[key]
    if dotenv_loading_disabled():
        return None
    value = _local_env_values().get(key)
    return value if isinstance(value, str) else None


def get_first_config_value(*keys: str) -> str | None:
    """Return the first configured value using exported-env precedence."""

    for key in keys:
        value = get_config_value(key)
        if value is not None:
            return value
    return None


def get_local_env_files() -> tuple[Path, ...]:
    """Return local dotenv files from broad to narrow precedence."""

    if dotenv_loading_disabled():
        return ()
    return _candidate_env_files()


def dotenv_loading_disabled() -> bool:
    """Return whether dotenv loading is disabled for isolated runs."""

    if DOTENV_DISABLED_ENV in os.environ:
        return _truthy(os.environ[DOTENV_DISABLED_ENV])
    value: str | None = None
    for env_path in _candidate_env_files():
        if not env_path.is_file():
            continue
        candidate = dotenv_values(env_path).get(DOTENV_DISABLED_ENV)
        if _truthy(candidate):
            value = "true"
        elif candidate is not None:
            value = candidate if isinstance(candidate, str) else None
    return _truthy(value)


def clear_local_env_cache() -> None:
    """Clear cached `.env` values after tests or cwd changes."""

    _local_env_values.cache_clear()


@lru_cache(maxsize=1)
def _local_env_values() -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    for env_path in get_local_env_files():
        if env_path.is_file():
            values.update(dotenv_values(env_path))
    return values


def _candidate_env_files() -> tuple[Path, ...]:
    paths: list[Path] = []
    for path in (REPO_ROOT_ENV_PATH, Path(LOCAL_ENV_PATH).resolve()):
        if path not in paths:
            paths.append(path)
    return tuple(paths)


def _truthy(value: str | None) -> bool:
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes"}
