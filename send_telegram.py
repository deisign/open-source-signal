#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TELEGRAM_MESSAGE_LIMIT = 4096
DEFAULT_SAFE_LIMIT = 3900


def read_message(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Text file is empty: {path}")
    return text


def split_message(text: str, limit: int = DEFAULT_SAFE_LIMIT) -> list[str]:
    if limit < 500:
        raise ValueError("limit must be at least 500 characters")
    if len(text) <= limit:
        return [text]

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""

    def flush_current() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= limit:
            current = candidate
            continue

        flush_current()

        if len(paragraph) <= limit:
            current = paragraph
            continue

        # Fallback for unusually long paragraphs: split by hard character limit.
        start = 0
        while start < len(paragraph):
            chunks.append(paragraph[start : start + limit].strip())
            start += limit

    flush_current()
    return chunks


def _telegram_url(token: str, api_base: str) -> str:
    return f"{api_base.rstrip('/')}/bot{token}/sendMessage"


def _post_json(url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Telegram connection error: {exc.reason}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Telegram returned non-JSON response: {raw[:500]}") from exc

    if not parsed.get("ok"):
        raise RuntimeError(f"Telegram API error: {parsed}")
    return parsed


def send_telegram_message(
    *,
    token: str,
    chat_id: str,
    text: str,
    disable_web_page_preview: bool = False,
    parse_mode: str | None = "HTML",
    timeout: int = 20,
    api_base: str = "https://api.telegram.org",
    chunk_limit: int = DEFAULT_SAFE_LIMIT,
) -> list[dict[str, Any]]:
    token = token.strip()
    chat_id = chat_id.strip()
    text = text.strip()

    if not token:
        raise ValueError("Telegram bot token is required")
    if not chat_id:
        raise ValueError("Telegram chat/channel id is required")
    if not text:
        raise ValueError("Telegram message text is required")
    if chunk_limit > TELEGRAM_MESSAGE_LIMIT:
        raise ValueError("chunk_limit cannot exceed Telegram's 4096-character message limit")

    url = _telegram_url(token, api_base)
    responses: list[dict[str, Any]] = []
    chunks = split_message(text, limit=chunk_limit)

    for index, chunk in enumerate(chunks, start=1):
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if len(chunks) > 1:
            payload["text"] = f"{chunk}\n\n[{index}/{len(chunks)}]"
        responses.append(_post_json(url, payload, timeout=timeout))

    return responses


def resolve_secret(cli_value: str | None, env_name: str, display_name: str) -> str:
    value = cli_value or os.environ.get(env_name, "")
    if not value.strip():
        raise SystemExit(f"Missing {display_name}. Pass it as an argument or set {env_name}.")
    return value.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Send an Open Source Signal Telegram announcement text file.")
    parser.add_argument("--text-file", type=Path, required=True, help="Path to a rendered Telegram .txt announcement")
    parser.add_argument("--token", help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN env variable")
    parser.add_argument("--chat-id", help="Telegram chat/channel id. Defaults to TELEGRAM_CHAT_ID env variable")
    parser.add_argument("--disable-preview", action="store_true", help="Disable link preview in Telegram")
    parser.add_argument("--parse-mode", default="HTML", help="Telegram parse mode: HTML, MarkdownV2, Markdown, or empty string for plain text")
    parser.add_argument("--dry-run", action="store_true", help="Print the message and do not call Telegram")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    parser.add_argument("--chunk-limit", type=int, default=DEFAULT_SAFE_LIMIT, help="Split messages above this length")
    args = parser.parse_args()

    text = read_message(args.text_file)

    if args.dry_run:
        chunks = split_message(text, limit=args.chunk_limit)
        print(f"DRY RUN: {args.text_file}")
        print(f"Chunks: {len(chunks)}")
        print("-" * 72)
        for index, chunk in enumerate(chunks, start=1):
            if len(chunks) > 1:
                print(f"[chunk {index}/{len(chunks)}]")
            print(chunk)
            if index != len(chunks):
                print("\n" + "-" * 72 + "\n")
        return

    token = resolve_secret(args.token, "TELEGRAM_BOT_TOKEN", "Telegram bot token")
    chat_id = resolve_secret(args.chat_id, "TELEGRAM_CHAT_ID", "Telegram chat/channel id")
    responses = send_telegram_message(
        token=token,
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=args.disable_preview,
        parse_mode=args.parse_mode or None,
        timeout=args.timeout,
        chunk_limit=args.chunk_limit,
    )
    print(f"Sent {len(responses)} Telegram message(s) to {chat_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - CLI should print a clear terminal error.
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
