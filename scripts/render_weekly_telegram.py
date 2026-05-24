#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

INTERNAL_MARKERS = (
    "Editorial use:",
    "internal_notes",
    "internal_editorial_notes",
    "private_notes",
    "Lead section; useful as",
)

DEFAULT_HASHTAGS = ["#OSINT", "#Ukraine", "#Verification", "#WarCrimes"]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def normalize_ws(value: Any) -> str:
    text = str(value or "")
    return re.sub(r"\s+", " ", text).strip()


def ellipsize(text: str, limit: int) -> str:
    text = normalize_ws(text)
    if len(text) <= limit:
        return text
    cut = text[: max(0, limit - 1)].rstrip()
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0].rstrip()
    return cut + "…"


def absolute_url(base_url: str, path: str) -> str:
    base = str(base_url or "").rstrip("/")
    return f"{base}/{path.lstrip('/')}" if base else path


def weekly_url(weekly: dict[str, Any], config: dict[str, Any]) -> str:
    output_name = str(weekly.get("output_name") or f"{weekly['slug']}.html")
    return absolute_url(str(config.get("base_url", "")), f"weekly/{output_name}")


def item_bullet(item: dict[str, Any], limit: int = 158) -> str:
    rubric = normalize_ws(item.get("rubric_uk") or item.get("rubric_en") or "Signal")
    title = normalize_ws(item.get("title_uk") or item.get("title_en") or "")
    raw = f"{rubric}: {title}" if title else rubric
    return "• " + html.escape(ellipsize(raw, limit), quote=False)


def build_post(
    weekly: dict[str, Any],
    config: dict[str, Any],
    max_items: int = 4,
    max_chars: int = 1800,
) -> tuple[str, str]:
    issue_number = normalize_ws(weekly.get("issue_number"))
    week_label = normalize_ws(weekly.get("week_label_uk") or weekly.get("week_label_en"))
    lead_source = weekly.get("dek_uk") or weekly.get("editorial_note_uk") or weekly.get("dek_en") or ""
    url = weekly_url(weekly, config)
    safe_url = html.escape(url, quote=True)

    items = [item for item in weekly.get("items", []) if isinstance(item, dict)]
    items = items[: max(0, max_items)]

    def render(item_count: int, lead_limit: int, bullet_limit: int) -> str:
        lead = html.escape(ellipsize(str(lead_source), lead_limit), quote=False)
        lines = [
            f"🛰 <b>Open Source Signal Weekly {html.escape(issue_number, quote=False)}</b>",
            f"<i>{html.escape(week_label, quote=False)}</i>",
            "",
            lead,
        ]

        chosen = items[:item_count]
        if chosen:
            lines.extend(["", "<b>У випуску:</b>"])
            lines.extend(item_bullet(item, bullet_limit) for item in chosen)

        lines.extend(
            [
                "",
                f'<a href="{safe_url}">Читати тижневий випуск</a>',
                "",
                " ".join(DEFAULT_HASHTAGS),
            ]
        )
        return "\n".join(lines).strip() + "\n"

    for item_count in range(len(items), 0, -1):
        for lead_limit in (360, 280, 220, 160, 120):
            for bullet_limit in (158, 130, 110, 90):
                post = render(item_count, lead_limit, bullet_limit)
                if len(post) <= max_chars:
                    return post, url

    for lead_limit in (160, 120, 90, 60):
        post = render(0, lead_limit, 90)
        if len(post) <= max_chars:
            return post, url

    raise ValueError(f"Cannot render Telegram post within {max_chars} characters")


def assert_public_text(text: str) -> None:
    found = [marker for marker in INTERNAL_MARKERS if marker in text]
    if found:
        raise ValueError("Public Telegram text contains internal marker(s): " + ", ".join(found))


def write_outputs(
    weekly_path: Path,
    config_path: Path,
    out_dir: Path,
    max_items: int,
    max_chars: int,
) -> tuple[Path, Path, int]:
    weekly = load_json(weekly_path)
    config = load_json(config_path) if config_path.exists() else {}

    text, url = build_post(weekly, config, max_items=max_items, max_chars=max_chars)
    assert_public_text(text)

    slug = str(weekly.get("slug") or weekly_path.stem)
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = out_dir / f"{slug}.txt"
    json_path = out_dir / f"{slug}.json"

    txt_path.write_text(text, encoding="utf-8")

    payload = {
        "kind": "weekly_telegram_announcement",
        "issue_number": weekly.get("issue_number"),
        "date_iso": weekly.get("date_iso"),
        "source_weekly_json": str(weekly_path),
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "url": url,
        "char_count": len(text),
        "text": text,
    }

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return txt_path, json_path, len(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a weekly Open Source Signal Telegram announcement.")
    parser.add_argument("weekly_json", type=Path)
    parser.add_argument("--config", type=Path, default=Path("site.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("telegram/weekly"))
    parser.add_argument("--max-items", type=int, default=4)
    parser.add_argument("--max-chars", type=int, default=1800)
    parser.add_argument("--print-text", action="store_true")
    args = parser.parse_args()

    txt_path, json_path, char_count = write_outputs(
        args.weekly_json,
        args.config,
        args.out_dir,
        args.max_items,
        args.max_chars,
    )

    print(f"text: {txt_path}")
    print(f"json: {json_path}")
    print(f"chars: {char_count}")

    if args.print_text:
        print()
        print(txt_path.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
