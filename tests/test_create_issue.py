import json
from pathlib import Path

import pytest

from create_issue import create_draft, publish_draft

ROOT = Path(__file__).resolve().parents[1]


def test_create_issue_draft_with_explicit_number(tmp_path):
    out_dir = tmp_path / "drafts"
    draft_path = create_draft("2026-05-14", "1", out_dir, ROOT / "issues")

    assert draft_path == out_dir / "2026-05-14.json"
    assert draft_path.exists()

    data = json.loads(draft_path.read_text(encoding="utf-8"))
    assert data["draft"] is True
    assert data["issue_number"] == "001"
    assert data["date_iso"] == "2026-05-14"
    assert data["date_label_en"] == "14 May 2026"
    assert data["date_label_uk"] == "14 травня 2026"
    assert data["items"] == []
    assert data["internal_notes"] == []


def test_create_issue_infers_next_number_from_existing_issues(tmp_path):
    issues_dir = tmp_path / "issues"
    issues_dir.mkdir()
    (issues_dir / "2026-05-13.json").write_text(
        json.dumps({"issue_number": "000"}, ensure_ascii=False),
        encoding="utf-8",
    )
    out_dir = tmp_path / "drafts"
    create_draft("2026-05-14", None, out_dir, issues_dir)
    data = json.loads((out_dir / "2026-05-14.json").read_text(encoding="utf-8"))
    assert data["issue_number"] == "001"


def test_create_issue_refuses_overwrite_without_force(tmp_path):
    out_dir = tmp_path / "drafts"
    create_draft("2026-05-14", "001", out_dir, ROOT / "issues")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        create_draft("2026-05-14", "001", out_dir, ROOT / "issues")


def test_publish_completed_draft_validates_and_removes_draft_marker(tmp_path):
    draft_path = tmp_path / "draft.json"
    source_issue = json.loads((ROOT / "issues" / "2026-05-13.json").read_text(encoding="utf-8"))
    source_issue["draft"] = True
    source_issue["issue_number"] = "001"
    source_issue["date_iso"] = "2026-05-14"
    source_issue["date_label_en"] = "14 May 2026"
    source_issue["date_label_uk"] = "14 травня 2026"
    draft_path.write_text(json.dumps(source_issue, ensure_ascii=False, indent=2), encoding="utf-8")

    issues_dir = tmp_path / "issues"
    published_path = publish_draft(draft_path, issues_dir)
    assert published_path == issues_dir / "2026-05-14.json"
    assert published_path.exists()
    published = json.loads(published_path.read_text(encoding="utf-8"))
    assert "draft" not in published
    assert published["issue_number"] == "001"


def test_publish_rejects_unfilled_draft(tmp_path):
    draft_path = create_draft("2026-05-14", "001", tmp_path, ROOT / "issues")
    with pytest.raises(ValueError, match="items"):
        publish_draft(draft_path, tmp_path / "issues")
