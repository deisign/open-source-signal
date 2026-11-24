# Tool Radar — editorial backlog

Created 2026-11-24. Consult this file before every Saturday Tool Radar and subsequent Toolkit update. This is a candidate register, not the public Toolkit.

## Intake and evaluation

For each submitted tool inspect the original repository or official documentation, actual functionality, OSINT relevance, maintenance/release activity, license, installation and dependencies, costs, alternatives, evidence value, automation potential, privacy, legal and OPSEC risks. Distinguish documented features from claims and hands-on tests. Never invent test results. Deduplicate against this register, previous issues and data/osint_tools.yaml.

Reject low-value wrappers, abandoned or nonfunctional projects, redundant tools without meaningful advantages, misleading claims and unsafe tools. Do not fill a weekly issue with weak candidates.

## Statuses

- READY — editorially suitable for an upcoming Tool Radar.
- WATCHLIST — promising but immature or insufficiently documented.
- TEST_REQUIRED — practical verification needed before recommendation.
- REJECTED — excluded, with reason retained.
- PUBLISHED — covered in a dated Tool Radar issue.
- TOOLKIT — added to the canonical Toolkit; retain publication reference.

These are editorial backlog statuses, NOT the tested_status enum of the public Toolkit. Follow scripts/build_toolkit.py and brain.md when updating the Toolkit. Untested public candidates must not be described as tested.

## Candidate entry format

Each entry records name, canonical URL, intake date, category, actual capabilities, concrete OSINT use cases, alternatives and distinguishing value, license/access, maintenance evidence, limitations and risks, test evidence, editorial verdict and status, publication reference and Toolkit ID when applicable. Mark unknown facts explicitly.

## Workflow

Evaluate on receipt and record the verdict, including rejections to avoid repeated research. Before Saturday, review READY candidates and reassess WATCHLIST/TEST_REQUIRED where useful. Select only strong relevant items. Publication requires explicit approval. After publication, record the issue reference and update the canonical Toolkit registry where appropriate, deduplicating and validating it. Never publish automatically on intake.

## Candidates

No standalone tool candidates evaluated yet.

## Methodology and reading candidates — 2026-11-24

Articles are not software. Keep them separate from public Toolkit entries; extract and evaluate individual tools separately.

| Source | Status | Editorial assessment |
|---|---|---|
| [Tech Tactician — 12 Best Telegram Search Engines](https://techtactician.com/find-telegram-channels-best-search-engines/) | TEST_REQUIRED | Austin Maurice; 2025-07-01, updated 2026-07-28. Author reports testing; TGWorld explicitly offline. Useful discovery list, not an independent benchmark. Compare public-channel search coverage, freshness, relevance, access and privacy with standardized nonpersonal queries. Individual services not yet independently tested. |
| [Hackers Arise — You Can't Hide on Telegram](https://hackers-arise.com/open-source-intelligence-or-osint-you-cant-hide-on-telegram/) | REJECTED | OTW, 2025-02-20. Basic concepts mixed with privacy-invasive deanonymization and third-party bot recommendations; unsuitable for editorial endorsement. |
| [0xINT — Telegram OSINT Investigation](https://oxint.io/blog/telegram-osint-investigation/) | WATCHLIST | 2026-04-10. Commercial methodology article; useful selective background on public-channel repost graphs and evidence preservation. Overconfident attribution claims and unsafe recommendations preclude blanket endorsement. Independently verify any selected technique. |
| [Cybersecurity UA — post 947](https://t.me/cybersecurity_ua/947) | WATCHLIST | Ukrainian defensive OPSEC resource per submitter. Exact URL accessible only as Telegram embed shell during review; full post, date and claims not verified. Reassess when content available. |

Editorial idea: comparative benchmark of public Telegram channel search engines; no private-person lookup. Check existing Toolkit records before evaluating services individually. No hands-on testing performed during this intake. No publication or Toolkit changes approved.
