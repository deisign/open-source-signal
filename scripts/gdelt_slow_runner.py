#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import unittest
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

DEFAULT_PACKS = [
    "war_crimes_verification",
    "losses_captivity_missing",
    "ukraine_osint_geolocation",
    "ai_verification",
    "platform_watch",
]

DEFAULT_DROP_DOMAINS = {
    "msn.com",
    "yahoo.com",
    "news.google.com",
    "flipboard.com",
    "dnyuz.com",
    "biztoc.com",
    "finance.sina.com.cn",
    "ntdtv.com",
    "weeklyblitz.net",
    "dailypioneer.com",
    "wptf.com",
    "news.mail.ru",
    "russian.rt.com",
    "rt.com",
    "iz.ru",
}

DEFAULT_TOPIC_TERMS = {
    "ukraine",
    "ukrainian",
    "україна",
    "україни",
    "украин",
    "kyiv",
    "kiev",
    "київ",
    "russia",
    "russian",
    "росія",
    "россии",
    "россий",
    "kremlin",
    "кремл",
    "oreshnik",
    "орешник",
    "war crime",
    "war crimes",
    "воєнн",
    "военн",
    "pow",
    "prisoner",
    "captivity",
    "полон",
    "mia",
    "kia",
    "missing",
    "зникл",
    "casualties",
    "losses",
    "втрат",
    "osint",
    "geolocation",
    "verification",
    "satellite",
    "deepfake",
    "ai-generated",
    "malware",
    "cyber",
    "telegram",
    "bluesky",
    "propaganda",
    "disinformation",
}


