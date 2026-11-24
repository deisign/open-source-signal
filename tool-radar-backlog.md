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

Three standalone tool candidates assessed on 2026-11-24; see below.

## Methodology and reading candidates — 2026-11-24

Articles are not software. Keep them separate from public Toolkit entries; extract and evaluate individual tools separately.

| Source | Status | Editorial assessment |
|---|---|---|
| [Tech Tactician — 12 Best Telegram Search Engines](https://techtactician.com/find-telegram-channels-best-search-engines/) | TEST_REQUIRED | Austin Maurice; 2025-07-01, updated 2026-07-28. Author reports testing; TGWorld explicitly offline. Useful discovery list, not an independent benchmark. Compare public-channel search coverage, freshness, relevance, access and privacy with standardized nonpersonal queries. Individual services not yet independently tested. |
| [Hackers Arise — You Can't Hide on Telegram](https://hackers-arise.com/open-source-intelligence-or-osint-you-cant-hide-on-telegram/) | REJECTED | OTW, 2025-02-20. Basic concepts mixed with privacy-invasive deanonymization and third-party bot recommendations; unsuitable for editorial endorsement. |
| [0xINT — Telegram OSINT Investigation](https://oxint.io/blog/telegram-osint-investigation/) | WATCHLIST | 2026-04-10. Commercial methodology article; useful selective background on public-channel repost graphs and evidence preservation. Overconfident attribution claims and unsafe recommendations preclude blanket endorsement. Independently verify any selected technique. |
| [Cybersecurity UA — post 947](https://t.me/cybersecurity_ua/947) | WATCHLIST | Ukrainian defensive OPSEC resource per submitter. Exact URL accessible only as Telegram embed shell during review; full post, date and claims not verified. Reassess when content available. |

Editorial idea: comparative benchmark of public Telegram channel search engines; no private-person lookup. Check existing Toolkit records before evaluating services individually. No hands-on testing performed during this intake. No publication or Toolkit changes approved.

## Tool candidates — 2026-11-24: social monitoring and Telegram analysis

Intake: OSINTFlow reference https://t.me/osintflow/17265 and direct links. Evaluations below are documentation/source reviews, not hands-on tests. Canonical Toolkit data/osint_tools.yaml checked: no matching entries by name.

### RecentReborn — TEST_REQUIRED (editorial score 7/10)

- URL: https://recentreborn.com/ ; pricing https://recentreborn.com/pricing ; system status https://recentreborn.com/status ; release notes https://recentreborn.com/release-notes
- Category: Public social-media chronological discovery (Instagram, TikTok, YouTube).
- Documented: newest-first discovery by hashtag/keyword/location (platform-dependent); Chrome extension, dashboard, search history, REST API and MCP introduced in 2026.
- Pricing checked: Free 10 searches/day, 1-day history, Chrome extension and hashtag suggestions; Pro $9.99/month, 100 searches/day, 30-day history and exports; Business $39.99/month, 500/day, 60-day history and profile detail lookup. Refresh and load-more consume credits.
- Significant known limitation: provider status page says Instagram's changes have disabled chronological posts/reels results, with no near-term restoration anticipated. Provider says Instagram location, TikTok and YouTube search remain unaffected. Therefore do NOT present full Instagram coverage as currently working.
- OSINT fit: early discovery of public event footage and cross-platform keyword monitoring. Freshness, comprehensiveness and chronological guarantees not independently measured; paid black-box infrastructure and query/data handling need review.
- Next step: controlled test using non-personal public hashtags and known timestamped videos across platforms. Measure coverage, lag, ordering, duplicate rate, source-link preservation, actual quotas and OPSEC. Compare against native searches/other monitored services.
- Publication: not yet. Toolkit: not yet. No hands-on execution performed.

### TelepathyDB — WATCHLIST (provisional editorial score 6/10)

- URL: https://telepathydb.com/ ; vendor: https://prose.ltd/
- Category: Commercial Telegram public-channel search, historical archive, analytics.
- Vendor-documented: multilingual/boolean text and image search, forwards/network analytics, archive of public channels, engagement, translations, API. Vendor asserts large coverage; independent corpus-size and freshness testing absent.
- Availability: direct product landing page showed Anvil application error when checked 2026-11-24. Do not treat 14-day/no-card trial claim from submitter as verified current pricing; independently confirm when service recovers.
- Fit: potential source for historical public-post retrieval and comparative channel coverage; redundancy with local telegram-osint-metasearch must be tested, not assumed.
- Risks: paid hosted third-party query confidentiality; provider selection/corpus biases; missing/edited/deleted post semantics; risk of private-person deanonymization. Limit tests to public channels.
- Publication: not yet. Toolkit: not yet. No hands-on access tested.

### Telepathy Community — REJECTED (editorial score 2/10)

- Repository: https://github.com/prose-intelligence-ltd/Telepathy-Community
- Category: Python CLI for Telegram chat archiving and analytics. MIT. Described features include public chat scans, media/replies, forward edges and Gephi export.
- Verified from repository README 2026-11-24: owner explicitly states no active maintenance; last toolkit-source modification 2024-07-12; subsequent 2026 pushes were repository housekeeping. README documents unparseable main source (IndentationError), inconsistent Telethon dependency versions (setup.py vs requirements.txt), and inconsistent package version identifiers. GitHub repository metadata last_push 2026-08-13 does NOT indicate new functional releases.
- Decision: not recommend installation or Tool Radar feature in current condition; useful only as historical methodology/reference. Consider an actively maintained repaired fork if independently tested.
- Safety: avoid user/location lookup functions and any deanonymization of private persons. No installation tests were run.
- Publication: no. Toolkit: no.

Source confidence: provider claims are labelled as such; GitHub maintenance assessment grounded in the repository's own prominent notice, but no local install was run. These assessments must be refreshed before a later issue.


## Candidate intake — 2026-11-24: broad OSINTFlow batch

This batch contains **50 distinct candidates/references**. Evaluation is editorial, not hands-on execution. Checked selected official pages and GitHub metadata/README on 2026-11-24; other descriptions remain unverified intake leads. READY is an editorial shortlist, not a test certificate. Existing Toolkit entries must never be duplicated. No tool has been installed or tested during intake.

### Search syntax, privacy and defensive hygiene

| Candidate | Status | Editorial assessment |
|---|---|---|
| [One-Liner-OSINT](https://github.com/yogsec/One-Liner-OSINT) | REJECTED | MIT, active August 2026, but repetitive dorks, obsolete cache syntax, credential-hunting examples and unreliable search semantics; do not endorse |
| [Go for Dorks!](https://dorks.xen00rw.me/) | WATCHLIST | Multi-engine dork builder, latest site update Dec 2025; limited novelty; query semantics untested |
| [Best Free Data Breach Checker Tools](https://www.digitalfootprintcheck.com/free-data-breach-checker) | WATCHLIST | Vendor-published comparison; not impartial testing; use only for leads to defensive self-check resources |
| [Research Clinic Security](https://researchclinic.net/#Security) | READY | Paul Myers' investigation reference directory, useful for defensive exposure tools and methodology; individually verify links |
| [Cybersecurity UA /1126](https://t.me/cybersecurity_ua/1126) | WATCHLIST | Defensive self-removal from Google; full post not reviewed; confirm platform policies independently |
| [Cybersecurity UA /1241](https://t.me/cybersecurity_ua/1241) | WATCHLIST | Nonconsensual content/impersonation reporting; full post not reviewed |
| [Cybersecurity UA /1204](https://t.me/cybersecurity_ua/1204) | WATCHLIST | Self-data removal collection; full post not reviewed |
| [OSINT Atlas](https://intelfocus.org/osint-atlas/) | TEST_REQUIRED | Intel Focus catalogue shows 151 entries in source; test curation, update dates, links and overlap |

### Extraction, archiving and browser infrastructure

| Candidate | Status | Editorial assessment |
|---|---|---|
| [Firecrawl](https://firecrawl.dev/) | TEST_REQUIRED | Hosted extraction; test page-to-Markdown, reference preservation, pricing and data retention |
| [Jina AI Reader](https://jina.ai/reader/) | TEST_REQUIRED | Hosted readable text extraction; compare with Defuddle and Crawl4AI; quotas unverified |
| [Apify](https://apify.com/) | WATCHLIST | Marketplace not one product; actor quality and cost vary; no standalone Tool Radar slot yet |
| [Thunderbit](https://thunderbit.com/) | WATCHLIST | Browser extraction convenience; price, security and distinctiveness not verified |
| [RSS.app](https://rss.app/) | TEST_REQUIRED | Website/social RSS generation; benchmark freshness and source fidelity against existing media-monitoring/n8n |
| [Crawl4AI](https://github.com/unclecode/crawl4ai) | TOOLKIT | Existing canonical id crawl4ai; maintained Apache-2.0, no duplicate |
| [Browser Use](https://github.com/browser-use/browser-use) | TEST_REQUIRED | MIT browser-agent framework; assess traceability, dependencies, reproducibility and privacy |
| [Crawlee](https://github.com/apify/crawlee) | TEST_REQUIRED | Apache-2.0 crawler, actively maintained; compare JS/TS against Scrapy and local stack |
| [Scrapy](https://github.com/scrapy/scrapy) | READY | Mature maintained BSD-3-Clause Python crawler; baseline utility, not automatically novel news |
| [Scrapling](https://github.com/D4Vinci/Scrapling) | TEST_REQUIRED | Maintained BSD-3-Clause; documented adaptive selectors and extraction, high relevance to unstable source sites |
| [AutoScraper](https://github.com/alirezamika/autoscraper) | WATCHLIST | MIT example-driven extractor; unknown resilience to modern dynamic sites, likely less robust than Scrapling |
| [Defuddle](https://github.com/kepano/defuddle) | TEST_REQUIRED | Maintained MIT content-to-Markdown parser used in Obsidian Web Clipper; strong potential for source-aware pipeline |
| [curl_cffi](https://github.com/lexiforest/curl_cffi) | WATCHLIST | Maintained MIT low-level HTTP/browser-fingerprint transport component; no standalone editorial novelty |
| [curl-impersonate](https://github.com/lwthiker/curl-impersonate) | REJECTED | Older related project last repository push July 2024; redundant with maintained curl_cffi as presented |
| [CloakBrowser](https://github.com/CloakHQ/CloakBrowser) | WATCHLIST | MIT patched browser, recent development; claimed anti-bot success unverified, free versus Pro binaries differ; security/terms risks |
| [invisible_playwright](https://github.com/feder-cr/invisible_playwright) | WATCHLIST | Patched Firefox wrapper; maintenance indicated by changelog, binary trust and anti-detection marketing require audit |

### Geospatial, Telegram, identity search and audio

| Candidate | Status | Editorial assessment |
|---|---|---|
| [Soar Atlas](https://soaratlas.com/) | TEST_REQUIRED | Satellite maps and timelines; JS-only app inaccessible to text fetch. Verify capture countdown, watermark, dates, provenance and licensing |
| [Teleteg](https://teleteg.com/) | TEST_REQUIRED | Public channel/group index with activity, language and creation filters; claims about searching individual users' messages not independently verified |
| [uFind.name](https://ufind.name/) | WATCHLIST | Reported Google CSE wrapper; inaccessible during review, privacy/false-positive concerns and limited novelty |
| [IDCrawl](https://www.idcrawl.com/) | WATCHLIST | People search alternative, untested; avoid private-person profiling and false identity inference |
| [Webmii](https://webmii.com/) | WATCHLIST | Public name-search lead, untested; name collisions |
| [Social Searcher](https://www.social-searcher.com/) | TEST_REQUIRED | Search for public social mentions; benchmark against RecentReborn on same public terms |
| [User Searcher](https://www.user-searcher.com/) | WATCHLIST | Username search, untested; matching handle does not prove identity |
| [WhatsMyName](https://whatsmyname.app/) | TEST_REQUIRED | Username-search resource; validate supported-site recency and false-positive behavior |
| [Sherlock](https://github.com/sherlock-project/sherlock) | TOOLKIT | Already exists in canonical Toolkit, id sherlock |
| [Namechk](https://namechk.com/) | WATCHLIST | Username/domain availability only, not identity verification |
| [DTMF Tone Generator and Decoder](https://freetoolcabin.com/dtmf-tone-generator/) | TEST_REQUIRED | Despite title, page describes decoder; test symbol accuracy with controlled consenting audio, don't expose phone numbers |
| [DOPPLERGEIST](https://github.com/1337isnot1337/DOPPLERGEIST) | TEST_REQUIRED | Aircraft acoustic Doppler and ADS-B location hypothesis; PolyForm Noncommercial source-available, not open-source; time/geographic bounds, large downloads and independent accuracy validation essential |

### Tool directories and research databases

| Candidate | Status | Editorial assessment |
|---|---|---|
| [Bellingcat Online Investigation Toolkit](https://bellingcat.gitbook.io/toolkit) | TOOLKIT | Already in canonical Toolkit, id bellingcat_online_investigation_toolkit |
| [OSINT Tools Library](https://tools.osintnewsletter.com/) | WATCHLIST | External directory; check dead links and curation against current Toolkit |
| [Awesome OSINT](https://github.com/jivoi/awesome-osint) | WATCHLIST | Maintained open-source resource list; no standalone functionality, compare with existing directories |
| [OSINT Stuff Tool Collection](https://github.com/cipher387/osint_stuff_tool_collection) | TEST_REQUIRED | Active GitHub collection with niche leads, validate links/dedup before editorial endorsement |
| [The OSINT Rack](https://osintrack.com/) | WATCHLIST | Thematic tool directory, current curation and usefulness not verified |
| [OCCRP ID — Research Databases](https://id.occrp.org/databases/) | READY | Relevant global research-database catalogue for public-interest company/court/procurement investigations; database discovery not verification |

### Media authenticity and deepfake verification

| Candidate | Status | Editorial assessment |
|---|---|---|
| [DeepFake-O-Meter](https://zinc.cse.buffalo.edu/ubmdfl/deep-o-meter/) | TEST_REQUIRED | Academic multi-detector tool; verify present support, input handling, error rates and data retention |
| [Deepware Scanner](https://deepware.ai/us/index.html) | WATCHLIST | Vendor deepfake video scanner; modality and independent accuracy unverified |
| [Reality Defender](https://www.realitydefender.com/) | WATCHLIST | Commercial multimodal classifier; unverified benchmarks, privacy and false positives |
| [Sensity AI](https://sensity.ai/) | WATCHLIST | Commercial synthetic media detection; accuracy/terms unverified |
| [AI or Not](https://www.aiornot.com/) | WATCHLIST | Commercial synthetic-content classifier; detection score not proof |
| [InVID / WeVerify](https://www.invid-project.eu/tools-and-services/invid-verification-plugin) | TOOLKIT | Already in canonical Toolkit id invid_weverify; keyframe/source verification is not definitive deepfake detection |
| [Hiya Deepfake Voice Detector](https://www.hiya.com/products/deepfake-voice-detector) | WATCHLIST | Vendor voice classifier; modalities, reliability and processing privacy not yet tested |

### Browser fingerprinting and investigator OPSEC

| Candidate | Status | Editorial assessment |
|---|---|---|
| [Detect.Expert](https://github.com/vektort13/Detect.Expert) | TEST_REQUIRED | New MIT fingerprint forensics extension, repo created Nov 7 2026; 158-API guard claimed, strong defensive angle; source/permission audit required, README notes no IP/TLS/engine spoof and detector blind spots |

### Editorial shortlist and evaluation protocol

Priority tests: **DOPPLERGEIST** (novel, high uncertainty and noncommercial licence), **Defuddle** (editorial Markdown extraction), **Scrapling** (robust scraping), **Soar Atlas** (imagery dates), **Teleteg** (compare with internal telegram-osint-metasearch), **Detect.Expert** (observable browser tracking), **RSS.app** (source-feed continuity). Strong reference entries: **OCCRP ID**, **Research Clinic** and **Scrapy**. Already in Toolkit and not new: **Crawl4AI, Sherlock, Bellingcat Toolkit, InVID/WeVerify**.

Controlled comparisons should use legal/public sample data and independently timestamped reference records, record version and date, capture original URL and checksums where applicable, measure precision/recall and missing-data behavior, test privacy/OPSEC and licence limits. No credential harvesting, private-person deanonymization, illicit access or operational targeting. Deepfake classifiers offer uncertainty signals, never proof of authenticity or fabrication.

Source notes: GitHub metadata accessed for yogsec/One-Liner-OSINT, 1337isnot1337/DOPPLERGEIST, vektort13/Detect.Expert, crawl4ai, browser-use, Crawlee, Scrapy, Scrapling, AutoScraper, Defuddle, curl_cffi, curl-impersonate, CloakBrowser, Awesome OSINT and OSINT Stuff; product descriptions checked selectively via official pages. DOPPLERGEIST explicitly PolyForm Noncommercial; its examples are not independent benchmarks. Detect.Expert README calls Chrome store listing pending and acknowledges browser-level blind spots. Teleteg's own documentation emphasizes indexing public channels/groups rather than proving person-message search. Do not equate GitHub push dates to new working feature releases.

Other OSINTFlow posts mentioned Google/Drive/DuckDuckGo/Bing/YouTube/Yandex query guides: these are **search-method articles**, not additional software candidates. Treat them as a reading-reference bundle until individually examined: https://t.me/osintflow/13267, https://t.me/osintflow/3861, https://t.me/osintflow/3519, https://t.me/osintflow/8387, https://t.me/osintflow/13089, https://t.me/osintflow/12850, https://t.me/osintflow/12959, https://t.me/osintflow/727, https://t.me/osintflow/11487. The alleged Soar release posts https://x.com/SoarAtlas/status/2097942789904568677 and OSINT Atlas launch https://x.com/IntelFocusHQ/status/2089260224813080936 are pointers only; verify original posting dates before describing as 'today's' news.

No public issue created; no Telegram request created; no canonical Toolkit edits made.
