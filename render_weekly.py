#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

DEFAULT_SITE_CONFIG = {
    "site_title_en": "Open Source Signal",
    "site_title_uk": "Сигнал відкритих джерел",
    "site_description_en": "A bilingual OSINT editorial radar for investigations, verification, maps, platforms, surveillance and researcher safety.",
    "site_description_uk": "Двомовний OSINT-радар про розслідування, верифікацію, мапи, платформи, інфраструктуру стеження й безпеку дослідника.",
    "base_url": "",
    "telegram_url": "https://t.me/open_source_signal_ua",
    "rss_path": "feed.xml",
}

REQUIRED_WEEKLY_FIELDS = [
    "issue_number",
    "week_start_iso",
    "week_end_iso",
    "date_label_en",
    "date_label_uk",
    "slug",
    "issue_type",
    "language_label",
    "title_en",
    "title_uk",
    "dek_en",
    "dek_uk",
    "editorial_note_en",
    "editorial_note_uk",
    "sections",
    "reading_list",
    "internal_notes",
]

REQUIRED_SECTION_FIELDS = ["key", "heading_en", "heading_uk", "summary_en", "summary_uk", "items"]

REQUIRED_WEEKLY_ITEM_FIELDS = [
    "title_en",
    "title_uk",
    "source_name",
    "source_url",
    "source_date_label_en",
    "source_date_label_uk",
    "why_it_matters_en",
    "why_it_matters_uk",
    "limits_en",
    "limits_uk",
    "tags",
]

REQUIRED_READING_FIELDS = ["title", "source_name", "source_url", "note_en", "note_uk"]


def _assert_non_empty_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string")


def validate_weekly(issue: dict[str, Any]) -> None:
    for field in REQUIRED_WEEKLY_FIELDS:
        if field not in issue:
            raise ValueError(f"Missing required weekly field: {field}")
    for field in [
        "issue_number", "week_start_iso", "week_end_iso", "date_label_en", "date_label_uk",
        "slug", "issue_type", "language_label", "title_en", "title_uk", "dek_en", "dek_uk",
        "editorial_note_en", "editorial_note_uk",
    ]:
        _assert_non_empty_string(issue[field], field)
    if issue["issue_type"] != "Weekly Magazine":
        raise ValueError("Field 'issue_type' must be 'Weekly Magazine'")
    if not isinstance(issue["sections"], list) or not issue["sections"]:
        raise ValueError("Field 'sections' must be a non-empty list")
    if not isinstance(issue["reading_list"], list):
        raise ValueError("Field 'reading_list' must be a list")
    if not isinstance(issue["internal_notes"], list):
        raise ValueError("Field 'internal_notes' must be a list")
    for section_index, section in enumerate(issue["sections"], start=1):
        if not isinstance(section, dict):
            raise ValueError(f"Section #{section_index} must be an object")
        for field in REQUIRED_SECTION_FIELDS:
            if field not in section:
                raise ValueError(f"Missing required field in section #{section_index}: {field}")
        for field in ["key", "heading_en", "heading_uk", "summary_en", "summary_uk"]:
            _assert_non_empty_string(section[field], f"sections[{section_index}].{field}")
        if not isinstance(section["items"], list) or not section["items"]:
            raise ValueError(f"Section #{section_index} field 'items' must be a non-empty list")
        for item_index, item in enumerate(section["items"], start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Section #{section_index} item #{item_index} must be an object")
            for field in REQUIRED_WEEKLY_ITEM_FIELDS:
                if field not in item:
                    raise ValueError(f"Missing required field in section #{section_index} item #{item_index}: {field}")
            for field in REQUIRED_WEEKLY_ITEM_FIELDS:
                if field == "tags":
                    if not isinstance(item[field], list) or not item[field]:
                        raise ValueError(f"Section #{section_index} item #{item_index} field 'tags' must be a non-empty list")
                    continue
                _assert_non_empty_string(item[field], f"sections[{section_index}].items[{item_index}].{field}")
    for reading_index, reading in enumerate(issue["reading_list"], start=1):
        if not isinstance(reading, dict):
            raise ValueError(f"Reading list item #{reading_index} must be an object")
        for field in REQUIRED_READING_FIELDS:
            if field not in reading:
                raise ValueError(f"Missing required field in reading list item #{reading_index}: {field}")
            _assert_non_empty_string(reading[field], f"reading_list[{reading_index}].{field}")


def load_weekly(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Weekly issue must be a JSON object")
    validate_weekly(data)
    return data


def output_filename(issue: dict[str, Any]) -> str:
    return f"{issue['slug']}-{issue['week_end_iso']}.html"


def render_weekly(weekly_json: Path, template_path: Path, out_dir: Path) -> Path:
    weekly = load_weekly(weekly_json)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / output_filename(weekly)
    html = template.render(
        weekly=weekly,
        config=DEFAULT_SITE_CONFIG,
        asset_prefix="",
        page_url="",
        og_image_url="static/og-image.png",
    )
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an Open Source Signal Weekly Magazine JSON into HTML.")
    parser.add_argument("weekly_json", type=Path, help="Path to a weekly issue JSON file")
    parser.add_argument("--template", type=Path, default=Path("templates/weekly.html.j2"), help="Weekly Jinja template")
    parser.add_argument("--out", type=Path, default=Path("dist/weekly"), help="Output directory")
    args = parser.parse_args()
    out_path = render_weekly(args.weekly_json, args.template, args.out)
    print(out_path)


if __name__ == "__main__":
    main()
