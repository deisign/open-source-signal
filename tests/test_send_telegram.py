from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import send_telegram


def test_split_message_keeps_short_message() -> None:
    assert send_telegram.split_message("hello", limit=500) == ["hello"]


def test_split_message_splits_on_paragraphs() -> None:
    text = "A" * 300 + "\n\n" + "B" * 300 + "\n\n" + "C" * 300
    chunks = send_telegram.split_message(text, limit=650)
    assert len(chunks) == 2
    assert all(len(chunk) <= 650 for chunk in chunks)
    assert chunks[0].startswith("A")
    assert chunks[1].startswith("C")


def test_split_message_rejects_tiny_limit() -> None:
    with pytest.raises(ValueError, match="at least 500"):
        send_telegram.split_message("hello", limit=100)


def test_read_message_rejects_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("\n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        send_telegram.read_message(path)


def test_send_telegram_message_posts_expected_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps({"ok": True, "result": {"message_id": 42}}).encode("utf-8")

    def fake_urlopen(request, timeout: int):
        calls.append((request.full_url, json.loads(request.data.decode("utf-8"))))
        return FakeResponse()

    monkeypatch.setattr(send_telegram.urllib.request, "urlopen", fake_urlopen)

    responses = send_telegram.send_telegram_message(
        token="123:ABC",
        chat_id="@open_source_signal",
        text="Сигнал відкритих джерел",
        disable_web_page_preview=True,
        api_base="https://example.test",
    )

    assert responses[0]["ok"] is True
    assert calls == [
        (
            "https://example.test/bot123:ABC/sendMessage",
            {
                "chat_id": "@open_source_signal",
                "text": "Сигнал відкритих джерел",
                "disable_web_page_preview": True,
            },
        )
    ]


def test_send_telegram_message_rejects_missing_token() -> None:
    with pytest.raises(ValueError, match="token"):
        send_telegram.send_telegram_message(token="", chat_id="@x", text="hello")


def test_send_telegram_message_rejects_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps({"ok": False, "description": "chat not found"}).encode("utf-8")

    monkeypatch.setattr(send_telegram.urllib.request, "urlopen", lambda request, timeout: FakeResponse())

    with pytest.raises(RuntimeError, match="Telegram API error"):
        send_telegram.send_telegram_message(token="123:ABC", chat_id="@missing", text="hello")
