from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def load_weekly_issues() -> list[dict[str, Any]]:
    weekly_issues: list[dict[str, Any]] = []
    for path in sorted((ROOT / "weekly").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise AssertionError(f"{path} must contain a JSON object")
        weekly_issues.append(data)

    return sorted(
        weekly_issues,
        key=lambda weekly: str(
            weekly.get("date_iso")
            or weekly.get("iso_week")
            or weekly.get("issue_number")
            or ""
        ),
        reverse=True,
    )


def weekly_output_name(weekly: dict[str, Any]) -> str:
    output_name = weekly.get("output_name")
    if output_name:
        return str(output_name)
    return f"{weekly['slug']}.html"


def weekly_href(weekly: dict[str, Any]) -> str:
    return f"weekly/{weekly_output_name(weekly)}"


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


def test_weekly_section_builds_index_issue_archive_and_sitemap(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_full_site(out_dir)

    weekly_issues = load_weekly_issues()
    assert weekly_issues

    latest_weekly = weekly_issues[0]
    latest_output_name = weekly_output_name(latest_weekly)
    latest_href = weekly_href(latest_weekly)

    weekly_index = out_dir / "weekly" / "index.html"
    weekly_issue = out_dir / "weekly" / latest_output_name

    assert weekly_index.exists()
    assert weekly_issue.exists()

    for weekly in weekly_issues:
        assert (out_dir / "weekly" / weekly_output_name(weekly)).exists()

    index_html = weekly_index.read_text(encoding="utf-8")
    assert "Open Source Signal Weekly" in index_html
    assert latest_output_name in index_html
    assert "logo-mark.png" in index_html

    home = BeautifulSoup((out_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
    home_links = {a.get("href") for a in home.select("a[href]")}
    home_text = home.get_text(" ")

    assert "archive.html" in home_links
    assert "weekly/" in home_links
    assert latest_href in home_links
    assert "Daily archive" in home_text
    assert "Weekly archive" in home_text

    weekly_card = home.select_one(".weekly-home-card")
    assert weekly_card is not None
    assert latest_output_name in str(weekly_card)
    assert "Weekly Magazine" in home_text

    archive = BeautifulSoup((out_dir / "archive.html").read_text(encoding="utf-8"), "html.parser")
    archive_links = {a.get("href") for a in archive.select("a[href]")}
    assert "weekly/" in archive_links
    assert latest_href in archive_links

    sitemap = (out_dir / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://osintsignal.org/weekly/" in sitemap
    assert f"https://osintsignal.org/{latest_href}" in sitemap
    assert "https://osintsignal.org/404.html" not in sitemap


def test_homepage_uses_daily_and_weekly_archive_labels(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_full_site(out_dir)

    html = (out_dir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    links = {a.get_text(" ", strip=True): a.get("href") for a in soup.select("a[href]")}

    assert links.get("Daily archive") == "archive.html"
    assert links.get("Weekly archive") == "weekly/"
    assert links.get("Weekly") != "weekly/"

    weekly_issues = load_weekly_issues()
    assert weekly_href(weekly_issues[0]) in set(links.values())
    assert "weekly/" in set(links.values())


def test_pages_workflow_builds_weekly_after_static_site() -> None:
    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "python build_weekly_site.py --weekly weekly --templates templates --out dist --config site.json" in workflow


def test_weekly_public_page_does_not_render_internal_editorial_notes(tmp_path: Path) -> None:
    out_dir = tmp_path / "dist"
    build_full_site(out_dir)

    latest_weekly = load_weekly_issues()[0]
    html = (out_dir / "weekly" / weekly_output_name(latest_weekly)).read_text(encoding="utf-8")

    assert "Editorial use:" not in html
    assert "Lead section; useful as" not in html

    for weekly in load_weekly_issues():
        assert "internal_notes" not in weekly
        assert "internal_editorial_notes" not in weekly
        for item in weekly.get("items", []):
            assert "editorial_use" not in item
