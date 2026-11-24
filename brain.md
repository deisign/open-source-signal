# Open Source Signal — brain.md

Last updated: 2026-11-24 (Europe/Kyiv). Read this file before every editorial or publishing session. This is the operational memory, not a replacement for the code or editorial policies. Update it after confirmed publication or an operational change.

## 1. Identity and editorial contract

- Repository: deisign/open-source-signal, branch main.
- Website: https://osintsignal.org
- Telegram: https://t.me/open_source_signal_ua
- Bilingual English/Ukrainian publication; Telegram normally Ukrainian.
- Ukrainian accountability lens AND international OSINT tradecraft. Prioritize verification, war-crimes documentation, losses/captivity/missing, investigations, maps, platforms, surveillance and researcher safety.
- Read README.md, docs/EDITORIAL_POLICY.md, docs/SOURCE_POLICY.md and relevant workflow before changing anything.
- Weekday Daily Signal; Saturday Tool Radar; Sunday weekly journal. Use Europe/Kyiv dates and check latest existing issue numbers; weekly editions use ISO week numbers.
- Collect and present draft first. Never publish without explicit user approval. An instruction to publish an approved draft does not require another confirmation. Site first, successful deployment second, Telegram third. Do not silently substitute another day's issue.
- Prefer 5–9 strong items, seven as a soft default. No filler. Verify direct original URLs, publication/event dates and claims before committing; identify historical material as retrospective. Syndication and collaborative partners are not independent corroboration. Do not treat AI-generated summaries as primary evidence.
- Both languages are edited adaptations, not literal translations. Explain what happened, why it matters, how to use it, and limits. Follow source roles and safety boundaries in the policies. No private personal data or operational targeting guidance.

## 2. Canonical files — do not invent parallel infrastructure

- Daily and Saturday: issues/YYYY-MM-DD.json; use latest successful issue of the same type as schema reference (2026-11-24.json Daily, 2026-11-21.json Tool Radar).
- Drafts: drafts/; create_issue.py and import_daily_signal.py are existing authoring tools.
- Weekly: weekly/open-source-signal-weekly-YYYY-Www.json; reference weekly/open-source-signal-weekly-2026-W47.json.
- Site: build_site.py, render_issue.py, templates/, site.json; generated output dist/.
- Toolkit: data/osint_tools.yaml, data/osint_tool_categories.yaml, scripts/build_toolkit.py, templates/toolkit.html.j2. Public page https://osintsignal.org/toolkit/. Do NOT use data/toolkit.json as a second registry.
- Source registries: data/sources_web.yaml, data/sources_telegram.yaml.
- Daily Telegram: telegram_digest.py, send_telegram.py, telegram_sent_log.py, .github/workflows/telegram.yml, telegram/requests/, data/telegram_sent.json.
- Weekly Telegram: .github/workflows/weekly-telegram.yml, telegram/weekly_requests/. Current implementation is hardcoded to W47; inspect and update for the actual week before triggering. It does not share daily duplicate protection. Never rerun blindly.

## 3. Daily schema and validation

Use the complete existing issue structure, including issue_number (string), date_iso, date_label_en/uk, slug (open-source-signal), title_en/uk, issue_type, language_label, subtitle_en/uk, dek_en/uk, editorial_frame, rubric_map, footer_note, internal_notes (list), items (nonempty list). Preserve field types and conventions from the appropriate successful reference. Actual required fields are defined in render_issue.py.

Each item: theme, emoji, rubric_en/uk, title_en/uk, source_name, source_url, source_date_label_en/uk, what_happened_en/uk, why_it_matters_en/uk, how_to_use_en/uk, limits_en/uk, tags (nonempty list). Other required item fields are nonempty strings. Internal notes are not public.

Weekly schema differs: use its own reference, including output_name, week_label_en/uk, editorial_note_en/uk, reading_list and compact_sections. Do not feed weekly JSON into the daily renderer.

## 4. Publication runbook

1. Read brain.md and relevant source files; inspect latest main, recent issues, current date, existing requests and latest Actions results. Avoid overwriting existing issues.
2. Research, verify sources and prepare bilingual draft. Wait for explicit publication approval.
3. Validate using existing scripts. In a checkout run:
   ```bash
   python -m pytest -q
   python build_site.py --issues issues --templates templates --out dist --config site.json
   ```
   If local execution is unavailable, do not claim local tests passed; inspect actual CI results. Fix failures before Telegram.
