# Publish Daily Issue workflow

`Publish Daily Issue` is the one-button editorial workflow for a new Daily Signal issue.

It replaces the split manual chain:

```text
Import Daily Signal → GitHub Pages deploy → Publish Telegram announcement
```

with one GitHub Actions run.

## Where to run it

```text
GitHub → Actions → Publish Daily Issue → Run workflow
```

## Inputs

```text
date: 2026-05-15
issue: 002
signal_text: paste the full import-compatible Daily Signal markdown
lang: uk
max_items: 7
send_telegram: true
force_issue: false
force_telegram: false
```

## What it does

The workflow:

1. writes the pasted Daily Signal to `drafts/daily_signal_input.md`;
2. imports it into `issues/YYYY-MM-DD.json`;
3. runs `python -m pytest -q`;
4. builds the static site with `build_site.py`;
5. commits the new issue and rebuilt `dist/`;
6. renders a Telegram announcement;
7. checks `data/telegram_sent.json` to avoid duplicate posts;
8. sends the Telegram post if enabled;
9. records the Telegram send and commits the sent log.

The existing GitHub Pages workflow still deploys the site after the workflow pushes the issue commit.

## Telegram secrets

The workflow uses the same secrets as the manual Telegram workflow:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

## Safety switches

Use `send_telegram: false` to publish the site without posting to Telegram.

Use `force_issue: true` only when you intentionally want to overwrite an existing issue JSON.

Use `force_telegram: true` only when you intentionally want to repost an already-recorded Telegram announcement.

## Required Daily Signal structure

The pasted `signal_text` must use the import-compatible structure documented in:

```text
docs/IMPORT_DAILY_SIGNAL.md
```

If the structure is broken, the importer fails and the workflow does not publish a partial issue.
