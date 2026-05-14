from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "import_daily_signal.yml"


def test_import_workflow_exists_and_uses_importer():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch" in text
    assert "signal_text" in text
    assert "contents: write" in text
    assert "import_daily_signal.py" in text
    assert "python -m pytest -q" in text
    assert "git commit" in text
