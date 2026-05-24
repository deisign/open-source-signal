from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY_W21 = ROOT / "weekly" / "open-source-signal-weekly-2026-W21.json"
SCRIPT = ROOT / "scripts" / "render_weekly_telegram.py"


def run_renderer(out_dir: Path, max_chars: int = 1800) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(WEEKLY_W21),
            "--config",
            str(ROOT / "site.json"),
            "--out-dir",
            str(out_dir),
            "--max-chars",
            str(max_chars),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def test_weekly_telegram_renderer_writes_public_text_and_json(tmp_path: Path) -> None:
    result = run_renderer(tmp_path)
    assert "chars:" in result.stdout

    txt_path = tmp_path / "open-source-signal-weekly-2026-W21.txt"
    json_path = tmp_path / "open-source-signal-weekly-2026-W21.json"

    assert txt_path.exists()
    assert json_path.exists()

    text = txt_path.read_text(encoding="utf-8")

    assert len(text) <= 1800
    assert "Open Source Signal Weekly W21" in text
    assert "Читати тижневий випуск" in text
    assert "https://osintsignal.org/weekly/open-source-signal-weekly-2026-W21.html" in text

    assert "Editorial use:" not in text
    assert "Lead section; useful as" not in text
    assert "internal_notes" not in text

    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["kind"] == "weekly_telegram_announcement"
    assert payload["parse_mode"] == "HTML"
    assert payload["disable_web_page_preview"] is False
    assert payload["char_count"] == len(text)
    assert payload["text"] == text


def test_weekly_telegram_renderer_respects_short_limit(tmp_path: Path) -> None:
    run_renderer(tmp_path, max_chars=700)

    text = (tmp_path / "open-source-signal-weekly-2026-W21.txt").read_text(encoding="utf-8")

    assert len(text) <= 700
    assert "Open Source Signal Weekly W21" in text
    assert "Читати тижневий випуск" in text
    assert "Editorial use:" not in text
