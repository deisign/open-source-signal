#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

from render_issue import validate_issue

DEFAULT_TITLE_EN = "Open Source Signal"
DEFAULT_TITLE_UK = "Сигнал відкритих джерел"
DEFAULT_SLUG = "open-source-signal"
DEFAULT_ISSUE_TYPE = "Daily Signal"
DEFAULT_LANGUAGE_LABEL = "EN + UKR"
DEFAULT_SUBTITLE_EN = (
    "Bilingual OSINT radar for Ukrainian accountability work, verification, war-crimes documentation, "
    "losses/captivity/missing-persons research, maps, platforms, surveillance and researcher safety."
)
DEFAULT_DEK_EN = (
    "A daily editorial filter for public-interest OSINT with a Ukrainian accountability lens: "
    "what happened, why it matters, how readers can use the insight, and where the method, evidence or attribution has limits."
)
DEFAULT_EDITORIAL_FRAME = {
    "what_this_is": (
        "Not a list of tools, but a daily editorial filter for public-interest OSINT. "
        "Each item explains what happened, why it matters, how a reader can use the insight, "
        "and where the method or evidence has limits."
    ),
    "what_this_is_not": (
        "Doxxing, live targeting, stolen-data workflows, marketplace guides or 'find anyone by phone number' tricks."
    ),
}
DEFAULT_RUBRIC_MAP = [
    "📡 Signal One",
    "🇺🇦 Ukraine Lens",
    "⚖️ War Crimes Verification",
    "🕯️ Losses, Captivity & Missing",
    "📨 Telegram Radar",
    "🛰️ Surveillance Watch",
    "🗺️ Map Room",
    "🔎 Platform Watch",
    "🛡️ Investigator OPSEC",
    "🌐 Infrastructure Signals",
    "⚠️ Risk Watch",
    "🧰 Toolbox / when deserved",
]
DEFAULT_FOOTER_NOTE = (
    "Generated for Open Source Signal / Сигнал відкритих джерел. Fonts: Fraunces for Latin display, "
    "Source Serif 4 for Ukrainian display, Inter and JetBrains Mono via Google Fonts with local fallbacks."
)

EN_MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
}
UK_MONTHS_GENITIVE = {
    1: "січня", 2: "лютого", 3: "березня", 4: "квітня", 5: "травня", 6: "червня",
    7: "липня", 8: "серпня", 9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня",
}
ISSUE_NUMBER_RE = re.compile(r"^\d+$")


def parse_iso_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Date must use YYYY-MM-DD format: {value}") from exc


def date_label_en(day: date) -> str:
    return f"{day.day} {EN_MONTHS[day.month]} {day.year}"


def date_label_uk(day: date) -> str:
    return f"{day.day} {UK_MONTHS_GENITIVE[day.month]} {day.year}"


def infer_next_issue_number(search_dir: Path) -> str:
    numbers: list[int] = []
    for path in sorted(search_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        raw = str(data.get("issue_number", "")).strip()
        if ISSUE_NUMBER_RE.match(raw):
            numbers.append(int(raw))
    next_number = max(numbers, default=-1) + 1
    return f"{next_number:03d}"


def normalize_issue_number(value: str) -> str:
    if not ISSUE_NUMBER_RE.match(value):
        raise ValueError("Issue number must contain only digits, for example 001")
    return f"{int(value):03d}"


def build_draft_issue(day: date, issue_number: str) -> dict[str, Any]:
    return {
        "draft": True,
        "issue_number": issue_number,
        "date_iso": day.isoformat(),
        "date_label_en": date_label_en(day),
        "date_label_uk": date_label_uk(day),
        "slug": DEFAULT_SLUG,
        "title_en": DEFAULT_TITLE_EN,
        "title_uk": DEFAULT_TITLE_UK,
        "issue_type": DEFAULT_ISSUE_TYPE,
        "language_label": DEFAULT_LANGUAGE_LABEL,
        "subtitle_en": DEFAULT_SUBTITLE_EN,
        "dek_en": DEFAULT_DEK_EN,
        "editorial_frame": DEFAULT_EDITORIAL_FRAME,
        "rubric_map": DEFAULT_RUBRIC_MAP,
        "footer_note": DEFAULT_FOOTER_NOTE,
        "items": [],
        "internal_notes": [],
    }


def write_json(path: Path, data: dict[str, Any], force: bool = False) -> Path:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}. Use --force to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def create_draft(date_value: str, issue_number: str | None, out_dir: Path, infer_from: Path, force: bool = False) -> Path:
    day = parse_iso_date(date_value)
    normalized_issue = normalize_issue_number(issue_number) if issue_number else infer_next_issue_number(infer_from)
    issue = build_draft_issue(day, normalized_issue)
    return write_json(out_dir / f"{day.isoformat()}.json", issue, force=force)


def publish_draft(draft_path: Path, issues_dir: Path, force: bool = False) -> Path:
    data = json.loads(draft_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Draft issue must be a JSON object")
    data.pop("draft", None)
    validate_issue(data)
    target = issues_dir / f"{data['date_iso']}.json"
    return write_json(target, data, force=force)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or publish issue JSON files for Open Source Signal."
    )
    parser.add_argument("--date", help="Issue date in YYYY-MM-DD format")
    parser.add_argument("--issue", help="Issue number, for example 001. If omitted, infer next number from --infer-from")
    parser.add_argument("--out", type=Path, default=Path("drafts"), help="Directory for new draft JSON files")
    parser.add_argument("--infer-from", type=Path, default=Path("issues"), help="Directory used to infer the next issue number")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output file")
    parser.add_argument("--publish", type=Path, help="Validate and copy a completed draft JSON into the issues directory")
    parser.add_argument("--issues-dir", type=Path, default=Path("issues"), help="Directory for published issue JSON files")
    args = parser.parse_args()

    if args.publish:
        path = publish_draft(args.publish, args.issues_dir, force=args.force)
        print(path)
        return

    if not args.date:
        parser.error("--date is required unless --publish is used")

    path = create_draft(args.date, args.issue, args.out, args.infer_from, force=args.force)
    print(path)


if __name__ == "__main__":
    main()
