from pathlib import Path
from urllib.parse import urlparse

from scripts.build_toolkit import (
    BLOCKED_PUBLIC_STATUSES,
    TOOL_REQUIRED_FIELDS,
    load_yaml,
    validate_toolkit_data,
)

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = load_yaml(ROOT / "data" / "osint_tool_categories.yaml")
TOOLS = load_yaml(ROOT / "data" / "osint_tools.yaml")


def test_tool_ids_are_unique():
    ids = [tool["id"] for tool in TOOLS]
    assert len(ids) == len(set(ids))


def test_tool_categories_exist():
    category_ids = {category["id"] for category in CATEGORIES}
    assert all(tool["category"] in category_ids for tool in TOOLS)


def test_public_tools_have_valid_http_urls():
    for tool in TOOLS:
        if not tool["public"]:
            continue
        parsed = urlparse(tool["url"])
        assert parsed.scheme in {"http", "https"}
        assert parsed.netloc


def test_public_tools_obey_safety_rules():
    for tool in TOOLS:
        if not tool["public"]:
            continue
        assert tool["legal_risk"] != "high"
        assert tool["opsec_level"] != "high"
        assert tool["tested_status"] not in BLOCKED_PUBLIC_STATUSES


def test_public_tools_have_required_fields():
    for tool in TOOLS:
        if tool["public"]:
            assert TOOL_REQUIRED_FIELDS <= set(tool)


def test_at_least_15_public_tools_exist():
    assert sum(1 for tool in TOOLS if tool["public"]) >= 15


def test_no_rejected_or_deprecated_tool_is_public():
    assert all(not tool["public"] for tool in TOOLS if tool["tested_status"] in BLOCKED_PUBLIC_STATUSES)


def test_toolkit_data_validates_as_a_whole():
    validate_toolkit_data(CATEGORIES, TOOLS)
