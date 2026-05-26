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


def normalize_url(url: str) -> str:
    cleaned = url.strip()
    cleaned = re.sub(r"(%20|\s)+title=$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[?&]utm_[^=&]+=[^&]+", "", cleaned)
    cleaned = cleaned.rstrip()
    return cleaned


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


def markdown_shortlist(rows: list[dict[str, Any]], limit: int = 30) -> str:
    lines = ["# GDELT shortlist", ""]
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


def run_self_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SlowRunnerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_tests()

    root = Path(args.root)
    run_dir = root / f"{args.date}-slow-run"
    combined_path = root / f"{args.date}-priority-combined.jsonl"
    shortlist_path = root / f"{args.date}-priority-shortlist.md"
    status_path = run_dir / "status.txt"
    radar_script = Path(args.radar_script)

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

    status_path.write_text(
        "".join(f"{result.pack} rc={result.returncode}\n" for result in results),
        encoding="utf-8",
    )

    ok_paths = [result.output_path for result in results if result.returncode == 0 and result.output_path.exists()]
    rows = combine_jsonl(ok_paths)
    write_jsonl(rows, combined_path)
    shortlist_path.write_text(markdown_shortlist(rows, args.top), encoding="utf-8")

    print()
    print(json.dumps({"combined": str(combined_path), "shortlist": str(shortlist_path), **summarize(rows)}, ensure_ascii=False, indent=2, sort_keys=True))
    print()
    print("STATUS:")
    print(status_path.read_text(encoding="utf-8").rstrip())
    print()
    print(f"TOP {args.top}:")
    for index, row in enumerate(rows[: args.top], 1):
        flags = ",".join(row.get("risk_flags") or [])
        print(f"{index:02d}. score={row.get('score', 0)} pack={row.get('query_pack', '')} domain={row.get('domain', '')} flags={flags}")
        print(f"    title: {row.get('title', '')}")
        print(f"    url:   {row.get('url', '')}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
