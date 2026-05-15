import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def latest_issue_href() -> str:
    issue_paths = sorted(ROOT.glob("issues/*.json"))
    latest = max(issue_paths, key=lambda path: json.loads(path.read_text(encoding="utf-8"))["date_iso"])
    date_iso = json.loads(latest.read_text(encoding="utf-8"))["date_iso"]
    return f"issues/open-source-signal-{date_iso}.html"

def latest_issue_file() -> Path:
    href = latest_issue_href().split("/", 1)[1]
    return Path("issues") / href


def test_build_site_creates_home_archive_and_issue(tmp_path):
    out_dir = tmp_path / "dist"
    result = subprocess.run(
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
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert (out_dir / "index.html").exists()
    assert (out_dir / "archive.html").exists()
    assert (out_dir / "issues" / "open-source-signal-2026-05-13.html").exists()
    assert (out_dir / latest_issue_file()).exists()
    assert "index.html" in result.stdout
    assert "archive.html" in result.stdout


def test_homepage_links_to_latest_issue_and_archive(tmp_path):
    out_dir = tmp_path / "dist"
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
        ],
        check=True,
    )
    soup = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    links = {a.get("href") for a in soup.select("a[href]")}
    assert latest_issue_href() in links
    assert "archive.html" in links
    assert soup.find(string="Сигнал відкритих джерел") is not None
    assert soup.select(".mini-signal")


def test_archive_lists_available_issues(tmp_path):
    out_dir = tmp_path / "dist"
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
        ],
        check=True,
    )
    soup = BeautifulSoup((out_dir / "archive.html").read_text(encoding="utf-8"), "html.parser")
    rows = soup.select(".issue-row")
    assert len(rows) >= 2
    archive_text = " ".join(row.get_text(" ", strip=True) for row in rows)
    assert "14 May 2026" in archive_text
    assert "13 May 2026" in archive_text
    assert rows[0].select_one(f"a[href='{latest_issue_href()}']") is not None


def test_build_site_copies_static_assets_and_links_favicon(tmp_path):
    out_dir = tmp_path / "dist"
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
    )
    assert (out_dir / "static" / "logo-mark.png").exists()
    assert (out_dir / "static" / "favicon.ico").exists()
    assert (out_dir / "static" / "apple-touch-icon.png").exists()
    assert (out_dir / "static" / "site.webmanifest").exists()
    assert (out_dir / "static" / "og-image.png").exists()

    home = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    issue = BeautifulSoup((out_dir / latest_issue_file()).read_text(encoding="utf-8"), "html.parser")

    assert home.find("link", rel="icon")["href"] == "static/logo-mark.png"
    assert issue.find("link", rel="icon")["href"] == "../static/logo-mark.png"
    assert home.find("img", {"class": "brand-mark"}) is not None


def test_build_site_generates_rss_and_social_metadata(tmp_path):
    out_dir = tmp_path / "dist"
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
    )
    feed = (out_dir / "feed.xml").read_text(encoding="utf-8")
    assert "<rss version=\"2.0\">" in feed
    assert latest_issue_href().split("/", 1)[1] in feed

    home = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    issue = BeautifulSoup((out_dir / latest_issue_file()).read_text(encoding="utf-8"), "html.parser")

    assert home.find("meta", attrs={"property": "og:title"}) is not None
    assert issue.find("meta", attrs={"property": "og:type"})["content"] == "article"
    assert home.find("link", attrs={"rel": "alternate", "type": "application/rss+xml"})["href"] == "feed.xml"
    links = {a.get("href") for a in home.select("a[href]")}
    assert "https://t.me/open_source_signal_ua" in links


def test_custom_domain_config_is_used_in_built_site(tmp_path):
    out_dir = tmp_path / "dist"
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

    assert (out_dir / "CNAME").read_text(encoding="utf-8") == "osintsignal.org\n"
    feed = (out_dir / "feed.xml").read_text(encoding="utf-8")
    assert f"https://osintsignal.org/{latest_issue_href()}" in feed

    home = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert home.find("link", rel="canonical")["href"] == "https://osintsignal.org"
    assert home.find("meta", attrs={"property": "og:image"})["content"] == "https://osintsignal.org/static/og-image.png"
