import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests" / "fixtures" / "daily_signal_sample.md"


def test_parse_daily_signal_creates_valid_issue():
    from import_daily_signal import parse_daily_signal

    issue = parse_daily_signal(SAMPLE.read_text(encoding="utf-8"), "2026-05-15", "002")
    assert issue["issue_number"] == "002"
    assert issue["date_iso"] == "2026-05-15"
    assert len(issue["items"]) == 2
    assert issue["items"][0]["rubric_en"] == "Ukraine Lens"
    assert issue["items"][0]["rubric_uk"] == "Українська оптика"
    assert issue["items"][0]["emoji"] == "🇺🇦"
    assert issue["items"][0]["source_name"] == "Slidstvo.Info"
    assert issue["items"][0]["source_url"] == "https://example.org/slidstvo-case"
    assert "Ukrainian investigators" in issue["items"][0]["what_happened_en"]
    assert "Українські розслідувачі" in issue["items"][0]["what_happened_uk"]
    assert issue["items"][1]["theme"] == "losses"
    assert "Telegram leads" in issue["internal_notes"][-1]


def test_import_daily_signal_cli_writes_json(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "import_daily_signal.py"),
            str(SAMPLE),
            "--date",
            "2026-05-15",
            "--issue",
            "002",
            "--out",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    out_path = Path(result.stdout.strip())
    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["items"][0]["title_en"].startswith("Ukrainian investigators")
    assert data["items"][1]["tags"] == ["losses", "KIA", "methodology", "Russia", "data"]


def test_import_daily_signal_refuses_overwrite(tmp_path):
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "import_daily_signal.py"),
            str(SAMPLE),
            "--date",
            "2026-05-15",
            "--issue",
            "002",
            "--out",
            str(tmp_path),
        ],
        check=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "import_daily_signal.py"),
            str(SAMPLE),
            "--date",
            "2026-05-15",
            "--issue",
            "002",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Refusing to overwrite" in result.stderr
