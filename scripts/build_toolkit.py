#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CONFIG = {
    "site_title_en": "Open Source Signal",
    "site_title_uk": "Сигнал відкритих джерел",
    "base_url": "",
    "rss_path": "feed.xml",
    "telegram_url": "https://t.me/open_source_signal_ua",
}

CATEGORY_REQUIRED_FIELDS = {
    "id",
    "title_en",
    "title_uk",
    "description_en",
    "description_uk",
    "order",
}

TOOL_REQUIRED_FIELDS = {
    "id",
    "name",
    "url",
    "category",
    "use_cases",
    "input",
    "output",
    "access",
    "requires_login",
    "api_available",
    "opsec_level",
    "legal_risk",
    "evidence_value",
    "automation_value",
    "learning_cost",
    "tested_status",
    "public",
    "project_fit",
    "notes",
}

PUBLIC_TOOL_UK_FIELDS = {
    "use_cases_uk",
    "input_uk",
    "output_uk",
    "notes_uk",
}

ALLOWED_VALUES = {
    "access": {"free", "freemium", "paid", "mixed"},
    "opsec_level": {"low", "medium", "high"},
    "legal_risk": {"low", "medium", "high"},
    "evidence_value": {"low", "medium", "high"},
    "automation_value": {"none", "low", "medium", "high"},
    "learning_cost": {"low", "medium", "high"},
    "tested_status": {"core", "recommended", "situational", "watchlist", "caution", "deprecated", "rejected"},
}

BLOCKED_PUBLIC_STATUSES = {"rejected", "deprecated"}


def load_yaml(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a YAML list")
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"{path} item {index} must be a mapping")
    return data


def load_config(config_path: Path | None) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if config_path and config_path.exists():
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("Site config must be a JSON object")
        config.update(loaded)
    return config


def absolute_url(base_url: str, path: str = "") -> str:
    if not base_url:
        return path
    base = base_url.rstrip("/")
    if not path:
        return base
    return f"{base}/{path.lstrip('/')}"


