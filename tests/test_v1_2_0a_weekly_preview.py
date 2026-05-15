from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_weekly_preview_renderer_creates_html(tmp_path: Path) -> None:
    out_dir = tmp_path / "weekly"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "render_weekly.py"),
            str(ROOT / "weekly" / "open-source-signal-weekly-2026-W20.json"),
            "--templates",
            str(ROOT / "templates"),
            "--out",
            str(out_dir),
            "--config",
            str(ROOT / "site.json"),
        ],
        check=True,
        cwd=ROOT,
    )

    html_path = out_dir / "open-source-signal-weekly-2026-W20.html"
    assert html_path.exists()

    html = html_path.read_text(encoding="utf-8")
    assert "Open Source Signal Weekly" in html
    assert "Тижневий сигнал відкритих джерел" in html
    assert "logo-mark.png" in html
    assert "theme-war-crimes" in html
    assert "theme-ukraine" in html
    assert "theme-losses" in html
    assert "language-toggle" in html
    assert 'data-lang="both"' in html


def test_weekly_template_avoids_jinja_dict_method_collisions() -> None:
    template = (ROOT / "templates" / "weekly.html.j2").read_text(encoding="utf-8")

    assert "weekly.items" not in template
    assert "block.items" not in template
    assert 'weekly["items"]' in template
