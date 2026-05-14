import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


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
    assert (out_dir / "issues" / "open-source-signal-2026-05-14.html").exists()
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
    assert "issues/open-source-signal-2026-05-14.html" in links
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
    assert rows[0].select_one("a[href='issues/open-source-signal-2026-05-14.html']") is not None


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
    assert (out_dir / "static" / "favicon.svg").exists()
    assert (out_dir / "static" / "favicon.ico").exists()
    assert (out_dir / "static" / "apple-touch-icon.png").exists()
    assert (out_dir / "static" / "site.webmanifest").exists()

    home = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    issue = BeautifulSoup((out_dir / "issues" / "open-source-signal-2026-05-14.html").read_text(encoding="utf-8"), "html.parser")

    assert home.find("link", rel="icon")["href"] == "static/favicon.svg"
    assert issue.find("link", rel="icon")["href"] == "../static/favicon.svg"
