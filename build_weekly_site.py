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
    config: dict[str, Any] = {
        "site_title_en": "Open Source Signal",
        "site_title_uk": "Сигнал відкритих джерел",
        "site_description_en": (
            "A bilingual OSINT editorial radar for investigations, verification, "
            "maps, platforms, surveillance and researcher safety."
        ),
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


def render_weekly_pages(
    weekly_issues: list[dict[str, Any]],
    templates_dir: Path,
    out_dir: Path,
    config_path: Path | None,
) -> list[Path]:
    written: list[Path] = []
    weekly_out_dir = out_dir / "weekly"
    weekly_out_dir.mkdir(parents=True, exist_ok=True)
    for weekly in weekly_issues:
        source_path = Path(str(weekly["source_path"]))
        written.append(render_weekly(source_path, templates_dir, weekly_out_dir, config_path))
    return written


def render_weekly_index(
    weekly_issues: list[dict[str, Any]],
    templates_dir: Path,
    out_dir: Path,
    config: dict[str, Any],
) -> Path:
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


def ensure_home_weekly_nav(out_dir: Path) -> Path | None:
    """Homepage should expose two archives, not a large Weekly promo block."""
    index_path = out_dir / "index.html"
    if not index_path.exists():
        return None

    html = index_path.read_text(encoding="utf-8")

    html = re.sub(r"\s*<!-- WEEKLY_HOME_START -->[\s\S]*?<!-- WEEKLY_HOME_END -->\s*", "\n", html, flags=re.I)
    html = re.sub(r"\s*<section[^>]*class=\"[^\"]*weekly-home-card[^\"]*\"[\s\S]*?</section>\s*", "\n", html, flags=re.I)
    html = re.sub(r"\s*<div[^>]*class=\"[^\"]*weekly-home-card[^\"]*\"[\s\S]*?</div>\s*", "\n", html, flags=re.I)
    html = re.sub(r"\s*<a[^>]+href=\"weekly/open-source-signal-weekly-[^\"]+\.html\"[^>]*>[\s\S]*?</a>\s*", " ", html, flags=re.I)

    html = re.sub(r"\s*<a([^>]+)href=\"weekly/\"([^>]*)>\s*Weekly\s*</a>\s*", " ", html, count=1, flags=re.I)

    html = re.sub(
        r"(<a[^>]+href=\"archive\.html\"[^>]*>)\s*Archive\s*(</a>)",
        r"\1Daily archive\2",
        html,
        count=1,
        flags=re.I,
    )

    if 'href="weekly/"' not in html:
        html = re.sub(
            r"(<a[^>]+href=\"archive\.html\"[^>]*>Daily archive</a>)",
            r'\1 <a class="button secondary" href="weekly/">Weekly archive</a>',
            html,
            count=1,
            flags=re.I,
        )

    html = re.sub(r"\n{3,}", "\n\n", html)
    index_path.write_text(html, encoding="utf-8")
    return index_path


def weekly_archive_block(latest: dict[str, Any]) -> str:
    issue_number = latest.get("issue_number", "")
    week_label = latest.get("week_label_en", "")
    output_name = latest["output_name"]
    return f"""
<section class="weekly-archive-card" aria-label="Weekly Magazine">
  <p class="weekly-home-eyebrow">Weekly Magazine</p>
  <h2>Open Source Signal Weekly</h2>
  <p>Sunday editorial synthesis, separate from the Daily Signal stream.</p>
  <p class="weekly-home-actions">
    <a href="weekly/{output_name}">Latest weekly: {escape(str(issue_number))} · {escape(str(week_label))}</a>
    <a href="weekly/">All weekly issues →</a>
  </p>
</section>
"""


def weekly_archive_css() -> str:
    return """
.weekly-archive-card {
  width: min(980px, 100%);
  margin: 28px auto;
  padding: 22px;
  border: 1px solid var(--line, rgba(20,20,20,.16));
  border-radius: 24px;
  background: rgba(255,249,234,.58);
  text-align: center;
}
.weekly-home-eyebrow {
  display: inline-flex;
  margin: 0 0 10px;
  color: var(--muted, #6d665a);
  font-family: var(--label-font, Arimo, Arial, sans-serif);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.weekly-home-actions {
  display: flex;
  justify-content: center;
  gap: 10px 14px;
  flex-wrap: wrap;
  margin-top: 16px;
}
.weekly-home-actions a {
  font-weight: 800;
  text-underline-offset: .22em;
}
"""


def inject_archive_css(html: str) -> str:
    if ".weekly-archive-card" in html:
        return html
    css = weekly_archive_css()
    if "</style>" in html:
        return html.replace("</style>", css + "\n</style>", 1)
    if "</head>" in html:
        return html.replace("</head>", f"<style>{css}</style>\n</head>", 1)
    return html


def replace_marker_block(html: str, start_marker: str, end_marker: str, block: str) -> str:
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.S)
    if pattern.search(html):
        return pattern.sub(block.strip(), html)
    return html


