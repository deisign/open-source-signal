#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_sent_log(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"telegram": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid sent log JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Sent log must be a JSON object: {path}")
    data.setdefault("telegram", {})
    if not isinstance(data["telegram"], dict):
        raise ValueError("sent log field 'telegram' must be an object")
    return data


def save_sent_log(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on", "force"}:
        return True
    if normalized in {"0", "false", "no", "n", "off", ""}:
        return False
    raise ValueError(f"Cannot parse boolean value: {value!r}")


def get_record(data: dict[str, Any], issue: str, lang: str) -> dict[str, Any] | None:
    issue_records = data.get("telegram", {}).get(issue, {})
    if not isinstance(issue_records, dict):
        return None
    record = issue_records.get(lang)
    return record if isinstance(record, dict) else None


def is_already_sent(path: Path, issue: str, lang: str) -> bool:
    data = load_sent_log(path)
    return get_record(data, issue, lang) is not None


def write_github_output(**values: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def check_sent(path: Path, issue: str, lang: str, force: bool) -> bool:
    already_sent = is_already_sent(path, issue, lang)
    should_send = force or not already_sent
    write_github_output(
        should_send="true" if should_send else "false",
        already_sent="true" if already_sent else "false",
    )
    return should_send


def record_sent(
    *,
    path: Path,
    issue: str,
    lang: str,
    issue_url: str,
    text_file: str,
    run_id: str = "",
    run_url: str = "",
) -> dict[str, Any]:
    data = load_sent_log(path)
    telegram = data.setdefault("telegram", {})
    issue_records = telegram.setdefault(issue, {})
    if not isinstance(issue_records, dict):
        raise ValueError(f"Sent log issue record must be an object: {issue}")

    record = {
        "sent_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "issue": issue,
        "lang": lang,
        "issue_url": issue_url,
        "text_file": text_file,
    }
    if run_id:
        record["github_run_id"] = run_id
    if run_url:
        record["github_run_url"] = run_url
    issue_records[lang] = record
    save_sent_log(path, data)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Check and record Telegram issue publication state.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Check whether a Telegram announcement was already sent")
    check.add_argument("--sent-log", type=Path, default=Path("data/telegram_sent.json"))
    check.add_argument("--issue", required=True, help="Issue filename, for example 2026-05-13.json")
    check.add_argument("--lang", required=True, choices=["uk", "en"])
    check.add_argument("--force", default="false", help="Allow sending even if already recorded")

    record = subparsers.add_parser("record", help="Record a successfully sent Telegram announcement")
    record.add_argument("--sent-log", type=Path, default=Path("data/telegram_sent.json"))
    record.add_argument("--issue", required=True, help="Issue filename, for example 2026-05-13.json")
    record.add_argument("--lang", required=True, choices=["uk", "en"])
    record.add_argument("--issue-url", required=True)
    record.add_argument("--text-file", required=True)
    record.add_argument("--run-id", default="")
    record.add_argument("--run-url", default="")

    args = parser.parse_args()

    if args.command == "check":
        should_send = check_sent(args.sent_log, args.issue, args.lang, parse_bool(args.force))
        if should_send:
            print(f"Telegram announcement can be sent: issue={args.issue}, lang={args.lang}")
        else:
            print(
                f"Telegram announcement already sent: issue={args.issue}, lang={args.lang}. "
                "Use force=true in workflow_dispatch to resend."
            )
        return

    if args.command == "record":
        record = record_sent(
            path=args.sent_log,
            issue=args.issue,
            lang=args.lang,
            issue_url=args.issue_url,
            text_file=args.text_file,
            run_id=args.run_id,
            run_url=args.run_url,
        )
        print(json.dumps(record, ensure_ascii=False, sort_keys=True))
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - CLI should print a clear terminal error.
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
