from pathlib import Path

from scripts.build_toolkit import build_toolkit

ROOT = Path(__file__).resolve().parents[1]


def test_build_toolkit_creates_static_page(tmp_path):
    output_path = build_toolkit(
        categories_path=ROOT / "data" / "osint_tool_categories.yaml",
        tools_path=ROOT / "data" / "osint_tools.yaml",
        templates_dir=ROOT / "templates",
        out_dir=tmp_path / "dist",
        config_path=ROOT / "site.json",
    )

    assert output_path == tmp_path / "dist" / "toolkit" / "index.html"
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "OSINT Signal Toolkit" in html
    assert "SunCalc" in html
    assert "Інструментарій відкритих джерел" in html
    assert "EN:" in html
    assert "UK:" in html
    assert "Для чого" in html
    assert "Вхідні дані" in html
    assert "<details" in html
    assert "<summary" in html
    assert "curated verification-oriented toolkit" in html


def test_build_toolkit_does_not_render_non_public_rejected_or_deprecated(tmp_path):
    tools_path = tmp_path / "tools.yaml"
    tools_path.write_text(
        (ROOT / "data" / "osint_tools.yaml").read_text(encoding="utf-8")
        + """
- id: retired_youtube_dataviewer
  name: Retired YouTube DataViewer
  url: https://citizenevidence.org/
  category: workflow_methods
  use_cases:
    - Historical review of excluded sources
  input: Public URL
  output: Exclusion note
  access: free
  requires_login: false
  api_available: false
  opsec_level: low
  legal_risk: low
  evidence_value: low
  automation_value: none
  learning_cost: low
  tested_status: rejected
  public: false
  project_fit: Excluded from public toolkit because it is no longer maintained.
  notes: Test fixture for rejected-status filtering.
""",
        encoding="utf-8",
    )

    output_path = build_toolkit(
        categories_path=ROOT / "data" / "osint_tool_categories.yaml",
        tools_path=tools_path,
        templates_dir=ROOT / "templates",
        out_dir=tmp_path / "dist",
        config_path=ROOT / "site.json",
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Retired YouTube DataViewer" not in html
