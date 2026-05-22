#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, select_autoescape

from render_weekly import analytics_snippet, render_weekly
from static_pages import TRUST_NAV_LINKS


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_config(config_path: Path | None) -> dict[str, Any]:
    config = {
        "site_title_en": "Open Source Signal",
        "site_title_uk": "Сигнал відкритих джерел",
        "site_description_en": "A bilingual OSINT editorial radar for investigations, verification, maps, platforms, surveillance and researcher safety.",
        "base_url": "",
        "telegram_url": "https://t.me/open_source_signal_ua",
        "sitemap_path": "sitemap.xml",
    }
    if config_path and config_path.exists():
        config.update(load_json(config_path))
    return config


def absolute_url(base_url: str, path: str = "") -> str:
    if not base_url:
        return path
    base = base_url.rstrip("/")
    if not path:
        return base
    return f"{base}/{path.lstrip('/')}"


def make_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def weekly_sort_key(weekly: dict[str, Any]) -> str:
    return str(weekly.get("date_iso") or weekly.get("iso_week") or weekly.get("issue_number") or "")


def load_weekly_issues(weekly_dir: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for path in sorted(weekly_dir.glob("*.json")):
        weekly = load_json(path)
        weekly.setdefault("source_path", str(path))
        weekly.setdefault("output_name", f"{weekly['slug']}.html")
        weekly.setdefault("href", f"weekly/{weekly['output_name']}")
        issues.append(weekly)
    return sorted(issues, key=weekly_sort_key, reverse=True)


def render_weekly_pages(weekly_issues: list[dict[str, Any]], templates_dir: Path, out_dir: Path, config_path: Path | None) -> list[Path]:
    written: list[Path] = []
    weekly_out_dir = out_dir / "weekly"
    weekly_out_dir.mkdir(parents=True, exist_ok=True)
    for weekly in weekly_issues:
        source_path = Path(str(weekly["source_path"]))
        written.append(render_weekly(source_path, templates_dir, weekly_out_dir, config_path))
    return written


def render_weekly_index(weekly_issues: list[dict[str, Any]], templates_dir: Path, out_dir: Path, config: dict[str, Any]) -> Path:
    env = make_env(templates_dir)
    template = env.get_template("weekly_index.html.j2")
    weekly_dir = out_dir / "weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    path = weekly_dir / "index.html"
    path.write_text(
        template.render(
            config=config,
            weekly_issues=weekly_issues,
            latest=weekly_issues[0] if weekly_issues else None,
            page_url=absolute_url(str(config.get("base_url", "")), "weekly/"),
            asset_prefix="../",
            trust_nav_links=TRUST_NAV_LINKS,
            analytics_snippet=analytics_snippet(config),
            og_image_url=absolute_url(str(config.get("base_url", "")), "static/og-image.png"),
        ),
        encoding="utf-8",
    )
    return path


def weekly_home_block(latest: dict[str, Any]) -> str:
    href = f"weekly/{latest['output_name']}"
    return f'''
<!-- weekly-magazine-block:start -->
<section class="weekly-home-card" aria-labelledby="weekly-home-title">
  <div class="weekly-home-eyebrow">Weekly Magazine</div>
  <h2 id="weekly-home-title">Open Source Signal Weekly</h2>
  <p>Sunday editorial synthesis of the strongest OSINT signals of the week: Ukrainian accountability, verification, tools, datasets, tradecraft, and source-risk notes.</p>
  <div class="weekly-home-actions">
    <a href="{href}">Read latest weekly</a>
    <a href="weekly/">Weekly archive</a>
  </div>
</section>
<!-- weekly-magazine-block:end -->
'''


def weekly_archive_block(latest: dict[str, Any]) -> str:
    href = f"weekly/{latest['output_name']}"
    return f'''
<!-- weekly-archive-block:start -->
<section class="weekly-archive-card" aria-labelledby="weekly-archive-title">
  <h2 id="weekly-archive-title">Weekly Magazine</h2>
  <p>Sunday editorial synthesis, separate from the Daily Signal stream.</p>
  <p><a href="{href}">Latest weekly: {latest.get('issue_number', '')} · {latest.get('week_label_en', '')}</a></p>
  <p><a href="weekly/">All weekly issues →</a></p>
</section>
<!-- weekly-archive-block:end -->
'''


def weekly_css() -> str:
    return '''
.weekly-home-card,
.weekly-archive-card {
  width: min(980px, 100%);
  margin: 28px auto;
  padding: 24px;
  border: 1px solid var(--line, rgba(20,20,20,.16));
  border-radius: 28px;
  background: rgba(255,249,234,.72);
  box-shadow: 0 14px 42px rgba(20,20,20,.08);
  text-align: center;
}
.weekly-home-eyebrow {
  display: inline-flex;
  margin-bottom: 10px;
  color: var(--muted, #6d665a);
  font-family: var(--label-font, Arimo, Arial, sans-serif);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.weekly-home-card h2,
.weekly-archive-card h2 {
  margin: 0 0 10px;
}
.weekly-home-card p,
.weekly-archive-card p {
  max-width: 720px;
  margin: 8px auto;
}
.weekly-home-actions {
  display: flex;
  justify-content: center;
  gap: 10px 14px;
  flex-wrap: wrap;
  margin-top: 18px;
}
.weekly-home-actions a,
.weekly-archive-card a {
  font-weight: 800;
  text-underline-offset: .22em;
}
'''


def inject_css(html: str) -> str:
    if "weekly-home-card" in html and "weekly-home-eyebrow" in html:
        return html
    css = weekly_css()
    if "</style>" in html:
        return html.replace("</style>", css + "\n</style>", 1)
    if "</head>" in html:
        return html.replace("</head>", f"<style>\n{css}\n</style>\n</head>", 1)
    return html


def replace_marker_block(html: str, start_marker: str, end_marker: str, block: str) -> str:
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.S)
    if pattern.search(html):
        return pattern.sub(block.strip(), html)
    return html