4. Commit only the intended issue and approved associated data. .github/workflows/pages.yml builds and deploys on main pushes. Find the run for the exact commit; wait for completed/success, verify public issue URL. A commit or queued run is NOT a successful deployment.
5. For daily Telegram after deployment, check data/telegram_sent.json for the issue/language and existing request. Create exactly one new request telegram/requests/YYYY-MM-DD-uk-NNN.json containing:
   ```json
   {"issue":"YYYY-MM-DD.json","lang":"uk","max_items":7,"force":false}
   ```
   The existing push-triggered workflow resolves exactly one added/modified request. Do not modify old requests or use force=true unless user explicitly requests a resend. Use the actual number of items within 1–9 where appropriate. Manual workflow_dispatch is also supported.
6. Check the Telegram run: Send Telegram announcement, Record Telegram send, Commit Telegram sent log. Verify the record on main. Distinguish sent, recorded, failed and queued. If send succeeded but log push failed, recover the exact record from job logs and commit only that record; NEVER resend.
7. Weekly: verify site deployment, correct week and URL in weekly workflow; check prior delivery, then create a single weekly request. Verify actual send step; do not claim daily-style log protection exists.
8. Report issue URL, commit, deployment run and Telegram result. Update this file with verified state. No unrelated redesigns, new schemas or infrastructure.

GitHub Actions status can be read from the repository API endpoint /repos/deisign/open-source-signal/actions/runs?per_page=10, and /actions/runs/RUN_ID. Match head_sha and workflow name. Inspect jobs and logs for errors. Never report queued as completed.

## 5. Toolkit rules

On approved Saturday Tool Radar publication, add relevant tools to the existing Toolkit registry, deduplicate by id/name/URL and update existing entries rather than creating duplicates. Inspect scripts/build_toolkit.py for schema and allowed values before editing.

Allowed tested_status: core, recommended, situational, watchlist, caution, deprecated, rejected. Untested candidates belong in watchlist, not an invented untested status. Never claim hands-on testing without evidence. Public entries require bilingual use_cases/input/output/notes, valid URL, no high legal or OPSEC risk, and no rejected/deprecated status. Validate categories and all enum values. Run tests/build before reporting success.

## 6. Verified state — 2026-11-24

- Saturday #165: issues/2026-11-21.json; Toolkit additions committed 6d5bf9e. Invalid tested_status fixed in 8153d05. Redundant data/toolkit.json was created earlier; not canonical, cleanup pending separate review.
- Weekly W47 (16–22 November): weekly/open-source-signal-weekly-2026-W47.json; Telegram run 45161830404 succeeded.
- Daily #166 (23 November): Pages run 45161836669 succeeded. Telegram run 45161836713 sent successfully but failed to push the log. Exact record recovered in f1f2f19; no resend.
- Telegram fix f27de77: after staging sent log, restore unstaged tracked changes in CI before rebase. Retry only log push. Earlier failed Telegram runs since November 6 need log-by-log reconciliation, not resending.
- Daily #167 (24 November): issue commit 391124cc686ff7bf0472f88e54c9f535b8c46c2a; Pages run 45365914206 completed successfully. URL https://osintsignal.org/issues/open-source-signal-2026-11-24.html.
- #167 Telegram request commit 721b4065174dea73be96e0ed329fc376887a9918; run 45366896037; sent_at 2026-11-24T09:37:28Z; confirmed record exists on main in data/telegram_sent.json. User confirmed announcement appeared. No resend.
- Next ordinary daily issue: #168 on 25 November, subject to checking current repository state and user approval.

## 7. Open operational debt

- Reconcile older failed Telegram runs using exact successful send evidence; never fabricate timestamps or resend to repair logs.
- Weekly Telegram workflow is hardcoded and lacks durable duplicate protection. Generalization is separate engineering work, not an improvised change during publication.
- Review redundant data/toolkit.json separately.
- Keep source verification distinct from successful rendering/deployment: green CI does not establish factual accuracy or URL validity.

## 8. Tool Radar candidate intake

Read `tool-radar-backlog.md` before Saturday selection and Toolkit updates. Evaluate user-submitted tools on receipt, record verdicts including rejections, and deduplicate against prior issues and the canonical Toolkit. Intake is not publication approval. Backlog statuses are separate from Toolkit tested_status values.
