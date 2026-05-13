import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE = ROOT / "issues" / "2026-05-13.json"
FULL_URL = "https://example.org/issues/open-source-signal-2026-05-13.html"


def _run_digest(tmp_path, lang):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "telegram_digest.py"),
            str(ISSUE),
            "--lang",
            lang,
            "--url",
            FULL_URL,
            "--out",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    output_path = Path(result.stdout.strip())
    assert output_path.exists()
    return output_path.read_text(encoding="utf-8")


def test_telegram_digest_uk_uses_ukrainian_fields(tmp_path):
    text = _run_digest(tmp_path, "uk")
    assert "СИГНАЛ ВІДКРИТИХ ДЖЕРЕЛ" in text
    assert "13 травня 2026" in text
    assert "Головний сигнал" in text
    assert "Стеження переходить" in text
    assert "Повний випуск" in text
    assert FULL_URL in text
    assert "What happened" not in text


def test_telegram_digest_en_uses_english_fields(tmp_path):
    text = _run_digest(tmp_path, "en")
    assert "OPEN SOURCE SIGNAL" in text
    assert "13 May 2026" in text
    assert "Signal One" in text
    assert "Telecom surveillance" in text
    assert "Full issue" in text
    assert FULL_URL in text
    assert "Що сталося" not in text


def test_telegram_digest_respects_max_items(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "telegram_digest.py"),
            str(ISSUE),
            "--lang",
            "uk",
            "--url",
            FULL_URL,
            "--out",
            str(tmp_path),
            "--max-items",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    text = Path(result.stdout.strip()).read_text(encoding="utf-8")
    assert "1. " in text
    assert "2. " in text
    assert "3. " in text
    assert "4. " not in text
