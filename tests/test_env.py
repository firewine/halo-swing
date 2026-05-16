from pathlib import Path

import halo_swing_mcp.env as local_env
from halo_swing_mcp.env import clear_local_env_cache, get_config_value


def test_get_config_value_can_disable_dotenv_loading(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo.env"
    repo_env.write_text("NEWS_API_KEY=repo-news-secret\n", encoding="utf-8")
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.setenv("HALO_SWING_DISABLE_DOTENV", "true")
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("NEWS_API_KEY") is None


def test_exported_disable_false_overrides_repo_root_disable_true(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo" / ".env"
    run_dir = tmp_path / "runner"
    repo_env.parent.mkdir()
    run_dir.mkdir()
    repo_env.write_text(
        "\n".join(
            [
                "HALO_SWING_DISABLE_DOTENV=true",
                "NEWS_API_KEY=repo-news-secret",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.setenv("HALO_SWING_DISABLE_DOTENV", "false")
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("NEWS_API_KEY") == "repo-news-secret"


def test_get_config_value_can_disable_dotenv_loading_from_repo_root_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo" / ".env"
    run_dir = tmp_path / "runner"
    repo_env.parent.mkdir()
    run_dir.mkdir()
    repo_env.write_text(
        "\n".join(
            [
                "HALO_SWING_DISABLE_DOTENV=true",
                "NEWS_API_KEY=repo-news-secret",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("NEWS_API_KEY") is None


def test_cwd_disable_false_overrides_repo_root_disable_true(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo" / ".env"
    run_dir = tmp_path / "runner"
    repo_env.parent.mkdir()
    run_dir.mkdir()
    repo_env.write_text(
        "\n".join(
            [
                "HALO_SWING_DISABLE_DOTENV=true",
                "NEWS_API_KEY=repo-news-secret",
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / ".env").write_text(
        "HALO_SWING_DISABLE_DOTENV=false\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("NEWS_API_KEY") == "repo-news-secret"


def test_get_config_value_can_disable_dotenv_loading_from_cwd_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo" / ".env"
    run_dir = tmp_path / "runner"
    repo_env.parent.mkdir()
    run_dir.mkdir()
    repo_env.write_text("NEWS_API_KEY=repo-news-secret\n", encoding="utf-8")
    (run_dir / ".env").write_text(
        "\n".join(
            [
                "HALO_SWING_DISABLE_DOTENV=true",
                "POLYGON_API_KEY=cwd-polygon-secret",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("NEWS_API_KEY") is None
    assert get_config_value("POLYGON_API_KEY") is None


def test_get_config_value_uses_exported_env_before_dotenv(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo.env"
    repo_env.write_text("POLYGON_API_KEY=repo-secret\n", encoding="utf-8")
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    monkeypatch.setenv("POLYGON_API_KEY", "exported-secret")
    clear_local_env_cache()

    assert get_config_value("POLYGON_API_KEY") == "exported-secret"


def test_get_config_value_uses_launch_directory_env_before_repo_root_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo" / ".env"
    run_dir = tmp_path / "runner"
    repo_env.parent.mkdir()
    run_dir.mkdir()
    repo_env.write_text("POLYGON_API_KEY=repo-secret\n", encoding="utf-8")
    (run_dir / ".env").write_text(
        "POLYGON_API_KEY=launch-secret\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("POLYGON_API_KEY") == "launch-secret"


def test_get_config_value_reads_repo_root_env_when_cwd_differs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_env = tmp_path / "repo" / ".env"
    run_dir = tmp_path / "runner"
    repo_env.parent.mkdir()
    run_dir.mkdir()
    repo_env.write_text("NEWS_API_KEY=repo-news-secret\n", encoding="utf-8")
    monkeypatch.setattr(local_env, "REPO_ROOT_ENV_PATH", repo_env)
    monkeypatch.chdir(run_dir)
    monkeypatch.delenv("HALO_SWING_DISABLE_DOTENV", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    clear_local_env_cache()

    assert get_config_value("NEWS_API_KEY") == "repo-news-secret"
