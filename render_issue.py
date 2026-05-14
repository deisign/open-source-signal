#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

REQUIRED_ISSUE_FIELDS = [
    "issue_number", "date_iso", "date_label_en", "title_en", "title_uk",
    "slug", "issue_type", "subtitle_en", "dek_en", "items", "internal_notes",
]

REQUIRED_ITEM_FIELDS = [
    "theme", "emoji", "rubric_en", "rubric_uk", "title_en", "title_uk",
    "source_name", "source_url", "source_date_label_en", "source_date_label_uk",
    "what_happened_en", "what_happened_uk", "why_it_matters_en", "why_it_matters_uk",
    "how_to_use_en", "how_to_use_uk", "limits_en", "limits_uk", "tags",
]


def load_issue(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        issue = json.load(f)
    validate_issue(issue)
    return issue


def _assert_non_empty_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string")


def validate_issue(issue: dict[str, Any]) -> None:
    for field in REQUIRED_ISSUE_FIELDS:
        if field not in issue:
            raise ValueError(f"Missing required issue field: {field}")

    for field in ["issue_number", "date_iso", "title_en", "title_uk", "slug"]:
        _assert_non_empty_string(issue[field], field)

    if not isinstance(issue["items"], list) or not issue["items"]:
        raise ValueError("Field 'items' must be a non-empty list")

    if not isinstance(issue["internal_notes"], list):
        raise ValueError("Field 'internal_notes' must be a list")

    for idx, item in enumerate(issue["items"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Item #{idx} must be an object")
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                raise ValueError(f"Missing required field in item #{idx}: {field}")
        for field in REQUIRED_ITEM_FIELDS:
            if field == "tags":
                if not isinstance(item[field], list) or not item[field]:
                    raise ValueError(f"Item #{idx} field 'tags' must be a non-empty list")
                continue
            _assert_non_empty_string(item[field], f"items[{idx}].{field}")


def output_filename(issue: dict[str, Any]) -> str:
    return f"{issue['slug']}-{issue['date_iso']}.html"


def render_issue(issue_path: Path, template_path: Path, out_dir: Path) -> Path:
    issue = load_issue(issue_path)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    html = template.render(issue=issue, asset_prefix="")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / output_filename(issue)
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Open Source Signal issue JSON into HTML.")
    parser.add_argument("issue_json", type=Path, help="Path to an issue JSON file")
    parser.add_argument("--template", type=Path, default=Path("templates/issue.html.j2"), help="Path to Jinja HTML template")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output directory")
    args = parser.parse_args()

    out_path = render_issue(args.issue_json, args.template, args.out)
    print(out_path)


if __name__ == "__main__":
    main()
