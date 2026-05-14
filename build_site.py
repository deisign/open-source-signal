#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from render_issue import load_issue, output_filename

DEFAULT_SITE_CONFIG = {
    "site_title_en": "Open Source Signal",
    "site_title_uk": "Сигнал відкритих джерел",
    "site_description_en": "A bilingual OSINT editorial radar for investigations, verification, maps, platforms, surveillance and researcher safety.",
    "site_description_uk": "Двомовний OSINT-радар про розслідування, верифікацію, мапи, платформи, інфраструктуру стеження й безпеку дослідника.",
    "base_url": "",
    "telegram_url": "https://t.me/open_source_signal_ua",
    "rss_path": "feed.xml",
    "sitemap_path": "sitemap.xml",
    "robots_path": "robots.txt",
    "analytics_provider": "goatcounter",
    "analytics_id": "",
    "analytics_domain": "",
}


@dataclass(frozen=True)
class BuiltIssue:
    issue: dict[str, Any]
    output_name: str
    href: str


def _make_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _load_config(config_path: Path | None) -> dict[str, Any]:
    config = dict(DEFAULT_SITE_CONFIG)
    if config_path and config_path.exists():
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("Site config must be a JSON object")
        config.update(loaded)
    return config


def _issue_sort_key(issue: dict[str, Any]) -> str:
    return str(issue["date_iso"])


def load_issues(issues_dir: Path) -> list[dict[str, Any]]:
    issue_paths = sorted(issues_dir.glob("*.json"))
    if not issue_paths:
        raise ValueError(f"No issue JSON files found in {issues_dir}")
    issues = [load_issue(path) for path in issue_paths]
    return sorted(issues, key=_issue_sort_key, reverse=True)




def _absolute_url(base_url: str, path: str = "") -> str:
    if not base_url:
        return path
    base = base_url.rstrip("/")
    if not path:
        return base
    return f"{base}/{path.lstrip('/')}"


def _pub_date(issue: dict[str, Any]) -> str:
    dt = datetime.strptime(str(issue["date_iso"]), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return format_datetime(dt)




def _xml_date(issue: dict[str, Any]) -> str:
    return str(issue["date_iso"])


def _issue_meta_description(issue: dict[str, Any]) -> str:
    items = issue.get("items", [])
    fragments: list[str] = []
    for item in items[:3]:
        title = str(item.get("title_en") or item.get("title_uk") or "").strip()
        rubric = str(item.get("rubric_en") or item.get("rubric_uk") or "").strip()
        if title and rubric:
            fragments.append(f"{rubric}: {title}")
        elif title:
            fragments.append(title)
    if fragments:
        return "Ukrainian accountability OSINT digest: " + "; ".join(fragments) + "."
    return str(issue.get("dek_en") or issue.get("dek_uk") or "")


def _json_script(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _issue_json_ld(issue: dict[str, Any], page_url: str, og_image_url: str, config: dict[str, Any]) -> str:
    keywords = sorted({tag for item in issue.get("items", []) for tag in item.get("tags", [])})
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": f"{issue['title_en']} #{issue['issue_number']}",
        "alternativeHeadline": issue["title_uk"],
        "description": _issue_meta_description(issue),
        "datePublished": issue["date_iso"],
        "dateModified": issue["date_iso"],
        "url": page_url,
        "image": [og_image_url] if og_image_url else [],
        "inLanguage": ["en", "uk"],
        "isAccessibleForFree": True,
        "author": {
            "@type": "Organization",
            "name": config["site_title_en"],
            "url": _absolute_url(str(config.get("base_url", ""))),
        },
        "publisher": {
            "@type": "Organization",
            "name": config["site_title_en"],
            "url": _absolute_url(str(config.get("base_url", ""))),
            "logo": {
                "@type": "ImageObject",
                "url": _absolute_url(str(config.get("base_url", "")), "static/logo-mark-512.png"),
            },
        },
        "keywords": keywords,
    }
    return _json_script(data)


def _site_json_ld(config: dict[str, Any]) -> str:
    base_url = _absolute_url(str(config.get("base_url", "")))
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": config["site_title_en"],
        "alternateName": config["site_title_uk"],
        "url": base_url,
        "description": config["site_description_en"],
        "inLanguage": ["en", "uk"],
        "publisher": {
            "@type": "Organization",
            "name": config["site_title_en"],
            "url": base_url,
            "logo": {
                "@type": "ImageObject",
                "url": _absolute_url(str(config.get("base_url", "")), "static/logo-mark-512.png"),
            },
        },
    }
    return _json_script(data)


