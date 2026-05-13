from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
SETUP_DOC = ROOT / "docs" / "GITHUB_PAGES_SETUP.md"


def test_pages_workflow_exists_and_uses_official_pages_actions():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/configure-pages@v5" in text
    assert "actions/upload-pages-artifact@v3" in text
    assert "actions/deploy-pages@v4" in text
    assert "path: dist" in text
    assert "pages: write" in text
    assert "id-token: write" in text
    assert "pytest -q" in text
    assert "python build_site.py --issues issues --templates templates --out dist --config site.json" in text


def test_github_pages_setup_doc_exists():
    text = SETUP_DOC.read_text(encoding="utf-8")
    assert "Settings → Pages" in text
    assert "GitHub Actions" in text
    assert "git push -u origin main" in text
