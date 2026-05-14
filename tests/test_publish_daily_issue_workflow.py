from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish_daily_issue.yml"
DOC = ROOT / "docs" / "PUBLISH_DAILY_ISSUE.md"


def test_publish_daily_issue_workflow_exists_and_has_inputs():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Publish Daily Issue" in text
    assert "workflow_dispatch" in text
    assert "signal_text" in text
    assert "send_telegram" in text
    assert "force_issue" in text
    assert "force_telegram" in text
    assert "contents: write" in text


def test_publish_daily_issue_workflow_imports_builds_commits_and_sends():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "import_daily_signal.py" in text
    assert "python -m pytest -q" in text
    assert "python build_site.py --issues issues --templates templates --out dist --config site.json" in text
    assert "git add issues dist" in text
    assert "git commit -m \"Publish Daily Signal" in text
    assert "python telegram_digest.py" in text
    assert "python send_telegram.py" in text
    assert "telegram_sent_log.py check" in text
    assert "telegram_sent_log.py record" in text
    assert "data/telegram_sent.json" in text
    assert "TELEGRAM_BOT_TOKEN" in text
    assert "TELEGRAM_CHAT_ID" in text


def test_publish_daily_issue_workflow_has_duplicate_and_skip_paths():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "inputs.send_telegram == true" in text
    assert "steps.duplicate.outputs.should_send == 'true'" in text
    assert "Telegram sending disabled" in text
    assert "already sent" in text


def test_publish_daily_issue_doc_exists():
    text = DOC.read_text(encoding="utf-8")
    assert "Actions → Publish Daily Issue" in text
    assert "TELEGRAM_BOT_TOKEN" in text
    assert "force_telegram" in text
    assert "docs/IMPORT_DAILY_SIGNAL.md" in text
