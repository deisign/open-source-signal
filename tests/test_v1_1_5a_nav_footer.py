import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

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


def soup(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def test_homepage_exposes_trust_pages_above_latest_issue(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    page = BeautifulSoup(html, "html.parser")

    nav = page.select_one('nav.home-trust-strip[aria-label="Trust and discovery on homepage"]')
    assert nav is not None

    links = {a.get_text(" ", strip=True): a.get("href") for a in nav.select("a[href]")}
    assert links == {
        "About": "about.html",
        "Methodology": "methodology.html",
        "Ethics": "ethics.html",
        "Subscribe": "subscribe.html",
    }

    nav_pos = html.find('class="home-trust-strip"')
    latest_pos = html.find('class="section latest"')
    assert nav_pos != -1
    assert latest_pos != -1
    assert nav_pos < latest_pos


def test_footer_trust_links_are_centered_in_css(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)
    html = (out_dir / "index.html").read_text(encoding="utf-8")

    assert ".trust-links" in html
    assert "justify-content: center" in html
    assert "footer .trust-links" in html

    page = soup(out_dir / "index.html")
    footer_nav = page.select_one('footer nav.trust-links[aria-label="Trust and discovery pages"]')
    assert footer_nav is not None

    footer_links = {a.get_text(" ", strip=True): a.get("href") for a in footer_nav.select("a[href]")}
    for label, href in {
        "About": "about.html",
        "Methodology": "methodology.html",
        "Ethics": "ethics.html",
        "Subscribe": "subscribe.html",
        "Archive": "archive.html",
        "RSS": "feed.xml",
    }.items():
        assert footer_links[label] == href


def test_static_pages_keep_centered_footer_links(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    for name in ["about.html", "methodology.html", "ethics.html", "subscribe.html", "404.html"]:
        html = (out_dir / name).read_text(encoding="utf-8")
        assert ".trust-links" in html
        assert "justify-content: center" in html
        assert "footer .trust-links" in html
        page = BeautifulSoup(html, "html.parser")
        assert page.select_one('footer nav.trust-links[aria-label="Trust and discovery pages"]') is not None

