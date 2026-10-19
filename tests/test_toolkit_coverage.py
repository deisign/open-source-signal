import json
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

from scripts.build_toolkit import build_toolkit

ROOT = Path(__file__).resolve().parents[1]
TOOLS = yaml.safe_load((ROOT / 'data/osint_tools.yaml').read_text())


def test_coverage_references_resolve_to_real_published_cards():
    for tool in TOOLS:
        reviews = tool['publication_refs']
        mentions = tool['mention_refs']
        expected = 'reviewed' if reviews else 'mentioned_only' if mentions else 'not_covered'
        assert tool['coverage_status'] == expected
        for ref in reviews + mentions:
            section = ref.get('section', 'issues')
            issue = json.loads((ROOT / section / ref['issue']).read_text())
            assert 0 <= ref['item_index'] < len(issue['items'])
            filename = issue.get('output_name') or (
                issue['slug'] + '.html' if section == 'weekly'
                else 'open-source-signal-' + issue['date_iso'] + '.html'
            )
            assert ref['href'] == section + '/' + filename


def test_archive_imports_do_not_claim_runtime_or_access_testing():
    for tool in TOOLS:
        if tool.get('archive_review'):
            assert tool['access_details_verified'] is False
            assert tool['review_summary_en'] and tool['review_summary_uk']
            assert 'not re-tested' in tool['notes']


def test_coverage_renders_review_mention_and_uncovered_states(tmp_path):
    html = build_toolkit(out_dir=tmp_path).read_text()
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.select_one('#docling .coverage a')['href'] == '../issues/open-source-signal-2026-10-17.html'
    assert 'Mentioned only' in soup.select_one('#mapillary .coverage').get_text()
    assert 'No coverage found' in soup.select_one('#perma_cc .coverage').get_text()
    assert soup.select_one('#securedrop .coverage a')
    assert soup.select_one('#shadohdorks') is None
    assert soup.select_one('#geospy') is None
    assert 'No API' not in soup.select_one('#docling .tag-row').get_text()


def test_deployment_rebuilds_toolkit_from_registry():
    workflow = (ROOT / '.github/workflows/pages.yml').read_text()
    assert 'python scripts/build_toolkit.py --out dist --config site.json' in workflow