def patch_archive(out_dir: Path, latest: dict[str, Any]) -> Path | None:
    archive_path = out_dir / "archive.html"
    if not archive_path.exists():
        return None

    block = (
        "\n<!-- WEEKLY_ARCHIVE_START -->\n"
        + weekly_archive_block(latest).strip()
        + "\n<!-- WEEKLY_ARCHIVE_END -->\n"
    )

    html = archive_path.read_text(encoding="utf-8")
    html = inject_archive_css(html)
    html = replace_marker_block(html, "<!-- WEEKLY_ARCHIVE_START -->", "<!-- WEEKLY_ARCHIVE_END -->", block)

    if "<!-- WEEKLY_ARCHIVE_START -->" not in html:
        if "</main>" in html:
            html = html.replace("</main>", block + "\n</main>", 1)
        elif "</body>" in html:
            html = html.replace("</body>", block + "\n</body>", 1)
        else:
            html += block

    archive_path.write_text(html, encoding="utf-8")
    return archive_path


def remove_old_weekly_entries_from_sitemap(sitemap: str) -> str:
    sitemap = re.sub(r"\s*<url>\s*<loc>[^<]*/weekly/?</loc>[\s\S]*?</url>", "", sitemap)
    sitemap = re.sub(r"\s*<url>\s*<loc>[^<]*/weekly/[^<]+\.html</loc>[\s\S]*?</url>", "", sitemap)
    return sitemap


def update_sitemap(out_dir: Path, config: dict[str, Any], weekly_issues: list[dict[str, Any]]) -> Path:
    sitemap_path = out_dir / str(config.get("sitemap_path", "sitemap.xml"))
    sitemap = sitemap_path.read_text(encoding="utf-8")
    base_url = str(config.get("base_url", "")).strip()

    sitemap = remove_old_weekly_entries_from_sitemap(sitemap)

    entries: list[str] = [
        "  <url>\n"
        f"    <loc>{escape(absolute_url(base_url, 'weekly/'))}</loc>\n"
        "    <changefreq>weekly</changefreq>\n"
        "  </url>"
    ]

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


def build_weekly_site(
    weekly_dir: Path,
    templates_dir: Path,
    out_dir: Path,
    config_path: Path | None,
) -> list[Path]:
    config = load_config(config_path)
    weekly_issues = load_weekly_issues(weekly_dir)
    if not weekly_issues:
        return []

    written = render_weekly_pages(weekly_issues, templates_dir, out_dir, config_path)
    written.append(render_weekly_index(weekly_issues, templates_dir, out_dir, config))

    home_path = ensure_home_weekly_nav(out_dir)
    if home_path is not None:
        written.append(home_path)

    archive_path = patch_archive(out_dir, weekly_issues[0])
    if archive_path is not None:
        written.append(archive_path)

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
