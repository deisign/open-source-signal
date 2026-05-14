import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "telegram.yml"
DOC = ROOT / "docs" / "TELEGRAM_SETUP.md"
SITE = ROOT / "site.json"
SENT_LOG = ROOT / "data" / "telegram_sent.json"


def test_telegram_workflow_exists_and_is_manual_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch" in text
    assert "push:" not in text
    assert "TELEGRAM_BOT_TOKEN" in text
    assert "TELEGRAM_CHAT_ID" in text
    assert "python -m pytest -q" in text
    assert "python build_site.py --issues issues --templates templates --out dist --config site.json" in text
    assert "python telegram_digest.py" in text
    assert "python send_telegram.py" in text
    assert "--disable-preview" in text


def test_telegram_workflow_has_duplicate_protection():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "force:" in text
    assert "permissions:" in text
    assert "contents: write" in text
    assert "telegram_sent_log.py check" in text
    assert "telegram_sent_log.py record" in text
    assert "data/telegram_sent.json" in text
    assert "steps.duplicate.outputs.should_send == 'true'" in text
    assert "Record Telegram announcement" in text


def test_telegram_setup_doc_mentions_github_secrets():
    text = DOC.read_text(encoding="utf-8")
    assert "TELEGRAM_BOT_TOKEN" in text
    assert "TELEGRAM_CHAT_ID" in text
    assert "Actions → Publish Telegram announcement" in text
    assert "manual" in text.lower()
    assert "force: false" in text
    assert "data/telegram_sent.json" in text


def test_site_config_has_public_base_url():
    data = json.loads(SITE.read_text(encoding="utf-8"))
    assert data["base_url"] == "https://osintsignal.org"


def test_initial_telegram_sent_log_exists_and_is_empty():
    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))
    assert data == {"telegram": {}}
