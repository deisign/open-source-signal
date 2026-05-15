import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def sample_weekly() -> dict:
    base_item = {
        "title_en": "A stronger verification workflow for accountability OSINT",
        "title_uk": "Сильніший workflow для accountability OSINT",
        "source_name": "Open Source Signal test source",
        "source_url": "https://osintsignal.org/methodology.html",
        "source_date_label_en": "17 May 2026",
        "source_date_label_uk": "17 травня 2026",
        "why_it_matters_en": "The item shows how a weekly issue should explain public-interest value rather than merely collect links.",
        "why_it_matters_uk": "Матеріал показує, як weekly-випуск має пояснювати суспільну цінність, а не просто збирати посилання.",
        "limits_en": "Synthetic test item; not a public factual claim.",
        "limits_uk": "Синтетичний тестовий пункт; не є публічним фактичним твердженням.",
        "tags": ["weekly", "verification", "accountability"],
    }
    sections = [
        ("signal-of-the-week", "Signal of the Week", "Сигнал тижня"),
        ("ukraine-lens", "Ukraine Lens", "Українська оптика"),
        ("war-crimes-verification", "War Crimes Verification", "Верифікація воєнних злочинів"),
        ("losses-captivity-missing", "Losses, Captivity & Missing", "Втрати, полон, зниклі"),
        ("tradecraft", "Tradecraft", "Методика"),
        ("tools-datasets", "Tools / Datasets", "Інструменти / датасети"),
        ("risk-watch", "Risk Watch", "Межі й ризики"),
    ]
    return {
        "issue_number": "W001",
        "week_start_iso": "2026-05-11",
        "week_end_iso": "2026-05-17",
        "date_label_en": "17 May 2026",
        "date_label_uk": "17 травня 2026",
        "slug": "weekly-open-source-signal",
        "issue_type": "Weekly Magazine",
        "language_label": "EN + UKR",
        "title_en": "Open Source Signal Weekly Magazine",
        "title_uk": "Сигнал відкритих джерел: тижневик",
        "dek_en": "A Sunday editorial issue for the strongest accountability OSINT signals of the week.",
        "dek_uk": "Недільний редакційний випуск про найсильніші accountability OSINT-сигнали тижня.",
        "editorial_note_en": "This weekly issue turns selected signals into a structured editorial map.",
        "editorial_note_uk": "Цей weekly-випуск перетворює вибрані сигнали на структуровану редакційну карту.",
        "sections": [
            {"key": key, "heading_en": heading_en, "heading_uk": heading_uk, "summary_en": f"Editorial summary for {heading_en}.", "summary_uk": f"Редакційне резюме для {heading_uk}.", "items": [dict(base_item)]}
            for key, heading_en, heading_uk in sections
        ],
        "reading_list": [{"title": "Methodology — Open Source Signal", "source_name": "Open Source Signal", "source_url": "https://osintsignal.org/methodology.html", "note_en": "A trust-page reference for source handling and verification limits.", "note_uk": "Trust-page посилання про роботу з джерелами й межі верифікації."}],
        "internal_notes": ["This internal note must not be rendered in public HTML."],
    }


def test_render_weekly_template_creates_public_html_without_internal_notes(tmp_path):
    weekly_json = tmp_path / "weekly.json"
    weekly_json.write_text(json.dumps(sample_weekly(), ensure_ascii=False, indent=2), encoding="utf-8")
    out_dir = tmp_path / "weekly-dist"
    result = subprocess.run([sys.executable, str(ROOT / "render_weekly.py"), str(weekly_json), "--template", str(ROOT / "templates" / "weekly.html.j2"), "--out", str(out_dir)], check=True, capture_output=True, text=True, cwd=ROOT)
    out_file = out_dir / "weekly-open-source-signal-2026-05-17.html"
    assert out_file.exists()
    assert str(out_file) in result.stdout
    text = BeautifulSoup(out_file.read_text(encoding="utf-8"), "html.parser").get_text(" ", strip=True)
    assert "Weekly Magazine" in text
    assert "Signal of the Week" in text
    assert "Ukraine Lens" in text
    assert "War Crimes Verification" in text
    assert "Losses, Captivity & Missing" in text
    assert "Reading List" in text
    assert "This internal note must not be rendered" not in text


def test_render_weekly_rejects_missing_required_fields(tmp_path):
    weekly_json = tmp_path / "broken-weekly.json"
    data = sample_weekly()
    data.pop("sections")
    weekly_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "render_weekly.py"), str(weekly_json), "--template", str(ROOT / "templates" / "weekly.html.j2"), "--out", str(tmp_path / "out")], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Missing required weekly field: sections" in result.stderr
