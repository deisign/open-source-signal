#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from static_pages import TRUST_NAV_LINKS

DEFAULT_SITE_CONFIG: dict[str, Any] = {
    "site_title_en": "Open Source Signal",
    "site_title_uk": "Сигнал відкритих джерел",
    "site_description_en": "A bilingual OSINT editorial radar for investigations, verification, maps, platforms, surveillance and researcher safety.",
    "site_description_uk": "Двомовний OSINT-радар про розслідування, верифікацію, мапи, платформи, інфраструктуру стеження й безпеку дослідника.",
    "base_url": "",
    "telegram_url": "https://t.me/open_source_signal_ua",
    "analytics_provider": "goatcounter",
    "analytics_id": "",
    "analytics_domain": "",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_config(config_path: Path | None) -> dict[str, Any]:
    config = dict(DEFAULT_SITE_CONFIG)
    if config_path and config_path.exists():
        config.update(load_json(config_path))
    return config


def make_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def absolute_url(base_url: str, path: str = "") -> str:
    if not base_url:
        return path
    base = base_url.rstrip("/")
    if not path:
        return base
    return f"{base}/{path.lstrip('/')}"


def analytics_snippet(config: dict[str, Any]) -> str:
    provider = str(config.get("analytics_provider", "")).strip().lower()
    analytics_id = str(config.get("analytics_id", "")).strip()
    analytics_domain = str(config.get("analytics_domain", "")).strip()
    if provider != "goatcounter" or not analytics_id:
        return ""
    if not analytics_domain:
        analytics_domain = f"{analytics_id}.goatcounter.com"
    analytics_domain = analytics_domain.removeprefix("https://").removeprefix("http://").rstrip("/")
    counter_url = f"https://{analytics_domain}/count"
    return f'<script data-goatcounter="https://{analytics_domain}/count" async src="{counter_url}.js"></script>'


def render_weekly(
    weekly_path: Path,
    templates_dir: Path,
    out_dir: Path,
    config_path: Path | None = None,
) -> Path:
    weekly = load_json(weekly_path)
    config = load_config(config_path)
    env = make_env(templates_dir)
    template = env.get_template("weekly.html.j2")

    output_name = str(weekly.get("output_name") or f"{weekly['slug']}.html")
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / output_name

    base_url = str(config.get("base_url", ""))
    page_url = absolute_url(base_url, f"weekly/{output_name}")
    og_image_url = absolute_url(base_url, "static/og-image.png")

    output_path.write_text(
        template.render(
            weekly=weekly,
            config=config,
            asset_prefix="../",
            page_url=page_url,
            og_image_url=og_image_url,
            meta_description=str(weekly.get("dek_en") or config.get("site_description_en", "")),
            analytics_snippet=analytics_snippet(config),
            trust_nav_links=TRUST_NAV_LINKS,
        ),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an Open Source Signal Weekly preview page.")
    parser.add_argument("weekly", type=Path, help="Weekly issue JSON file")
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--out", type=Path, default=Path("dist/weekly"))
    parser.add_argument("--config", type=Path, default=Path("site.json"))
    args = parser.parse_args()

    config_path = args.config if args.config.exists() else None
    path = render_weekly(args.weekly, args.templates, args.out, config_path)
    print(path)


if __name__ == "__main__":
    main()
