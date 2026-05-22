from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def build_full_site(out_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "build_site.py"),
            "--issues",
            str(ROOT / "issues"),
            "--templates",
            str(ROOT / "templates"),
            "--out",
            str(out_dir),
            "--config",
            str(ROOT / "site.json"),
            "--static",
            str(ROOT / "static"),
        ],
        check=True,
        cwd=ROOT,
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "build_weekly_site.py"),
            "--weekly",
            str(ROOT / "weekly"),
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


def test_weekly_section_builds_index_issue_home_and_sitemap(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_full_site(out_dir)

    weekly_index = out_dir / "weekly" / "index.html"
    weekly_issue = out_dir / "weekly" / "open-source-signal-weekly-2026-W20.html"
    assert weekly_index.exists()
    assert weekly_issue.exists()

    index_html = weekly_index.read_text(encoding="utf-8")
    assert "Open Source Signal Weekly" in index_html
    assert "open-source-signal-weekly-2026-W20.html" in index_html
    assert "logo-mark.png" in index_html

    home = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    home_links = {a.get("href") for a in home.select("a[href]")}
    assert "weekly/" in home_links
    assert "weekly/open-source-signal-weekly-2026-W20.html" in home_links
    assert home.select_one(".weekly-home-card") is not None

    archive = BeautifulSoup((out_dir / "archive.html").read_text(encoding="utf-8"), "html.parser")
    archive_links = {a.get("href") for a in archive.select("a[href]")}
    assert "weekly/" in archive_links
    assert "weekly/open-source-signal-weekly-2026-W20.html" in archive_links

    sitemap = (out_dir / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://osintsignal.org/weekly/" in sitemap
    assert "https://osintsignal.org/weekly/open-source-signal-weekly-2026-W20.html" in sitemap
    assert "https://osintsignal.org/404.html" not in sitemap


def test_pages_workflow_builds_weekly_after_static_site() -> None:
    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "python build_weekly_site.py --weekly weekly --templates templates --out dist --config site.json" in workflow