def normalize_url(url: str) -> str:
    cleaned = url.strip()
    cleaned = re.sub(r"(%20|\s)+title=$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"([?&])utm_[^=&]+=[^&]*", r"\1", cleaned)
    cleaned = re.sub(r"[?&]+$", "", cleaned)
    return cleaned.rstrip()


def normalize_domain(domain: str) -> str:
    cleaned = domain.strip().lower()
    return cleaned.removeprefix("www.")


def domain_matches(domain: str, blocked_domain: str) -> bool:
    domain = normalize_domain(domain)
    blocked_domain = normalize_domain(blocked_domain)
    return domain == blocked_domain or domain.endswith("." + blocked_domain)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSONL in {path}:{line_no}: {exc}") from exc
        if isinstance(row, dict):
            rows.append(row)
    return rows


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def combine_jsonl(paths: list[Path]) -> list[dict[str, Any]]:
    best_by_url: dict[str, dict[str, Any]] = {}

    for path in paths:
        for row in read_jsonl(path):
            url = normalize_url(str(row.get("url", "")))
            if not url:
                continue
            row["url"] = url
            row["domain"] = normalize_domain(str(row.get("domain", "")))
            old = best_by_url.get(url)
            if old is None or int(row.get("score", 0)) > int(old.get("score", 0)):
                best_by_url[url] = row

    rows = list(best_by_url.values())
    rows.sort(
        key=lambda row: (
            int(row.get("score", 0)),
            str(row.get("seen_date", "")),
            str(row.get("title", "")),
        ),
        reverse=True,
    )
    return rows


def has_topic_signal(row: dict[str, Any], topic_terms: set[str] | None = None) -> bool:
    terms = topic_terms or DEFAULT_TOPIC_TERMS
    haystack = f"{row.get('title', '')} {row.get('url', '')} {row.get('query_pack', '')}".lower()
    return any(term.lower() in haystack for term in terms)


def filter_reason(
    row: dict[str, Any],
    *,
    min_score: int,
    drop_domains: set[str],
    keep_risky: bool,
    require_topic: bool,
) -> str | None:
    score = int(row.get("score", 0))
    if score < min_score:
        return "low_score"

    domain = normalize_domain(str(row.get("domain", "")))
    if any(domain_matches(domain, blocked) for blocked in drop_domains):
        return "dropped_domain"

    if row.get("risk_flags") and not keep_risky:
        return "risk_flags"

    if require_topic and not has_topic_signal(row):
        return "no_topic_signal"

    return None


def filter_rows(
    rows: list[dict[str, Any]],
    *,
    min_score: int = 3,
    drop_domains: set[str] | None = None,
    keep_risky: bool = False,
    require_topic: bool = True,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    drop_domains = drop_domains or set()
    kept: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()

    for row in rows:
        reason = filter_reason(
            row,
            min_score=min_score,
            drop_domains=drop_domains,
            keep_risky=keep_risky,
            require_topic=require_topic,
        )
        if reason is None:
            kept.append(row)
        else:
            reasons[reason] += 1

    return kept, reasons


def markdown_shortlist(rows: list[dict[str, Any]], limit: int = 30) -> str:
    lines = ["# GDELT shortlist", ""]
    if not rows:
        lines.extend(["No candidates passed the current local filters.", ""])
        return "\n".join(lines)

    for index, row in enumerate(rows[:limit], 1):
        flags = ", ".join(row.get("risk_flags") or [])
        flag_text = flags if flags else "none"
        lines.extend(
            [
                f"## {index}. score={row.get('score', 0)} — {row.get('query_pack', '')}",
                "",
                f"- domain: `{row.get('domain', '')}`",
                f"- risk_flags: `{flag_text}`",
                f"- title: {row.get('title', '')}",
                f"- url: {row.get('url', '')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class RunResult:
    pack: str
    returncode: int
    output_path: Path


def run_pack(
    pack: str,
    *,
    radar_script: Path,
    output_path: Path,
    timespan: str,
    maxrecords: int,
    timeout: int,
    retries: int,
    backoff: float,
) -> RunResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(radar_script),
        "--timespan",
        timespan,
        "--maxrecords",
        str(maxrecords),
        "--query-pack",
        pack,
        "--timeout",
        str(timeout),
        "--retries",
        str(retries),
        "--backoff",
        str(backoff),
        "--sleep",
        "0",
        "--out",
        str(output_path),
    ]
    print(f"\n=== GDELT PACK: {pack} ===", flush=True)
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        output_path.unlink(missing_ok=True)
    return RunResult(pack=pack, returncode=completed.returncode, output_path=output_path)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(rows),
        "high_score_8_plus": sum(1 for row in rows if int(row.get("score", 0)) >= 8),
        "with_risk_flags": sum(1 for row in rows if row.get("risk_flags")),
        "by_query_pack": dict(Counter(str(row.get("query_pack", "")) for row in rows)),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Slow GDELT runner for Open Source Signal.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Run date label, YYYY-MM-DD")
    parser.add_argument("--root", default="data/leads/gdelt", help="Output root directory")
    parser.add_argument("--timespan", default="24h", help="GDELT timespan")
    parser.add_argument("--maxrecords", type=int, default=10, help="Records per query pack")
    parser.add_argument("--pack", action="append", choices=DEFAULT_PACKS, help="Query pack to run; repeatable")
    parser.add_argument("--delay", type=float, default=300.0, help="Delay between packs in seconds")
    parser.add_argument("--timeout", type=int, default=90, help="Network timeout per request")
    parser.add_argument("--retries", type=int, default=2, help="Retry attempts inside gdelt_radar.py")
    parser.add_argument("--backoff", type=float, default=60.0, help="Base backoff inside gdelt_radar.py")
    parser.add_argument("--top", type=int, default=30, help="How many leads to print and put into shortlist")
    parser.add_argument("--radar-script", default="scripts/gdelt_radar.py", help="Path to gdelt_radar.py")
    parser.add_argument("--input-jsonl", help="Existing JSONL to filter without calling GDELT")
    parser.add_argument("--min-score", type=int, default=3, help="Minimum score for shortlist candidates")
    parser.add_argument("--drop-domain", action="append", default=[], help="Additional domain to drop from shortlist; repeatable")
    parser.add_argument("--no-default-drop-domains", action="store_true", help="Disable built-in low-value domain drops")
    parser.add_argument("--keep-risky", action="store_true", help="Keep candidates with risk_flags in shortlist")
    parser.add_argument("--no-topic-filter", action="store_true", help="Disable topical relevance filter for shortlist")
    parser.add_argument("--self-test", action="store_true", help="Run unit tests without network")
    return parser.parse_args(argv)


class SlowRunnerTests(unittest.TestCase):
    def test_normalize_url_removes_title_suffix(self) -> None:
        self.assertEqual(
            normalize_url("https://example.org/a%20title="),
            "https://example.org/a",
        )

    def test_combine_keeps_highest_score(self) -> None:
        with TemporaryDirectory() as tmpdir:
            first = Path(tmpdir) / "a.jsonl"
            second = Path(tmpdir) / "b.jsonl"
            write_jsonl(
                [
                    {
                        "url": "https://example.org/item",
                        "score": 3,
                        "title": "low",
                        "seen_date": "20260526T080000Z",
                    }
                ],
                first,
            )
            write_jsonl(
                [
                    {
                        "url": "https://example.org/item",
                        "score": 9,
                        "title": "high",
                        "seen_date": "20260526T090000Z",
                    }
                ],
                second,
            )
            rows = combine_jsonl([first, second])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["score"], 9)
            self.assertEqual(rows[0]["title"], "high")

    def test_markdown_shortlist_contains_title_and_risk_flags(self) -> None:
        text = markdown_shortlist(
            [
                {
                    "score": 7,
                    "query_pack": "ai_verification",
                    "domain": "example.org",
                    "risk_flags": ["unverified_claim_risk"],
                    "title": "Example title",
                    "url": "https://example.org/story",
                }
            ],
            limit=1,
        )
        self.assertIn("Example title", text)
        self.assertIn("unverified_claim_risk", text)

    def test_filter_rows_drops_low_value_domain(self) -> None:
        rows = [
            {
                "score": 4,
                "query_pack": "platform_watch",
                "domain": "yahoo.com",
                "risk_flags": [],
                "title": "Russia sees spate of wartime school attacks",
                "url": "https://yahoo.com/example",
            }
        ]
        kept, reasons = filter_rows(rows, min_score=3, drop_domains=DEFAULT_DROP_DOMAINS)
        self.assertEqual(kept, [])
        self.assertEqual(reasons["dropped_domain"], 1)

    def test_filter_rows_keeps_bluesky_kremlin_signal(self) -> None:
        rows = [
            {
                "score": 3,
                "query_pack": "platform_watch",
                "domain": "thestar.com.my",
                "risk_flags": [],
                "title": "Bluesky says Kremlin is hacking its platform to spread propaganda",
                "url": "https://www.thestar.com.my/tech/example",
            }
        ]
        kept, reasons = filter_rows(rows, min_score=3, drop_domains=DEFAULT_DROP_DOMAINS)
        self.assertEqual(len(kept), 1)
        self.assertEqual(reasons, Counter())

    def test_filter_rows_drops_no_topic_signal(self) -> None:
        rows = [
            {
                "score": 3,
                "query_pack": "platform_watch",
                "domain": "thetimes.com",
                "risk_flags": [],
                "title": "At Cannes, the sound of institutions creaking",
                "url": "https://www.thetimes.com/comment/columnists/example",
            }
        ]
        kept, reasons = filter_rows(rows, min_score=3, drop_domains=DEFAULT_DROP_DOMAINS)
        self.assertEqual(kept, [])
        self.assertEqual(reasons["no_topic_signal"], 1)


def run_self_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SlowRunnerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def local_filter_outputs(
    *,
    rows: list[dict[str, Any]],
    root: Path,
    run_date: str,
    top: int,
    min_score: int,
    drop_domains: set[str],
    keep_risky: bool,
    require_topic: bool,
) -> tuple[Path, Path, list[dict[str, Any]], Counter[str]]:
    shortlist_jsonl_path = root / f"{run_date}-priority-shortlist.jsonl"
    shortlist_md_path = root / f"{run_date}-priority-shortlist.md"
    filtered_rows, reasons = filter_rows(
        rows,
        min_score=min_score,
        drop_domains=drop_domains,
        keep_risky=keep_risky,
        require_topic=require_topic,
    )
    write_jsonl(filtered_rows, shortlist_jsonl_path)
    shortlist_md_path.write_text(markdown_shortlist(filtered_rows, top), encoding="utf-8")
    return shortlist_jsonl_path, shortlist_md_path, filtered_rows, reasons


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_tests()

    root = Path(args.root)
    run_dir = root / f"{args.date}-slow-run"
    combined_path = root / f"{args.date}-priority-combined.jsonl"
    status_path = run_dir / "status.txt"
    radar_script = Path(args.radar_script)
    drop_domains = set(args.drop_domain)
    if not args.no_default_drop_domains:
        drop_domains |= DEFAULT_DROP_DOMAINS
    require_topic = not args.no_topic_filter

    if args.input_jsonl:
        rows = combine_jsonl([Path(args.input_jsonl)])
        write_jsonl(rows, combined_path)
        status_text = "input_jsonl rc=0"
    else:
        packs = args.pack or DEFAULT_PACKS
        run_dir.mkdir(parents=True, exist_ok=True)
        results: list[RunResult] = []
        for index, pack in enumerate(packs):
            result = run_pack(
                pack,
                radar_script=radar_script,
                output_path=run_dir / f"{pack}.jsonl",
                timespan=args.timespan,
                maxrecords=args.maxrecords,
                timeout=args.timeout,
                retries=args.retries,
                backoff=args.backoff,
            )
            results.append(result)
            if index != len(packs) - 1 and args.delay > 0:
                print(f"Sleeping {args.delay:.0f}s before next pack...", flush=True)
                time.sleep(args.delay)
        status_text = "".join(f"{result.pack} rc={result.returncode}\n" for result in results).rstrip()
        status_path.write_text(status_text + "\n", encoding="utf-8")
        ok_paths = [result.output_path for result in results if result.returncode == 0 and result.output_path.exists()]
        rows = combine_jsonl(ok_paths)
        write_jsonl(rows, combined_path)

    shortlist_jsonl_path, shortlist_md_path, filtered_rows, filter_reasons = local_filter_outputs(
        rows=rows,
        root=root,
        run_date=args.date,
        top=args.top,
        min_score=args.min_score,
        drop_domains=drop_domains,
        keep_risky=args.keep_risky,
        require_topic=require_topic,
    )

    print()
    print(
        json.dumps(
            {
                "combined": str(combined_path),
                "shortlist_jsonl": str(shortlist_jsonl_path),
                "shortlist": str(shortlist_md_path),
                "raw": summarize(rows),
                "shortlist_summary": summarize(filtered_rows),
                "filter_reasons": dict(filter_reasons),
                "min_score": args.min_score,
                "default_drop_domains": not args.no_default_drop_domains,
                "topic_filter": require_topic,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    print()
    print("STATUS:")
    print(status_text)
    print()
    print(f"TOP {args.top}:")
    for index, row in enumerate(filtered_rows[: args.top], 1):
        flags = ",".join(row.get("risk_flags") or [])
        print(f"{index:02d}. score={row.get('score', 0)} pack={row.get('query_pack', '')} domain={row.get('domain', '')} flags={flags}")
        print(f"    title: {row.get('title', '')}")
        print(f"    url:   {row.get('url', '')}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
