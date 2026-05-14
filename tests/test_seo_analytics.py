import json
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def build(tmp_path, extra_config=None):
    out_dir = tmp_path / "dist"
    config_path = ROOT / "site.json"
    if extra_config is not None:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        data.update(extra_config)
        config_path = tmp_path / "site.json"
        config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
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
            str(config_path),
            "--static",
            str(ROOT / "static"),
        ],
        check=True,
        cwd=ROOT,
    )
    return out_dir


def test_sitemap_and_robots_are_generated(tmp_path):
    out_dir = build(tmp_path)

    sitemap = out_dir / "sitemap.xml"
    robots = out_dir / "robots.txt"

    assert sitemap.exists()
    assert robots.exists()

    xml = ET.fromstring(sitemap.read_text(encoding="utf-8"))
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [loc.text for loc in xml.findall(".//sm:loc", ns)]

    assert "https://osintsignal.org" in locs
    assert "https://osintsignal.org/archive.html" in locs
    assert "https://osintsignal.org/feed.xml" in locs
    assert "https://osintsignal.org/issues/open-source-signal-2026-05-14.html" in locs

    robots_text = robots.read_text(encoding="utf-8")
    assert "User-agent: *" in robots_text
    assert "Allow: /" in robots_text
    assert "Sitemap: https://osintsignal.org/sitemap.xml" in robots_text


def test_issue_page_contains_json_ld_news_article(tmp_path):
    out_dir = build(tmp_path)
    issue_html = out_dir / "issues" / "open-source-signal-2026-05-14.html"
    soup = BeautifulSoup(issue_html.read_text(encoding="utf-8"), "html.parser")

    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    assert scripts

    data = json.loads(scripts[0].string)
    assert data["@type"] == "NewsArticle"
    assert data["url"] == "https://osintsignal.org/issues/open-source-signal-2026-05-14.html"
    assert data["publisher"]["name"] == "Open Source Signal"
    assert data["inLanguage"] == ["en", "uk"]


def test_analytics_not_inserted_without_id(tmp_path):
    out_dir = build(
        tmp_path,
        {
            "analytics_provider": "goatcounter",
            "analytics_id": "",
            "analytics_domain": "",
        },
    )
    home = (out_dir / "index.html").read_text(encoding="utf-8")
    assert "gc.zgo.at/count.js" not in home
    assert "data-goatcounter" not in home


def test_goatcounter_snippet_is_inserted_when_configured(tmp_path):
    out_dir = build(
        tmp_path,
        {
            "analytics_provider": "goatcounter",
            "analytics_id": "osintsignal",
            "analytics_domain": "",
        },
    )
    home = (out_dir / "index.html").read_text(encoding="utf-8")
    issue = (out_dir / "issues" / "open-source-signal-2026-05-14.html").read_text(encoding="utf-8")
    assert 'data-goatcounter="https://osintsignal.goatcounter.com/count"' in home
    assert 'src="//gc.zgo.at/count.js"' in home
    assert 'data-goatcounter="https://osintsignal.goatcounter.com/count"' in issue


def test_issue_meta_description_uses_digest_topics(tmp_path):
    out_dir = build(tmp_path)
    soup = BeautifulSoup(
        (out_dir / "issues" / "open-source-signal-2026-05-14.html").read_text(encoding="utf-8"),
        "html.parser",
    )
    description = soup.find("meta", attrs={"name": "description"})["content"]
    assert description.startswith("Ukrainian accountability OSINT digest:")
    assert "Signal One" in description or "Головний сигнал" in description
