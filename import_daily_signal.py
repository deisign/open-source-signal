#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from create_issue import build_draft_issue, parse_iso_date, normalize_issue_number
from render_issue import validate_issue

LANG_LABELS = {
    "en": {
        "source": ["Source"],
        "what": ["What happened"],
        "why": ["Why it matters"],
        "how": ["How to use it", "How to use"],
        "limits": ["Limits", "Limitations"],
        "tags": ["Tags"],
    },
    "uk": {
        "source": ["Джерело"],
        "what": ["Що сталося"],
        "why": ["Чому це важливо"],
        "how": ["Як використати", "Як це застосувати", "Як застосувати"],
        "limits": ["Обмеження", "Межі"],
        "tags": ["Теги"],
    },
}

RUBRIC_META = {
    "Signal One": ("signal", "📡"),
    "Головний сигнал": ("signal", "📡"),
    "Toolbox": ("toolbox", "🧰"),
    "Інструментарій": ("toolbox", "🧰"),
    "Tradecraft": ("tradecraft", "🧭"),
    "Методика": ("tradecraft", "🧭"),
    "Map Room": ("map-room", "🗺️"),
    "Картографічна кімната": ("map-room", "🗺️"),
    "Platform Watch": ("platform", "🔎"),
    "Платформний радар": ("platform", "🔎"),
    "Surveillance Watch": ("surveillance", "🛰️"),
    "Інфраструктура стеження": ("surveillance", "🛰️"),
    "Investigator OPSEC": ("opsec", "🛡️"),
    "Безпека дослідника": ("opsec", "🛡️"),
    "Infrastructure Signals": ("infrastructure", "🌐"),
    "Інфраструктурні сигнали": ("infrastructure", "🌐"),
    "AI Verification": ("ai", "🤖"),
    "ШІ та верифікація": ("ai", "🤖"),
    "Casefile": ("casefile", "📁"),
    "Розбір кейсу": ("casefile", "📁"),
    "Risk Watch": ("risk", "⚠️"),
    "Межі й ризики": ("risk", "⚠️"),
    "Ukraine Lens": ("ukraine", "🇺🇦"),
    "Українська оптика": ("ukraine", "🇺🇦"),
    "War Crimes Verification": ("war-crimes", "⚖️"),
    "Верифікація воєнних злочинів": ("war-crimes", "⚖️"),
    "Losses, Captivity & Missing": ("losses", "🕯️"),
    "Втрати, полон, зниклі": ("losses", "🕯️"),
    "Telegram Radar": ("telegram", "📨"),
    "Telegram-радар": ("telegram", "📨"),
}