def _analytics_snippet(config: dict[str, Any]) -> str:
    provider = str(config.get("analytics_provider", "")).strip().lower()
    analytics_id = str(config.get("analytics_id", "")).strip()
    analytics_domain = str(config.get("analytics_domain", "")).strip()

    if provider != "goatcounter" or not analytics_id:
        return ""

    if not analytics_domain:
        analytics_domain = f"{analytics_id}.goatcounter.com"

    analytics_domain = analytics_domain.removeprefix("https://").removeprefix("http://").rstrip("/")
    counter_url = f"https://{analytics_domain}/count"

    return f'<script data-goatcounter="{counter_url}" async src="//gc.zgo.at/count.js"></script>'


def write_sitemap(issues: list[BuiltIssue], out_dir: Path, config: dict[str, Any]) -> Path:
    base_url = str(config.get("base_url", "")).strip()
    urls: list[tuple[str, str, str]] = [
        (_absolute_url(base_url), "", "daily"),
        (_absolute_url(base_url, "archive.html"), "", "weekly"),
        (_absolute_url(base_url, str(config.get("rss_path", "feed.xml"))), "", "daily"),
    ]
    for built in issues:
        urls.append((_absolute_url(base_url, built.href), _xml_date(built.issue), "weekly"))

    entries = []
    for loc, lastmod, changefreq in urls:
        lastmod_line = f"\n    <lastmod>{escape(lastmod)}</lastmod>" if lastmod else ""
        entries.append(
            f"  <url>\n    <loc>{escape(loc)}</loc>{lastmod_line}\n    <changefreq>{escape(changefreq)}</changefreq>\n  </url>"
        )

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</urlset>
"""
    path = out_dir / str(config.get("sitemap_path", "sitemap.xml"))
    path.write_text(sitemap, encoding="utf-8")
    return path


def write_robots(out_dir: Path, config: dict[str, Any]) -> Path:
    base_url = str(config.get("base_url", "")).rstrip("/")
    sitemap_url = _absolute_url(base_url, str(config.get("sitemap_path", "sitemap.xml")))
    body = f"""User-agent: *
Allow: /

