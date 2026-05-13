from __future__ import annotations

import json
from pathlib import Path

import pytest

import telegram_sent_log


def test_empty_log_allows_send(tmp_path: Path) -> None:
    sent_log = tmp_path / "telegram_sent.json"
    assert telegram_sent_log.check_sent(sent_log, "2026-05-14.json", "uk", force=False) is True


def test_record_then_check_blocks_duplicate(tmp_path: Path) -> None:
    sent_log = tmp_path / "telegram_sent.json"
    telegram_sent_log.record_sent(
        path=sent_log,
        issue="2026-05-14.json",
        lang="uk",
        issue_url="https://example.test/issues/open-source-signal-2026-05-14.html",
        text_file="dist/telegram-open-source-signal-2026-05-14.uk.txt",
        run_id="123",
        run_url="https://github.com/example/actions/runs/123",
    )

    assert telegram_sent_log.check_sent(sent_log, "2026-05-14.json", "uk", force=False) is False
    assert telegram_sent_log.check_sent(sent_log, "2026-05-14.json", "uk", force=True) is True

    data = json.loads(sent_log.read_text(encoding="utf-8"))
    record = data["telegram"]["2026-05-14.json"]["uk"]
    assert record["issue"] == "2026-05-14.json"
    assert record["lang"] == "uk"
    assert record["github_run_id"] == "123"
    assert record["sent_at"].endswith("Z")


def test_check_writes_github_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sent_log = tmp_path / "telegram_sent.json"
    output = tmp_path / "github_output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert telegram_sent_log.check_sent(sent_log, "2026-05-14.json", "en", force=False) is True

    text = output.read_text(encoding="utf-8")
    assert "should_send=true" in text
    assert "already_sent=false" in text


def test_parse_bool_rejects_ambiguous_value() -> None:
    with pytest.raises(ValueError, match="Cannot parse boolean"):
        telegram_sent_log.parse_bool("perhaps")