def insert_before_latest_section(html: str, block: str) -> str:
    html = replace_marker_block(html, "<!-- weekly-magazine-block:start -->", "<!-- weekly-magazine-block:end -->", block)
    if "<!-- weekly-magazine-block:start -->" in html:
        return html
    needle = "Latest issue / останній випуск"
    pos = html.find(needle)
    if pos != -1:
        section_pos = html.rfind("<section", 0, pos)
        if section_pos != -1:
            return html[:section_pos] + block + html[section_pos:]
        return html[:pos] + block + html[pos:]
    main_end = html.find("</main>")
    if main_end != -1:
        return html[:main_end] + block + html[main_end:]
    body_end = html.find("</body>")
    if body_end != -1:
        return html[:body_end] + block + html[body_end:]
    return html + block


def insert_archive_block(html: str, block: str) -> str:
    html = replace_marker_block(html, "<!-- weekly-archive-block:start -->", "<!-- weekly-archive-block:end -->", block)
    if "<!-- weekly-archive-block:start -->" in html:
        return html
    footer_pos = html.find("<footer")
    if footer_pos != -1:
        return html[:footer_pos] + block + html[footer_pos:]
    body_end = html.find("</body>")
    if body_end != -1:
        return html[:body_end] + block + html[body_end:]
    return html + block


def patch_home_and_archive(out_dir: Path, latest: dict[str, Any]) -> list[Path]:
    written: list[Path] = []
    index_path = out_dir / "index.html"
    if index_path.exists():
        html = inject_css(index_path.read_text(encoding="utf-8"))
        html = insert_before_latest_section(html, weekly_home_block(latest))
        html = html.replace('href="archive.html">Archive</a>', 'href="weekly/">Weekly</a> <a href="archive.html">Archive</a>')
        index_path.write_text(html, encoding="utf-8")
        written.append(index_path)

    archive_path = out_dir / "archive.html"
    if archive_path.exists():
        html = inject_css(archive_path.read_text(encoding="utf-8"))
        html = insert_archive_block(html, weekly_archive_block(latest))
        archive_path.write_text(html, encoding="utf-8")
        written.append(archive_path)
    return written


def update_sitemap(out_dir: Path, config: dict[str, Any], weekly_issues: list[dict[str, Any]]) -> Path:
    sitemap_path = out_dir / str(config.get("sitemap_path", "sitemap.xml"))
    sitemap = sitemap_path.read_text(encoding="utf-8")
    base_url = str(config.get("base_url", "")).strip()
    sitemap = re.sub(r"\s*<url>\s*<loc>[^<]*/weekly/?</loc>.*?</url>", "", sitemap, flags=re.S)
    sitemap = re.sub(r"\s*<url>\s*<loc>[^<]*/weekly/[^<]+\.html</loc>.*?</url>", "", sitemap, flags=re.S)

    entries: list[str] = []
    entries.append(
        "  <url>\n"
        f"    <loc>{escape(absolute_url(base_url, 'weekly/'))}</loc>\n"
        "    <changefreq>weekly</changefreq>\n"
        "  </url>"
    )
    for weekly in weekly_issues:
        href = f"weekly/{weekly['output_name']}"
        lastmod = str(weekly.get("date_iso") or "")
        lastmod_line = f"\n    <lastmod>{escape(lastmod)}</lastmod>" if lastmod else ""
        entries.append(
            "  <url>\n"
            f"    <loc>{escape(absolute_url(base_url, href))}</loc>"
            f"{lastmod_line}\n"
            "    <changefreq>weekly</changefreq>\n"
            "  </url>"
        )
    insert = "\n" + "\n".join(entries) + "\n"
    if "</urlset>" in sitemap:
        sitemap = sitemap.replace("</urlset>", insert + "</urlset>", 1)
    else:
        sitemap += insert
    sitemap_path.write_text(sitemap, encoding="utf-8")
    return sitemap_path


def build_weekly_site(weekly_dir: Path, templates_dir: Path, out_dir: Path, config_path: Path | None) -> list[Path]:
    config = load_config(config_path)
    weekly_issues = load_weekly_issues(weekly_dir)
    if not weekly_issues:
        return []
    written = render_weekly_pages(weekly_issues, templates_dir, out_dir, config_path)
    written.append(render_weekly_index(weekly_issues, templates_dir, out_dir, config))
    written.extend(patch_home_and_archive(out_dir, weekly_issues[0]))
    written.append(update_sitemap(out_dir, config, weekly_issues))
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Open Source Signal Weekly section after build_site.py.")
    parser.add_argument("--weekly", type=Path, default=Path("weekly"), help="Directory with weekly JSON files")
    parser.add_argument("--templates", type=Path, default=Path("templates"), help="Directory with Jinja templates")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Built site output directory")
    parser.add_argument("--config", type=Path, default=Path("site.json"), help="Site config JSON")
    args = parser.parse_args()
    config_path = args.config if args.config.exists() else None
    for path in build_weekly_site(args.weekly, args.templates, args.out, config_path):
        print(path)


if __name__ == "__main__":
    main()