CITATION_RE = re.compile(r"\ue200cite\ue202[^\ue201]+\ue201")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)\]]+")
ITEM_HEADING_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*$", re.MULTILINE)
LANG_HEADING_RE = re.compile(r"^###\s+(EN|UK|UA|Українська|English)\s+[—-]\s+(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
BOLD_LABEL_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")


FIELD_ORDER = ["source", "what", "why", "how", "limits", "tags"]
FIELD_LABELS = {
    "en": {
        "source": "Source",
        "what": "What happened",
        "why": "Why it matters",
        "how": "How to use it",
        "limits": "Limits",
        "tags": "Tags",
    },
    "uk": {
        "source": "Джерело",
        "what": "Що сталося",
        "why": "Чому це важливо",
        "how": "Як використати",
        "limits": "Обмеження",
        "tags": "Теги",
    },
}


def summarize_block(text: str, limit: int = 120) -> str:
    clean = clean_inline(text)
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def format_missing_fields(lang: str, fields: list[str]) -> str:
    labels = ", ".join(FIELD_LABELS[lang][field] for field in fields)
    lang_name = "EN" if lang == "en" else "UK"
    return f"{lang_name} section is missing: {labels}"


def strip_citations(text: str) -> str:
    return CITATION_RE.sub("", text)


def clean_inline(text: str) -> str:
    text = strip_citations(text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_internal_notes(text: str) -> tuple[str, list[str]]:
    pattern = re.compile(r"^#*\s*EDITORIAL NOTES\s+[—-]\s+INTERNAL\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return text, []
    public = text[: match.start()].rstrip()
    notes_text = text[match.end() :].strip()
    notes: list[str] = []
    for raw in notes_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = clean_inline(line)
        if line:
            notes.append(line)
    return public, notes


def _iter_heading_blocks(text: str, regex: re.Pattern[str]) -> Iterable[tuple[re.Match[str], str]]:
    matches = list(regex.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        yield match, text[start:end].strip()


def split_rubric(value: str) -> tuple[str, str]:
    value = clean_inline(value)
    parts = [p.strip() for p in re.split(r"\s+/\s+", value, maxsplit=1)]
    if len(parts) == 2:
        return parts[0], parts[1]
    if value in RUBRIC_META:
        # Known one-language rubric: keep same for both as a fallback.
        return value, value
    return value, value


def lang_code(label: str) -> str:
    normalized = label.strip().lower()
    if normalized in {"uk", "ua", "українська"}:
        return "uk"
    return "en"


def parse_labelled_fields(block: str, lang: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    label_to_key: dict[str, str] = {}
    for key, labels in LANG_LABELS[lang].items():
        for label in labels:
            label_to_key[label.casefold()] = key

    def flush() -> None:
        nonlocal current_key, current_lines
        if current_key:
            value = "\n".join(current_lines).strip()
            fields[current_key] = clean_inline(value)
        current_key = None
        current_lines = []

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        match = BOLD_LABEL_RE.match(line.strip())
        if match:
            label = clean_inline(match.group(1)).casefold()
            if label in label_to_key:
                flush()
                current_key = label_to_key[label]
                current_lines = [match.group(2).strip()] if match.group(2).strip() else []
                continue
        if current_key is not None:
            current_lines.append(line.strip())
    flush()
    return fields


def parse_source(source_text: str, fallback_url: str = "") -> tuple[str, str]:
    clean = clean_inline(source_text)
    name = clean
    if " — " in name:
        name = name.split(" — ", 1)[0].strip()
    if "," in name:
        name = name.split(",", 1)[0].strip()
    if " - " in name:
        name = name.split(" - ", 1)[0].strip()
    url = fallback_url or ""
    if not url:
        match = URL_RE.search(source_text)
        url = match.group(0).rstrip(".,") if match else ""
    if not name:
        parsed = urlparse(url)
        name = parsed.netloc or "Source"
    return name, url


def extract_first_url(text: str) -> str:
    md = MD_LINK_RE.search(text)
    if md:
        return md.group(2)
    plain = URL_RE.search(text)
    return plain.group(0).rstrip(".,") if plain else ""


def parse_tags(value: str) -> list[str]:
    tags = re.findall(r"`([^`]+)`", value)
    if not tags:
        cleaned = clean_inline(value)
        tags = [part.strip(" #") for part in re.split(r"[,;]", cleaned)]
    result: list[str] = []
    for tag in tags:
        tag = clean_inline(tag).strip()
        if tag and tag not in result:
            result.append(tag)
    return result[:8]


def build_item(rubric_heading: str, body: str, issue_date_en: str, issue_date_uk: str) -> dict[str, Any]:
    rubric_en, rubric_uk = split_rubric(rubric_heading)
    theme, emoji = RUBRIC_META.get(rubric_en, RUBRIC_META.get(rubric_uk, ("signal", "•")))

    lang_blocks: dict[str, tuple[str, str]] = {}
    for match, lang_body in _iter_heading_blocks(body, LANG_HEADING_RE):
        lang = lang_code(match.group(1))
        title = clean_inline(match.group(2))
        lang_blocks[lang] = (title, lang_body)

    missing_langs = [lang.upper() for lang in ("en", "uk") if lang not in lang_blocks]
    if missing_langs:
        raise ValueError(
            f"Rubric '{rubric_heading}' must contain both EN and UK sections; missing: {', '.join(missing_langs)}. "
            f"Preview: {summarize_block(body)}"
        )

    title_en, body_en = lang_blocks["en"]
    title_uk, body_uk = lang_blocks["uk"]
    en_fields = parse_labelled_fields(body_en, "en")
    uk_fields = parse_labelled_fields(body_uk, "uk")

    missing_en = [key for key in FIELD_ORDER if key not in en_fields]
    missing_uk = [key for key in FIELD_ORDER if key not in uk_fields]
    if missing_en or missing_uk:
        details = []
        if missing_en:
            details.append(format_missing_fields("en", missing_en))
        if missing_uk:
            details.append(format_missing_fields("uk", missing_uk))
        raise ValueError(f"Item '{title_en}' has an invalid structure: {'; '.join(details)}")

    fallback_url = extract_first_url(en_fields["source"] + " " + uk_fields["source"] + " " + body_en + " " + body_uk)
    source_name, source_url = parse_source(en_fields["source"], fallback_url=fallback_url)
    if not source_url:
        raise ValueError(
            f"Item '{title_en}' does not contain a source URL. Add a markdown link or plain URL to the Source/Джерело line."
        )

    return {
        "theme": theme,
        "emoji": emoji,
        "rubric_en": rubric_en,
        "rubric_uk": rubric_uk,
        "title_en": title_en,
        "title_uk": title_uk,
        "source_name": source_name,
        "source_url": source_url,
        "source_date_label_en": issue_date_en,
        "source_date_label_uk": issue_date_uk,
        "what_happened_en": en_fields["what"],
        "what_happened_uk": uk_fields["what"],
        "why_it_matters_en": en_fields["why"],
        "why_it_matters_uk": uk_fields["why"],
        "how_to_use_en": en_fields["how"],
        "how_to_use_uk": uk_fields["how"],
        "limits_en": en_fields["limits"],
        "limits_uk": uk_fields["limits"],
        "tags": parse_tags(en_fields["tags"] or uk_fields["tags"]),
    }


def parse_daily_signal(markdown: str, date_value: str, issue_number: str) -> dict[str, Any]:
    markdown = markdown.replace("\r\n", "\n").replace("\r", "\n")
    public_text, internal_notes = split_internal_notes(markdown)

    day = parse_iso_date(date_value)
    issue = build_draft_issue(day, normalize_issue_number(issue_number))
    issue.pop("draft", None)

    item_blocks = list(_iter_heading_blocks(public_text, ITEM_HEADING_RE))
    items: list[dict[str, Any]] = []
    for index, (match, body) in enumerate(item_blocks, start=1):
        rubric_heading = match.group(1)
        if not LANG_HEADING_RE.search(body):
            continue
        try:
            items.append(build_item(rubric_heading, body, issue["date_label_en"], issue["date_label_uk"]))
        except ValueError as exc:
            raise ValueError(f"Item #{index} ({rubric_heading}): {exc}") from exc

    if not items:
        raise ValueError("No Daily Signal items found. Expected headings like '## 1. Signal One / Головний сигнал'.")

    issue["items"] = items
    issue["internal_notes"] = internal_notes
    issue["rubric_map"] = [f"{item['emoji']} {item['rubric_en']}" for item in items]
    titles = "; ".join(item["title_en"] for item in items[:4])
    issue["dek_en"] = f"Daily issue #{issue['issue_number']}: {titles}."
    validate_issue(issue)
    return issue


def import_daily_signal(input_path: Path, date_value: str, issue_number: str, out_dir: Path, force: bool = False) -> Path:
    markdown = input_path.read_text(encoding="utf-8")
    issue = parse_daily_signal(markdown, date_value, issue_number)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{issue['date_iso']}.json"
    if out_path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {out_path}. Use --force to replace it.")
    out_path.write_text(json.dumps(issue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a Daily Signal markdown/text issue into Open Source Signal JSON.")
    parser.add_argument("input", type=Path, help="Daily Signal markdown/text file")
    parser.add_argument("--date", required=True, help="Issue date in YYYY-MM-DD format")
    parser.add_argument("--issue", required=True, help="Issue number, for example 002")
    parser.add_argument("--out", type=Path, default=Path("issues"), help="Output directory, usually issues/ or drafts/")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output JSON")
    args = parser.parse_args()

    out_path = import_daily_signal(args.input, args.date, args.issue, args.out, force=args.force)
    print(out_path)


if __name__ == "__main__":
    main()
