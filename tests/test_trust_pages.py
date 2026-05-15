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


def read_soup(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def test_trust_pages_are_generated_with_contact(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    for name in ["about.html", "methodology.html", "ethics.html", "subscribe.html", "404.html"]:
        assert (out_dir / name).exists()

    assert (out_dir / "contact.html").exists()


def test_trust_pages_have_seo_metadata_and_goatcounter_once(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    for name in ["about.html", "methodology.html", "ethics.html", "subscribe.html"]:
        html = (out_dir / name).read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        assert soup.find("link", rel="canonical")["href"] == f"https://osintsignal.org/{name}"
        assert soup.find("meta", attrs={"property": "og:title"}) is not None
        assert soup.find("meta", attrs={"property": "og:description"}) is not None
        assert soup.find("script", attrs={"data-goatcounter": "https://deisign.goatcounter.com/count"}) is not None
        assert html.count("gc.zgo.at/count.js") == 1


def test_sitemap_includes_trust_pages_and_contact_but_excludes_404(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    sitemap = (out_dir / "sitemap.xml").read_text(encoding="utf-8")

    assert "about.html" in sitemap
    assert "methodology.html" in sitemap
    assert "ethics.html" in sitemap
    assert "contact.html" in sitemap
    assert "subscribe.html" in sitemap
    assert "404.html" not in sitemap

def test_footer_links_to_trust_pages_from_home_archive_issue_and_static_pages(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    pages = [
        out_dir / "index.html",
        out_dir / "archive.html",
        out_dir / "issues" / "open-source-signal-2026-05-14.html",
        out_dir / "about.html",
        out_dir / "methodology.html",
        out_dir / "ethics.html",
        out_dir / "subscribe.html",
    ]

    for path in pages:
        soup = read_soup(path)
        links = {a.get("href") for a in soup.select("a[href]")}
        prefix = "../" if path.parent.name == "issues" else ""
        assert f"{prefix}about.html" in links
        assert f"{prefix}methodology.html" in links
        assert f"{prefix}ethics.html" in links
        assert f"{prefix}subscribe.html" in links


def test_404_is_noindex_and_not_a_contact_placeholder(tmp_path):
    out_dir = tmp_path / "dist"
    build_site_into(out_dir)

    soup = read_soup(out_dir / "404.html")
    assert soup.find("meta", attrs={"name": "robots"})["content"] == "noindex"
    text = soup.get_text(" ", strip=True)
    assert "Signal lost" in text
    assert "editor@osintsignal.org" not in text
    assert "tips@osintsignal.org" not in text
