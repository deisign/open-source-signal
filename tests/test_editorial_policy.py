from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITORIAL = ROOT / "docs" / "EDITORIAL_POLICY.md"
SOURCE_POLICY = ROOT / "docs" / "SOURCE_POLICY.md"
WEB_SOURCES = ROOT / "data" / "sources_web.yaml"
TELEGRAM_SOURCES = ROOT / "data" / "sources_telegram.yaml"
README = ROOT / "README.md"
CREATE_ISSUE = ROOT / "create_issue.py"


def test_editorial_policy_defines_ukrainian_accountability_focus():
    text = EDITORIAL.read_text(encoding="utf-8")
    assert "Ukrainian accountability OSINT" in text
    assert "War Crimes Verification / Верифікація воєнних злочинів" in text
    assert "Losses, Captivity & Missing / Втрати, полон, зниклі" in text
    assert "Telegram Radar / Telegram-радар" in text
    assert "When the source is Ukrainian-only" in text
    assert "alleged" in text
    assert "convicted" in text


def test_source_policy_marks_evocation_as_source_pointer():
    text = SOURCE_POLICY.read_text(encoding="utf-8")
    assert "Evocation.info" in text
    assert "source_pointer" in text
    assert "independent verification" in text


def test_web_sources_include_required_ukrainian_sources():
    text = WEB_SOURCES.read_text(encoding="utf-8")
    for required in [
        "InformNapalm",
        "Molfar",
        "Texty.org.ua",
        "Slidstvo.Info",
        "NGL.media",
        "Truth Hounds",
        "OSINT for Ukraine",
        "DeepStateMap",
        "KibOrg",
        "RussianWarCriminals",
        "Evocation.info",
        "Mediazona / BBC confirmed Russian deaths",
    ]:
        assert required in text
    assert "https://evocation.info/" in text
    assert "english_adaptation_needed" in text


def test_telegram_sources_are_candidate_sources_not_automatic_evidence():
    text = TELEGRAM_SOURCES.read_text(encoding="utf-8")
    assert "Candidate Telegram source registry" in text
    assert "verify_handle_before_use" in text
    assert "do_not_auto_publish" in text
    assert "private phone numbers" in text
    assert "Evocation.info" in text


def test_readme_mentions_policy_files_and_reverse_adaptation():
    text = README.read_text(encoding="utf-8")
    assert "docs/EDITORIAL_POLICY.md" in text
    assert "data/sources_web.yaml" in text
    assert "Ukrainian-only material is adapted back into English" in text
    assert "Evocation.info is included as a source pointer" in text


def test_new_draft_defaults_include_ukrainian_accountability_rubrics():
    text = CREATE_ISSUE.read_text(encoding="utf-8")
    assert "Ukrainian accountability" in text
    assert "Ukraine Lens" in text
    assert "War Crimes Verification" in text
    assert "Losses, Captivity & Missing" in text
    assert "Telegram Radar" in text
