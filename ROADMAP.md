# Open Source Signal Roadmap

Open Source Signal is starting as a bilingual OSINT digest and static publishing toolkit. The direction is broader: reusable infrastructure for ethical, source-aware, public-interest OSINT publishing.

The project should help small teams and individual investigators publish better: with clearer source policies, safer editorial workflows, visible limits, and practical OSINT literacy for readers.

## Current foundation

The repository already supports:

- bilingual EN/UK issue files;
- static HTML issue rendering;
- front page and archive generation;
- Telegram announcement generation and manual publishing;
- GitHub Pages deployment;
- editorial and source policies;
- web and Telegram source registries;
- CI-tested Python/Jinja build pipeline.

## v1.2 — Weekly Magazine generator

Build a separate weekly edition under `/weekly/`.

The weekly should not be a mechanical merge of daily issues. It should work as an edited magazine issue with:

- editorial note;
- signal of the week;
- Ukraine Lens;
- War Crimes Verification;
- Losses, Captivity & Missing;
- Tradecraft;
- tools and datasets;
- Risk Watch;
- reading list.

## v1.3 — Evidence and source-risk layer

Add structured fields for higher-risk topics:

- evidence_level;
- source_type;
- risk_flags;
- public_interest;
- verification_status.

This is especially important for war-crimes cases, POW/KIA/MIA/missing topics, suspects, commanders, collaborators, Telegram-derived leads, and any material involving sensitive personal data.

## v1.4 — Topic landing pages

Generate topic pages for major editorial streams:

- War Crimes Verification;
- Ukraine Lens;
- Losses, Captivity & Missing;
- OSINT Tools;
- Geolocation;
- Investigator OPSEC;
- Telegram Radar;
- AI Verification.

Each page should explain the topic, list recent items, expose tags, and point readers to relevant methods and limits.

## v1.5 — Issue-specific social preview images

Generate per-issue Open Graph images with:

- logo;
- issue number;
- date;
- top rubrics;
- Daily / Weekly label.

The goal is better sharing without turning serious OSINT work into clickbait.

## v1.6 — Search and archive filters

Add static search and filtering by:

- rubric;
- tag;
- source;
- issue type;
- evidence level.

This should make the archive useful as a learning and reference tool, not only as a publication log.

## v1.7 — Link checker and archive URL support

Add source URL validation and reporting:

- broken-link report;
- optional archive_url field;
- warnings for missing or unstable source links.

The goal is to make older issues more durable and easier to audit.

## v1.8 — Telegram source collector prototype

Build a cautious Telethon-based lead collector:

- sources_telegram.yaml;
- raw message intake;
- candidate export;
- risk flags;
- manual review.

Telegram material must remain lead-only by default. No direct auto-publication from Telegram sources.

## Long-term direction

The long-term goal is not only to publish Open Source Signal faster.

The goal is to turn wartime OSINT practice into reusable public capacity: open workflows, transparent examples, safer source handling, and practical ethical OSINT literacy for Ukrainian and international readers.
