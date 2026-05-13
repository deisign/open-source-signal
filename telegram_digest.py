#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path
from typing import Any, Literal

from render_issue import load_issue

Lang = Literal["en", "uk"]

FIELD_MAP = {
    "en": {
        "title": "OPEN SOURCE SIGNAL — Daily Signal",
        "issue": "Issue",
        "full_issue": "Full issue",
        "source": "Source",
        "items_heading": "Today’s signals",
    },
    "uk": {
        "title": "СИГНАЛ ВІДКРИТИХ ДЖЕРЕЛ — Daily Signal",
        "issue": "Випуск",
        "full_issue": "Повний випуск",
        "source": "Джерело",
        "items_heading": "Сьогодні в сигналах",
    },
}


def _first_sentence(text: str) -> str:
    clean = " ".join(text.split())
    parts = re.split(r"(?<=[.!?])\s+", clean, maxsplit=1)
    return parts[0] if parts and parts[0] else clean


def _shorten(text: str, width: int = 230) -> str:
    return textwrap.shorten(text, width=width, placeholder="…")


def _issue_date(issue: dict[str, Any], lang: Lang) -> str:
    if lang == "uk":
        return str(issue.get("date_label_uk") or issue["date_iso"])
    return str(issue.get("date_label_en") or issue["date_iso"])


def _item_title(item: dict[str, Any], lang: Lang) -> str:
    return str(item[f"title_{lang}"])


def _item_rubric(item: dict[str, Any], lang: Lang) -> str:
    rubric_key = "rubric_uk" if lang == "uk" else "rubric_en"
    return str(item[rubric_key])


def _item_summary(item: dict[str, Any], lang: Lang) -> str:
    source_field = "what_happened_uk" if lang == "uk" else "what_happened_en"
    return _shorten(_first_sentence(str(item[source_field])))


def render_telegram_digest(issue: dict[str, Any], lang: Lang, full_issue_url: str, max_items: int = 7) -> str:
    if lang not in FIELD_MAP:
        raise ValueError("lang must be 'en' or 'uk'")
    if not full_issue_url.strip():
        raise ValueError("full_issue_url must be a non-empty string")
    if max_items < 1:
        raise ValueError("max_items must be at least 1")

    labels = FIELD_MAP[lang]
    date = _issue_date(issue, lang)
    issue_number = str(issue.get("issue_number", "")).strip()

    lines: list[str] = [
        f"{labels['title']} #{issue_number}" if issue_number else labels["title"],
        date,
        "",
        labels["items_heading"] + ":",
        "",
    ]

    for idx, item in enumerate(issue["items"][:max_items], start=1):
        emoji = str(item.get("emoji", "•"))
        rubric = _item_rubric(item, lang)
        title = _item_title(item, lang)
        summary = _item_summary(item, lang)
        source_name = str(item["source_name"])
        lines.extend(
            [
                f"{idx}. {emoji} {rubric}",
                title,
                summary,
                f"{labels['source']}: {source_name}",
                "",
            ]
        )

    lines.extend([f"{labels['full_issue']}: {full_issue_url}", ""])
    return "\n".join(lines).rstrip() + "\n"


def output_filename(issue: dict[str, Any], lang: Lang) -> str:
    slug = str(issue.get("slug", "open-source-signal"))
    date_iso = str(issue["date_iso"])
    return f"telegram-{slug}-{date_iso}.{lang}.txt"


def write_telegram_digest(issue_path: Path, lang: Lang, full_issue_url: str, out_dir: Path, max_items: int = 7) -> Path:
    issue = load_issue(issue_path)
    text = render_telegram_digest(issue, lang, full_issue_url, max_items=max_items)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / output_filename(issue, lang)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Telegram announcement from an Open Source Signal issue JSON.")
    parser.add_argument("issue_json", type=Path, help="Path to an issue JSON file")
    parser.add_argument("--lang", choices=["en", "uk"], required=True, help="Announcement language")
    parser.add_argument("--url", required=True, help="URL of the full HTML issue")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output directory")
    parser.add_argument("--max-items", type=int, default=7, help="Maximum number of items to include")
    args = parser.parse_args()

    out_path = write_telegram_digest(args.issue_json, args.lang, args.url, args.out, max_items=args.max_items)
    print(out_path)


if __name__ == "__main__":
    main()