def validate_categories(categories: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    seen: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for category in categories:
        missing = CATEGORY_REQUIRED_FIELDS - set(category)
        if missing:
            raise ValueError(f"Category {category.get('id', '<unknown>')} missing fields: {sorted(missing)}")
        category_id = str(category["id"])
        if category_id in seen:
            raise ValueError(f"Duplicate category id: {category_id}")
        if not isinstance(category["order"], int):
            raise ValueError(f"Category {category_id} order must be an integer")
        seen.add(category_id)
        by_id[category_id] = category
    return by_id


def _validate_url(tool: dict[str, Any]) -> None:
    parsed = urlparse(str(tool["url"]))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Public tool {tool['id']} must have a valid http/https URL")


def _validate_non_empty_string_list(tool: dict[str, Any], field: str) -> None:
    if not isinstance(tool[field], list) or not tool[field] or not all(isinstance(item, str) and item for item in tool[field]):
        raise ValueError(f"Tool {tool['id']} {field} must be a non-empty list of strings")


def validate_tools(tools: list[dict[str, Any]], category_ids: set[str]) -> None:
    seen: set[str] = set()
    for tool in tools:
        missing = TOOL_REQUIRED_FIELDS - set(tool)
        if missing:
            raise ValueError(f"Tool {tool.get('id', '<unknown>')} missing fields: {sorted(missing)}")

        tool_id = str(tool["id"])
        if tool_id in seen:
            raise ValueError(f"Duplicate tool id: {tool_id}")
        seen.add(tool_id)

        category = str(tool["category"])
        if category not in category_ids:
            raise ValueError(f"Tool {tool_id} references unknown category: {category}")

        for field, allowed in ALLOWED_VALUES.items():
            if tool[field] not in allowed:
                raise ValueError(f"Tool {tool_id} has invalid {field}: {tool[field]}")

        _validate_non_empty_string_list(tool, "use_cases")
        if not isinstance(tool["requires_login"], bool):
            raise ValueError(f"Tool {tool_id} requires_login must be boolean")
        if not isinstance(tool["api_available"], bool):
            raise ValueError(f"Tool {tool_id} api_available must be boolean")
        if not isinstance(tool["public"], bool):
            raise ValueError(f"Tool {tool_id} public must be boolean")

        if tool["public"]:
            uk_missing = PUBLIC_TOOL_UK_FIELDS - set(tool)
            if uk_missing:
                raise ValueError(f"Public tool {tool_id} missing Ukrainian fields: {sorted(uk_missing)}")
            _validate_url(tool)
            for field in ("use_cases_uk", "input_uk", "output_uk"):
                _validate_non_empty_string_list(tool, field)
            if not isinstance(tool["notes_uk"], str) or not tool["notes_uk"]:
                raise ValueError(f"Public tool {tool_id} notes_uk must be a non-empty string")
            if tool["legal_risk"] == "high":
                raise ValueError(f"Public tool {tool_id} cannot have high legal risk")
            if tool["opsec_level"] == "high":
                raise ValueError(f"Public tool {tool_id} cannot have high OPSEC level")
            if tool["tested_status"] in BLOCKED_PUBLIC_STATUSES:
                raise ValueError(f"Public tool {tool_id} cannot be {tool['tested_status']}")


def validate_toolkit_data(categories: list[dict[str, Any]], tools: list[dict[str, Any]]) -> None:
    category_by_id = validate_categories(categories)
    validate_tools(tools, set(category_by_id))


def group_public_tools(categories: list[dict[str, Any]], tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public_tools = [tool for tool in tools if tool["public"]]
    groups: list[dict[str, Any]] = []
    for category in sorted(categories, key=lambda item: (item["order"], item["id"])):
        category_tools = sorted(
            [tool for tool in public_tools if tool["category"] == category["id"]],
            key=lambda item: item["name"].lower(),
        )
        if category_tools:
            groups.append({"category": category, "tools": category_tools})
    return groups


def make_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_toolkit(
    categories_path: Path = ROOT / "data" / "osint_tool_categories.yaml",
    tools_path: Path = ROOT / "data" / "osint_tools.yaml",
    templates_dir: Path = ROOT / "templates",
    out_dir: Path = ROOT / "dist",
    config_path: Path | None = ROOT / "site.json",
    config: dict[str, Any] | None = None,
) -> Path:
    categories = load_yaml(categories_path)
    tools = load_yaml(tools_path)
    validate_toolkit_data(categories, tools)

    site_config = dict(DEFAULT_CONFIG)
    site_config.update(config if config is not None else load_config(config_path))

    grouped_categories = group_public_tools(categories, tools)
    template = make_env(templates_dir).get_template("toolkit.html.j2")
    toolkit_dir = out_dir / "toolkit"
    toolkit_dir.mkdir(parents=True, exist_ok=True)
    output_path = toolkit_dir / "index.html"

    page_url = absolute_url(str(site_config.get("base_url", "")), "toolkit/")
    output_path.write_text(
        template.render(
            config=site_config,
            asset_prefix="../",
            page_url=page_url,
            og_image_url=absolute_url(str(site_config.get("base_url", "")), "static/og-image.png"),
            analytics_snippet="",
            grouped_categories=grouped_categories,
            trust_nav_links=[
                {"label": "About", "href": "about.html"},
                {"label": "Methodology", "href": "methodology.html"},
                {"label": "Ethics", "href": "ethics.html"},
                {"label": "Contact", "href": "contact.html"},
                {"label": "Subscribe", "href": "subscribe.html"},
                {"label": "Archive", "href": "archive.html"},
                {"label": "RSS", "href": "feed.xml"},
            ],
        ),
        encoding="utf-8",
    )
    public_count = sum(1 for tool in tools if tool["public"])
    print(f"Built toolkit: {public_count} public tools across {len(grouped_categories)} categories -> {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the OSINT Signal Toolkit static page.")
    parser.add_argument("--categories", type=Path, default=ROOT / "data" / "osint_tool_categories.yaml")
    parser.add_argument("--tools", type=Path, default=ROOT / "data" / "osint_tools.yaml")
    parser.add_argument("--templates", type=Path, default=ROOT / "templates")
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    parser.add_argument("--config", type=Path, default=ROOT / "site.json")
    args = parser.parse_args()

    config_path = args.config if args.config.exists() else None
    build_toolkit(args.categories, args.tools, args.templates, args.out, config_path)


if __name__ == "__main__":
    main()
