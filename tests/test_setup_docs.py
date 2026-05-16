from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DEVOPS_GUIDE = ROOT / "docs" / "devops-setup-guide.md"


def _normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_setup_docs_describe_repo_root_dotenv_precedence() -> None:
    text = _normalized_text(README)
    guide = _normalized_text(DEVOPS_GUIDE)

    for document in (text, guide):
        assert "repo-root `.env`" in document or "repo-root .env" in document
        assert "exported environment variables" in document
        assert "launch-directory `.env`" in document or "launch-directory .env" in document
        assert "HALO_SWING_DISABLE_DOTENV=true" in document
        assert "exported or set in `.env`" in document or "exported or placed in `.env`" in document
        assert "other dotenv values are ignored" in document or "ignores other dotenv values" in document


def test_devops_guide_shows_dotenv_key_only_live_data_setup() -> None:
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    assert "POLYGON_API_KEY=your_polygon_key" in guide
    assert "FRED_API_KEY=your_fred_key" in guide
    assert "NEWS_API_KEY=your_newsapi_key" in guide
    assert "export POLYGON_API_KEY" not in guide
    assert "export FRED_API_KEY" not in guide
    assert "export NEWS_API_KEY" not in guide


def test_setup_docs_describe_hermes_registration_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_HERMES_CONFIG_PATH" in document
        assert "HALO_SWING_HERMES_MCP_CONFIG_REGISTERED=true" in document
        assert "non-secret" in document


def test_setup_docs_describe_binance_passphrase_confirmation_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_BINANCE_PASSPHRASE_CONFIRMED=true" in document
        assert "non-secret" in document
        assert "does not store" in document or "never stores" in document


def test_setup_docs_describe_binance_trade_only_attestation_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_BINANCE_TRADE_ONLY_PERMISSION_ATTESTED=true" in document
        assert "trade-only" in document
        assert "does not enable order submission" in document


def test_setup_docs_describe_binance_live_order_approval_env_flag() -> None:
    text = README.read_text(encoding="utf-8")
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    for document in (text, guide):
        assert "HALO_SWING_BINANCE_LIVE_ORDER_APPROVED=true" in document
        assert "readiness evidence only" in document
        assert "CONFIRM_BTC_BINANCE_COINM_ORDER" in document


def test_setup_docs_describe_all_env_readiness_smoke_boundary() -> None:
    text = _normalized_text(README)
    guide = _normalized_text(DEVOPS_GUIDE)

    for document in (text, guide):
        assert "repo-root `.env`" in document or "repo-root .env" in document
        assert "MIGRATION_GO" in document
        assert "REPOSITORY_GO" in document
        assert "no network call" in document
        assert "no Telegram send" in document
        assert "no order submission" in document