Sitemap: {sitemap_url}
"""
    path = out_dir / str(config.get("robots_path", "robots.txt"))
    path.write_text(body, encoding="utf-8")
    return path


def write_feed(issues: list[BuiltIssue], out_dir: Path, config: dict[str, Any]) -> Path:
    items_xml: list[str] = []
    base_url = str(config.get("base_url", ""))
    for built in issues:
        issue = built.issue
        link = _absolute_url(base_url, built.href)
        description = escape((issue.get("dek_en") or issue.get("dek_uk") or config.get("site_description_en", "")).strip())
        title = escape(f"{issue['title_en']} / {issue['title_uk']} #{issue['issue_number']}")
        item_xml = f"""    <item>
      <title>{title}</title>
      <link>{escape(link)}</link>
      <guid>{escape(link)}</guid>
      <pubDate>{_pub_date(issue)}</pubDate>
      <description>{description}</description>
    </item>"""
        items_xml.append(item_xml)

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{escape(config['site_title_en'] + " / " + config['site_title_uk'])}</title>
    <link>{escape(_absolute_url(base_url))}</link>
    <description>{escape(config['site_description_en'])}</description>
    <language>en</language>
    <lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    path = out_dir / str(config.get('rss_path', 'feed.xml'))
    path.write_text(feed, encoding='utf-8')
    return path


def copy_cname(cname_path: Path, out_dir: Path) -> list[Path]:
    if not cname_path.exists():
        return []
    target = out_dir / "CNAME"
    target.write_text(cname_path.read_text(encoding="utf-8").strip() + "\n", encoding="utf-8")
    return [target]

def copy_static(static_dir: Path, out_dir: Path) -> list[Path]:
    written: list[Path] = []
    if not static_dir.exists():
        return written
    out_static = out_dir / "static"
    out_static.mkdir(parents=True, exist_ok=True)
    for path in static_dir.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(static_dir)
        target = out_static / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        written.append(target)
    return written


def build_site(issues_dir: Path, templates_dir: Path, out_dir: Path, config_path: Path | None = None, static_dir: Path | None = None) -> list[Path]:
    config = _load_config(config_path)
    issues = load_issues(issues_dir)
    env = _make_env(templates_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    issue_out_dir = out_dir / "issues"
    issue_out_dir.mkdir(parents=True, exist_ok=True)

    built_issues: list[BuiltIssue] = []
    written: list[Path] = []

    issue_template = env.get_template("issue.html.j2")
    og_image_url = _absolute_url(str(config.get("base_url", "")), "static/og-image.png")
    analytics_snippet = _analytics_snippet(config)
    for issue in issues:
        name = output_filename(issue)
        href = f"issues/{name}"
        page_url = _absolute_url(str(config.get("base_url", "")), href)
        meta_description = _issue_meta_description(issue)
        issue_schema_json = _issue_json_ld(issue, page_url, og_image_url, config)
        path = issue_out_dir / name
        path.write_text(
            issue_template.render(
                issue=issue,
                config=config,
                asset_prefix="../",
                page_url=page_url,
                og_image_url=og_image_url,
                meta_description=meta_description,
                issue_schema_json=issue_schema_json,
                analytics_snippet=analytics_snippet,
            ),
            encoding="utf-8",
        )
        built_issues.append(BuiltIssue(issue=issue, output_name=name, href=href))
        written.append(path)

    context = {
        "config": config,
        "issues": built_issues,
        "latest": built_issues[0],
        "latest_items": built_issues[0].issue["items"][:4],
        "feed_href": str(config.get("rss_path", "feed.xml")),
        "og_image_url": _absolute_url(str(config.get("base_url", "")), "static/og-image.png"),
        "site_schema_json": _site_json_ld(config),
        "analytics_snippet": analytics_snippet,
    }

    pages = [
        ("index.html.j2", "index.html"),
        ("archive.html.j2", "archive.html"),
    ]
    for template_name, output_name in pages:
        template = env.get_template(template_name)
        path = out_dir / output_name
        page_url = _absolute_url(str(config.get("base_url", "")), output_name if output_name != "index.html" else "")
        path.write_text(template.render(asset_prefix="", page_url=page_url, **context), encoding="utf-8")
        written.append(path)

    written.append(write_feed(built_issues, out_dir, config))
    written.append(write_sitemap(built_issues, out_dir, config))
    written.append(write_robots(out_dir, config))

    written.extend(copy_cname(Path("CNAME"), out_dir))

    if static_dir is not None:
        written.extend(copy_static(static_dir, out_dir))

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Open Source Signal static site.")
    parser.add_argument("--issues", type=Path, default=Path("issues"), help="Directory with issue JSON files")
    parser.add_argument("--templates", type=Path, default=Path("templates"), help="Directory with Jinja templates")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output site directory")
    parser.add_argument("--config", type=Path, default=Path("site.json"), help="Optional site config JSON")
    parser.add_argument("--static", type=Path, default=Path("static"), help="Static assets directory")
    args = parser.parse_args()

    config_path = args.config if args.config.exists() else None
    static_dir = args.static if args.static.exists() else None
    written = build_site(args.issues, args.templates, args.out, config_path, static_dir)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
