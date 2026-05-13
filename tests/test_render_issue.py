import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def test_render_issue_creates_html(tmp_path):
    out_dir = tmp_path / "dist"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "render_issue.py"),
            str(ROOT / "issues" / "2026-05-13.json"),
            "--template",
            str(ROOT / "templates" / "issue.html.j2"),
            "--out",
            str(out_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    out_path = Path(result.stdout.strip())
    assert out_path.exists()
    assert out_path.name == "open-source-signal-2026-05-13.html"


def test_rendered_html_contains_expected_structure(tmp_path):
    out_dir = tmp_path / "dist"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "render_issue.py"),
            str(ROOT / "issues" / "2026-05-13.json"),
            "--template",
            str(ROOT / "templates" / "issue.html.j2"),
            "--out",
            str(out_dir),
        ],
        check=True,
    )
    html = (out_dir / "open-source-signal-2026-05-13.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.signal-card")
    assert len(cards) == 7
    assert soup.select_one(".ua-masthead").get_text(strip=True) == "Сигнал відкритих джерел"
    assert soup.select_one(".internal") is None
    assert "EDITORIAL NOTES — INTERNAL" not in html
    assert len(soup.select("a[href^='https://']")) >= 7
    assert "Source Serif 4" in html
    assert "Arimo" in html
    assert "--label-font: Arimo" in html
    assert "Cormorant" not in html


def test_issue_json_has_public_fields_for_each_language():
    issue = json.loads((ROOT / "issues" / "2026-05-13.json").read_text(encoding="utf-8"))
    required = [
        "title_en", "title_uk", "what_happened_en", "what_happened_uk",
        "why_it_matters_en", "why_it_matters_uk", "how_to_use_en", "how_to_use_uk",
        "limits_en", "limits_uk", "source_url",
    ]
    for item in issue["items"]:
        for field in required:
            assert item[field].strip(), field
