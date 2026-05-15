import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

WORKFLOW = ROOT / ".github" / "workflows" / "publish_telegram.yml"
SENT_LOG = ROOT / "data" / "telegram_sent.json"
RENDER_SCRIPT = ROOT / "render_telegram.py"
SEND_SCRIPT = ROOT / "send_telegram.py"


def test_telegram_workflow_exists():
    assert WORKFLOW.exists(), "Missing .github/workflows/publish_telegram.yml"


def test_telegram_workflow_has_manual_dispatch_inputs():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "issue:" in text
    assert "lang:" in text
    assert "max_items:" in text
    assert "force:" in text


def test_telegram_workflow_uses_expected_scripts():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "render_telegram.py" in text
    assert "send_telegram.py" in text


def test_telegram_workflow_does_not_default_to_pilot_issue():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'default: "2026-05-13.json"' not in text
    assert "default: '2026-05-13.json'" not in text
    assert "default: 2026-05-13.json" not in text


def test_telegram_scripts_exist():
    assert RENDER_SCRIPT.exists(), "Missing render_telegram.py"
    assert SEND_SCRIPT.exists(), "Missing send_telegram.py"


def test_telegram_sent_log_exists_and_has_valid_shape():
    assert SENT_LOG.exists(), "Missing data/telegram_sent.json"

    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))

    assert isinstance(data, dict)
    assert "telegram" in data
    assert isinstance(data["telegram"], dict)

    for issue_name, langs in data["telegram"].items():
        assert isinstance(issue_name, str)
        assert issue_name.endswith(".json")
        assert isinstance(langs, dict)

        for lang, record in langs.items():
            assert isinstance(lang, str)
            assert isinstance(record, dict)

            assert record.get("issue") == issue_name
            assert record.get("lang") == lang
            assert isinstance(record.get("sent_at"), str)
            assert isinstance(record.get("issue_url"), str)
            assert isinstance(record.get("text_file"), str)

            assert record["issue_url"].startswith("https://")
            assert record["text_file"].startswith("dist/")
            assert record["text_file"].endswith(".txt")


def test_telegram_sent_log_timestamps_are_iso_like():
    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))

    for langs in data.get("telegram", {}).values():
        for record in langs.values():
            sent_at = record.get("sent_at", "")
            assert re.match(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
                sent_at,
            ), f"Invalid sent_at format: {sent_at}"


def test_telegram_sent_log_references_existing_issue_files():
    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))

    for issue_name in data.get("telegram", {}):
        assert (ROOT / "issues" / issue_name).exists(), (
            f"Telegram sent log references missing issue file: {issue_name}"
        )


def test_telegram_sent_log_references_valid_issue_urls():
    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))

    for issue_name, langs in data.get("telegram", {}).items():
        issue_json = ROOT / "issues" / issue_name
        issue_data = json.loads(issue_json.read_text(encoding="utf-8"))

        expected_date = issue_data["date_iso"]
        expected_url = (
            f"https://osintsignal.org/issues/open-source-signal-{expected_date}.html"
        )

        for record in langs.values():
            assert record["issue_url"] == expected_url
