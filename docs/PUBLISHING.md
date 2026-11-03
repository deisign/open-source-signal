# Open Source Signal — publication runbook

## Canonical issue format

The publication source is `issues/YYYY-MM-DD.json`, not a Markdown article. Match the structure of the most recent valid issue and the requirements in `render_issue.py`, `issue.schema.json` and `docs/EDITORIAL_POLICY.md`.

The canonical publication name is **Open Source Signal / Сигнал відкритих джерел** (`title_en`, `title_uk`). Preserve `slug: open-source-signal`, `issue_type`, bilingual fields, dated primary-source links, evidence limits, tags and `internal_notes`. Do not change the publication's title or invent an alternative format.

Daily Signal runs Monday–Friday; Saturday is Tool Radar, Sunday is Weekly Magazine. Choose verified OSINT investigations, verification methodology, Ukraine accountability material and relevant international cases. Do not pad the issue with generic news or unverified links.

## Standard publication sequence

1. Read `docs/EDITORIAL_POLICY.md` and the most recent `issues/*.json`.
2. Research, check original URLs and dates, write `issues/YYYY-MM-DD.json` using the existing issue schema.
3. Validate the JSON with `render_issue.validate_issue` and `python -m pytest -q`; build with `python build_site.py --issues issues --templates templates --out dist --config site.json`.
4. Commit the complete JSON to `main`. The existing site build/deploy workflow is triggered by the commit; verify its run succeeded and the page is accessible.
5. After the site is live, publish Telegram using the **Publish Telegram announcement** workflow (`.github/workflows/telegram.yml`) with `issue=YYYY-MM-DD.json`, `lang=uk`, `max_items=7`, `force=false`.
6. Check `data/telegram_sent.json` and the workflow result. Never claim Telegram publication merely because the issue was committed.

## Assistant-triggered Telegram announcement

GitHub's connected file-write API can create files but does not expose `workflow_dispatch`. To trigger Telegram from a file commit, `.github/workflows/telegram.yml` can accept a `push` event restricted to `telegram/requests/*.json`. A new, uniquely named request file triggers the workflow. The workflow reads the request and uses the same rendering, duplicate check, Telegram secrets, send script and sent log as the manual workflow.

Example request:
```json
{"issue":"2026-11-03.json","lang":"uk","max_items":7,"force":false}
```

**Guardrails:** publish only after the issue page is live; use a unique request filename per attempt; do not set `force=true` without explicit approval; `data/telegram_sent.json` prevents repeat sends. A request commit is not proof of delivery. Confirm a successful run and the sent-log entry.

## Recovery

If the build fails, inspect the actual Actions log before making changes. Do not create placeholder or incomplete JSON. If Telegram has already been sent manually, do not resend. Check the sent log and use `force=false` to avoid duplicates. If a workflow run is still queued or running, report that state accurately.

## Historical incident — 2026-11-03

Issue #150 was initially mishandled as Markdown and then an incomplete JSON was briefly committed. The corrected JSON was committed at `4d561f04570a5138eebf27b16db45dab4e9de3da`. The operator confirmed the site deployed and manually triggered the Telegram workflow. This is why the canonical JSON-first sequence and automation bridge are documented here.

## Verified automation bridge — 2026-11-03

- Telegram workflow: `.github/workflows/telegram.yml`, with both `workflow_dispatch` and `push` on `telegram/requests/*.json`.
- ChatGPT's connected GitHub file-create action can commit a uniquely named request JSON, which starts the Telegram workflow. Required JSON: `{"issue":"YYYY-MM-DD.json","lang":"uk","max_items":7,"force":false}`.
- The workflow resolves the request, validates parameters, builds and renders, checks `data/telegram_sent.json`, and sends only if not already recorded. Keep `force=false` by default.
- **Verified green test:** [GitHub Actions run 41630966085](https://github.com/deisign/open-source-signal/actions/runs/41630966085) completed with `success`. This test targeted the already-sent `2026-11-03.json` and was designed to exercise duplicate protection.
- The manual Telegram send of issue #150 was recorded separately in `data/telegram_sent.json` under run `41630501757` at `2026-11-03T11:49:01Z`.
- Operational sequence: commit validated issue JSON → wait for successful site deployment → create a new `telegram/requests/YYYY-MM-DD-<unique>.json` → verify successful Telegram Actions run and sent-log entry. Do not use `force=true` unless explicitly requested.
