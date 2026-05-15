from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build_site_into(out_dir: Path) -> None:
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

def test_contact_page_exists_and_mailboxes_are_clickable(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    html = (out_dir / "contact.html").read_text(encoding="utf-8")

    assert 'href="mailto:editor@osintsignal.org"' in html
    assert 'href="mailto:tips@osintsignal.org"' in html
    assert 'href="mailto:tools@osintsignal.org"' in html
    assert 'href="mailto:sources@osintsignal.org"' in html
    assert "live targeting information" in html

def test_subscribe_links_are_clickable(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    html = (out_dir / "subscribe.html").read_text(encoding="utf-8")

    assert 'href="https://t.me/open_source_signal_ua"' in html
    assert 'href="feed.xml"' in html
    assert 'href="archive.html"' in html

def test_contact_is_in_sitemap_and_404_is_not(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    sitemap = (out_dir / "sitemap.xml").read_text(encoding="utf-8")

    assert "contact.html" in sitemap
    assert "404.html" not in sitemap
