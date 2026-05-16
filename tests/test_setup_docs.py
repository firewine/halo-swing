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


def test_devops_guide_shows_dotenv_key_only_live_data_setup() -> None:
    guide = DEVOPS_GUIDE.read_text(encoding="utf-8")

    assert "POLYGON_API_KEY=your_polygon_key" in guide
    assert "FRED_API_KEY=your_fred_key" in guide
    assert "NEWS_API_KEY=your_newsapi_key" in guide
    assert "export POLYGON_API_KEY" not in guide
    assert "export FRED_API_KEY" not in guide
    assert "export NEWS_API_KEY" not in guide
