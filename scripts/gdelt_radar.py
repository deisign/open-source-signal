#!/usr/bin/env python3
"""GDELT radar for Open Source Signal.

Collects lead-only article candidates from the GDELT DOC 2.0 API and writes JSONL.
No third-party dependencies.

Examples:
  python gdelt_radar.py --timespan 72h --out data/leads/gdelt/today.jsonl
  python gdelt_radar.py --query-pack war_crimes_verification --maxrecords 50
  python gdelt_radar.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GDELT_DOC_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"

QUERY_PACKS: dict[str, dict[str, str]] = {
    "war_crimes_verification": {
        "rubric": "War Crimes Verification / Верифікація воєнних злочинів",
        "query": '("Ukraine" OR "Ukrainian") ("war crimes" OR "war crime" OR atrocities OR atrocity OR "International Criminal Court" OR ICC OR "prosecutor general" OR "deported children" OR filtration OR torture)',
    },
    "losses_captivity_missing": {
        "rubric": "Losses, Captivity & Missing / Втрати, полон, зниклі",
        "query": '("Ukraine" OR Russia OR Russian) (POW OR "prisoner of war" OR captivity OR "missing soldiers" OR MIA OR KIA OR "body exchange" OR "repatriated bodies")',
    },
    "ukraine_osint_geolocation": {
        "rubric": "Ukraine Lens / Українська оптика",
        "query": '("Ukraine" OR "Ukrainian") (OSINT OR geolocation OR "open source intelligence" OR "satellite imagery" OR "video verification" OR "image verification")',
    },
    "ai_verification": {
        "rubric": "AI Verification / ШІ та верифікація",
        "query": '("Ukraine war" OR "Russia Ukraine") (deepfake OR "AI-generated" OR "synthetic media" OR "image manipulation" OR "AI verification")',
    },
    "tool_radar": {
        "rubric": "Tool Radar / Інструментальний радар",
        "query": '(OSINT OR "open source intelligence") ("new tool" OR toolkit OR GitHub OR "satellite imagery" OR geolocation OR verification OR "social media analysis")',
    },
    "platform_watch": {
        "rubric": "Platform Watch / Платформний радар",
        "query": '(Telegram OR "social media") ("Ukraine war" OR Russia) (propaganda OR disinformation OR "war crimes" OR OSINT OR verification)',
    },
}

PRIMARY_OR_HIGH_TRUST_DOMAINS = {
    "icc-cpi.int",
    "ohchr.org",
    "un.org",
    "coe.int",
    "icrc.org",
    "bellingcat.com",
    "occrp.org",
    "hrw.org",
    "amnesty.org",
    "truth-hounds.org",
    "zmina.info",
    "helsinki.org.ua",
    "globalrightscompliance.com",
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "theguardian.com",
    "kyivindependent.com",
    "pravda.com.ua",
    "rferl.org",
    "rusi.org",
    "understandingwar.org",
    "atlanticcouncil.org",
    "airwars.org",
    "github.com",
}

LOW_VALUE_DOMAINS = {
    "msn.com",
    "yahoo.com",
    "news.google.com",
    "flipboard.com",
    "dnyuz.com",
    "biztoc.com",
}

PRIMARY_KEYWORDS = {
    "court",
    "prosecutor",
    "indictment",
    "warrant",
    "report",
    "dataset",
    "investigation",
    "methodology",
    "evidence",
    "satellite",
    "geolocation",
    "verification",
    "github",
}

RISK_PATTERNS: list[tuple[str, str]] = [
    (r"\b(doxx?ing|doxxed|dox)\b", "doxxing_language"),
    (r"\b(phone numbers?|home addresses?|passport|personal data|leaked database|dump)\b", "personal_data_risk"),
    (r"\b(family members?|wives|children|relatives)\b", "family_data_risk"),
    (r"\b(unverified|alleged|rumor|rumour)\b", "unverified_claim_risk"),
]


@dataclass(frozen=True)
class Candidate:
    collected_at: str
    query_pack: str
    rubric_candidate: str
    query: str
    title: str
    url: str
    domain: str
    seen_date: str
    language: str
    source_country: str
    social_image: str
    score: int
    evidence_level: str
    source_type: str
    verification_status: str
    risk_flags: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "collected_at": self.collected_at,
            "query_pack": self.query_pack,
            "rubric_candidate": self.rubric_candidate,
            "query": self.query,
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "seen_date": self.seen_date,
            "language": self.language,
            "source_country": self.source_country,
            "social_image": self.social_image,
            "score": self.score,
            "evidence_level": self.evidence_level,
            "source_type": self.source_type,
            "verification_status": self.verification_status,
            "risk_flags": self.risk_flags,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_gdelt_url(query: str, timespan: str, maxrecords: int, mode: str = "artlist") -> str:
    params = {
        "query": query,
        "mode": mode,
        "format": "json",
        "timespan": timespan,
        "maxrecords": str(maxrecords),
        "sort": "datedesc",
    }
    return f"{GDELT_DOC_ENDPOINT}?{urlencode(params)}"


def fetch_json(url: str, timeout: int = 30) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "OpenSourceSignal-GDELT-Radar/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed public API endpoint
            raw = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise RuntimeError(f"GDELT HTTP error {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"GDELT network error: {exc.reason}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GDELT returned invalid JSON: {exc}") from exc


def clean_domain(domain: str) -> str:
    domain = domain.lower().strip()
    domain = domain.removeprefix("www.")
    return domain


def detect_risks(title: str, url: str) -> list[str]:
    text = f"{title} {url}".lower()
    flags: list[str] = []
    for pattern, flag in RISK_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            flags.append(flag)
    return sorted(set(flags))


def score_candidate(title: str, url: str, domain: str, query_pack: str, risk_flags: list[str]) -> int:
    text = f"{title} {url}".lower()
    score = 3

    if domain in PRIMARY_OR_HIGH_TRUST_DOMAINS:
        score += 3
    if domain in LOW_VALUE_DOMAINS:
        score -= 3
    if any(keyword in text for keyword in PRIMARY_KEYWORDS):
        score += 2
    if "ukraine" in text or "ukrainian" in text:
        score += 1
    if query_pack in {"war_crimes_verification", "losses_captivity_missing"}:
        score += 1
    if risk_flags:
        score -= min(4, len(risk_flags) * 2)
    if not title or not url:
        score -= 5

    return max(0, min(10, score))


def article_to_candidate(article: dict[str, Any], query_pack: str, collected_at: str) -> Candidate | None:
    pack = QUERY_PACKS[query_pack]
    title = str(article.get("title") or "").strip()
    url = str(article.get("url") or "").strip()
    if not url:
        return None

    domain = clean_domain(str(article.get("domain") or ""))
    risk_flags = detect_risks(title, url)
    score = score_candidate(title, url, domain, query_pack, risk_flags)

    return Candidate(
        collected_at=collected_at,
        query_pack=query_pack,
        rubric_candidate=pack["rubric"],
        query=pack["query"],
        title=title,
        url=url,
        domain=domain,
        seen_date=str(article.get("seendate") or article.get("date") or ""),
        language=str(article.get("language") or ""),
        source_country=str(article.get("sourcecountry") or ""),
        social_image=str(article.get("socialimage") or ""),
        score=score,
        evidence_level="lead_only",
        source_type="gdelt_doc_article_candidate",
        verification_status="needs_editorial_review",
        risk_flags=risk_flags,
    )


def collect(query_packs: list[str], timespan: str, maxrecords: int, sleep_seconds: float = 1.0) -> list[Candidate]:
    collected_at = utc_now_iso()
    candidates: list[Candidate] = []
    seen_urls: set[str] = set()

    for index, query_pack in enumerate(query_packs):
        if query_pack not in QUERY_PACKS:
            raise ValueError(f"Unknown query pack: {query_pack}")
        url = build_gdelt_url(QUERY_PACKS[query_pack]["query"], timespan, maxrecords)
        payload = fetch_json(url)
        articles = payload.get("articles", [])
        if not isinstance(articles, list):
            articles = []
        for article in articles:
            if not isinstance(article, dict):
                continue
            candidate = article_to_candidate(article, query_pack, collected_at)
            if candidate is None or candidate.url in seen_urls:
                continue
            seen_urls.add(candidate.url)
            candidates.append(candidate)
        if index != len(query_packs) - 1 and sleep_seconds > 0:
            time.sleep(sleep_seconds)

    candidates.sort(key=lambda item: (-item.score, item.seen_date, item.title))
    return candidates


def write_jsonl(candidates: list[Candidate], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for candidate in candidates:
            handle.write(json.dumps(candidate.as_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def summarize(candidates: list[Candidate]) -> dict[str, Any]:
    by_pack: dict[str, int] = {}
    high_score = 0
    risky = 0
    for candidate in candidates:
        by_pack[candidate.query_pack] = by_pack.get(candidate.query_pack, 0) + 1
        if candidate.score >= 8:
            high_score += 1
        if candidate.risk_flags:
            risky += 1
    return {
        "total": len(candidates),
        "high_score_8_plus": high_score,
        "with_risk_flags": risky,
        "by_query_pack": by_pack,
    }


def demo_candidates() -> list[Candidate]:
    collected_at = "2026-05-16T09:00:00+00:00"
    fixture = [
        {
            "title": "Investigators publish new geolocation methodology for Ukraine war-crimes evidence",
            "url": "https://www.bellingcat.com/example/geolocation-methodology-ukraine",
            "domain": "bellingcat.com",
            "seendate": "20260516T081500Z",
            "language": "English",
            "sourcecountry": "United Kingdom",
        },
        {
            "title": "Random repost: shocking leaked phone numbers of soldiers' families",
            "url": "https://msn.com/example/leaked-phone-numbers",
            "domain": "msn.com",
            "seendate": "20260516T082000Z",
            "language": "English",
            "sourcecountry": "United States",
        },
    ]
    return [
        candidate
        for article in fixture
        if (candidate := article_to_candidate(article, "war_crimes_verification", collected_at)) is not None
    ]


class GdeltRadarTests(unittest.TestCase):
    def test_build_gdelt_url_encodes_query(self) -> None:
        url = build_gdelt_url('"Ukraine" "war crimes"', "72h", 25)
        self.assertIn("mode=artlist", url)
        self.assertIn("format=json", url)
        self.assertIn("timespan=72h", url)
        self.assertIn("maxrecords=25", url)
        self.assertIn("%22Ukraine%22+%22war+crimes%22", url)

    def test_risk_detection(self) -> None:
        flags = detect_risks("Leaked phone number and home address", "https://example.org")
        self.assertIn("personal_data_risk", flags)

    def test_candidate_scoring(self) -> None:
        high = article_to_candidate(
            {
                "title": "New report on Ukraine war crimes evidence and geolocation",
                "url": "https://www.bellingcat.com/example",
                "domain": "bellingcat.com",
            },
            "war_crimes_verification",
            "2026-05-16T09:00:00+00:00",
        )
        low = article_to_candidate(
            {
                "title": "Leaked phone number dump",
                "url": "https://msn.com/example",
                "domain": "msn.com",
            },
            "war_crimes_verification",
            "2026-05-16T09:00:00+00:00",
        )
        self.assertIsNotNone(high)
        self.assertIsNotNone(low)
        assert high is not None and low is not None
        self.assertGreaterEqual(high.score, 8)
        self.assertLessEqual(low.score, 2)
        self.assertIn("personal_data_risk", low.risk_flags)

    def test_jsonl_write(self) -> None:
        temp = Path("/tmp/gdelt_radar_test.jsonl")
        candidates = demo_candidates()
        write_jsonl(candidates, temp)
        lines = temp.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 2)
        parsed = json.loads(lines[0])
        self.assertEqual(parsed["evidence_level"], "lead_only")
        temp.unlink(missing_ok=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect lead-only GDELT candidates for Open Source Signal.")
    parser.add_argument("--timespan", default="72h", help="GDELT timespan, e.g. 24h, 72h, 7d, 1w")
    parser.add_argument("--maxrecords", type=int, default=75, help="Records per query pack")
    parser.add_argument("--query-pack", action="append", choices=sorted(QUERY_PACKS), help="Query pack to run; repeatable")
    parser.add_argument("--out", default="data/leads/gdelt/gdelt_leads.jsonl", help="Output JSONL path")
    parser.add_argument("--sleep", type=float, default=1.0, help="Delay between GDELT requests")
    parser.add_argument("--demo", action="store_true", help="Write deterministic demo candidates without network")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(GdeltRadarTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    out_path = Path(args.out)
    if args.demo:
        candidates = demo_candidates()
    else:
        query_packs = args.query_pack or list(QUERY_PACKS)
        candidates = collect(query_packs, args.timespan, args.maxrecords, args.sleep)

    write_jsonl(candidates, out_path)
    print(json.dumps({"out": str(out_path), **summarize(candidates)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
