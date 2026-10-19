import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

WORKFLOWS_DIR = ROOT / ".github" / "workflows"
SENT_LOG = ROOT / "data" / "telegram_sent.json"
ISSUES_DIR = ROOT / "issues"
WEEKLY_DIR = ROOT / "weekly"


def _issue_path(issue_name: str) -> Path:
    directory = WEEKLY_DIR if issue_name.startswith("open-source-signal-weekly-") else ISSUES_DIR
    return directory / issue_name


def _workflow_files() -> list[Path]:
    if not WORKFLOWS_DIR.exists():
        return []

    return sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(WORKFLOWS_DIR.glob("*.yaml"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _telegram_workflows() -> list[Path]:
    result: list[Path] = []

    for path in _workflow_files():
        text = _read(path).lower()
        if "telegram" in text:
            result.append(path)

    return result


def test_workflows_directory_exists():
    assert WORKFLOWS_DIR.exists(), "Missing .github/workflows directory"


def test_at_least_one_telegram_workflow_exists():
    workflows = _telegram_workflows()

    assert workflows, (
        "No Telegram-related workflow found. "
        "Expected at least one workflow containing the word 'telegram'."
    )


def test_telegram_workflow_has_manual_dispatch_or_is_part_of_daily_publish():
    workflows = _telegram_workflows()
    combined = "\n\n".join(_read(path) for path in workflows)

    assert (
        "workflow_dispatch:" in combined
        or "Publish Daily Issue" in combined
        or "publish daily issue" in combined.lower()
    )


def test_telegram_workflow_does_not_default_to_pilot_issue():
    workflows = _telegram_workflows()
    combined = "\n\n".join(_read(path) for path in workflows)

    forbidden_defaults = [
        'default: "2026-05-13.json"',
        "default: '2026-05-13.json'",
        "default: 2026-05-13.json",
    ]

    for forbidden in forbidden_defaults:
        assert forbidden not in combined


def test_telegram_workflow_mentions_expected_runtime_tools():
    workflows = _telegram_workflows()
    combined = "\n\n".join(_read(path).lower() for path in workflows)

    assert "telegram" in combined
    assert "python" in combined or "curl" in combined


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

            if "issue" in record:
                assert record["issue"] == issue_name

            if "lang" in record:
                assert record["lang"] == lang

            if "sent_at" in record:
                assert isinstance(record["sent_at"], str)
                assert re.match(
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
                    record["sent_at"],
                ), f"Invalid sent_at format: {record['sent_at']}"

            if "issue_url" in record:
                assert isinstance(record["issue_url"], str)
                assert record["issue_url"].startswith("https://")

            if "text_file" in record:
                assert isinstance(record["text_file"], str)
                expected_prefix = "telegram/weekly/" if issue_name.startswith("open-source-signal-weekly-") else "dist/"
                assert record["text_file"].startswith(expected_prefix)
                assert record["text_file"].endswith(".txt")


def test_telegram_sent_log_references_existing_issue_files():
    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))

    for issue_name in data.get("telegram", {}):
        assert _issue_path(issue_name).exists(), (
            f"Telegram sent log references missing issue file: {issue_name}"
        )


def test_telegram_sent_log_references_valid_issue_urls_when_present():
    data = json.loads(SENT_LOG.read_text(encoding="utf-8"))

    for issue_name, langs in data.get("telegram", {}).items():
        issue_json = _issue_path(issue_name)
        issue_data = json.loads(issue_json.read_text(encoding="utf-8"))

        if issue_json.parent == WEEKLY_DIR:
            expected_url = f"https://osintsignal.org/weekly/{issue_data['output_name']}"
        else:
            expected_date = issue_data["date_iso"]
            expected_url = f"https://osintsignal.org/issues/open-source-signal-{expected_date}.html"

        for record in langs.values():
            if "issue_url" in record:
                assert record["issue_url"] == expected_url


def test_issue_path_selects_daily_and_weekly_directories():
    assert _issue_path("2026-10-19.json") == ISSUES_DIR / "2026-10-19.json"
    assert _issue_path("open-source-signal-weekly-2026-W42.json") == WEEKLY_DIR / "open-source-signal-weekly-2026-W42.json"
