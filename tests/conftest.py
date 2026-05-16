import pytest

from halo_swing_mcp.config import get_settings
from halo_swing_mcp.env import clear_local_env_cache


@pytest.fixture(autouse=True)
def disable_dotenv_loading_by_default(monkeypatch) -> None:
    monkeypatch.setenv("HALO_SWING_DISABLE_DOTENV", "true")
    clear_local_env_cache()
    get_settings.cache_clear()
    yield
    clear_local_env_cache()
    get_settings.cache_clear()
