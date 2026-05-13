# Open Source Signal v0.8

Static generator and publishing toolkit for the bilingual OSINT journal **Open Source Signal / Сигнал відкритих джерел**.

## What it does

The project currently supports six working modes.

### 0. Create a safe draft for the next issue

`create_issue.py` creates an unfinished issue in `drafts/` so it cannot break the published site.

```bash
python create_issue.py --date 2026-05-14 --issue 001
```

When the draft is filled, validate and publish it into `issues/`:

```bash
python create_issue.py --publish drafts/2026-05-14.json
```

Full instructions are in:

```text
docs/ADD_ISSUE.md
```

### 1. Render one issue

`render_issue.py` takes one issue JSON file and renders a standalone HTML issue using `templates/issue.html.j2`.

```bash
python render_issue.py issues/2026-05-13.json --out dist
```

### 2. Build the web front page and archive

`build_site.py` takes all JSON files from `issues/`, renders issue pages into `dist/issues/`, and builds:

```text
dist/index.html
dist/archive.html
dist/issues/open-source-signal-2026-05-13.html
```

Run:

```bash
python build_site.py --issues issues --templates templates --out dist --config site.json
```

### 3. Generate Telegram announcements

`telegram_digest.py` takes the same issue JSON and renders a short Telegram announcement in English or Ukrainian.

```bash
python telegram_digest.py issues/2026-05-13.json \
  --lang uk \
  --url https://deisign.github.io/open-source-signal/issues/open-source-signal-2026-05-13.html \
  --out dist
```

### 4. Send Telegram announcements locally

`send_telegram.py` sends a prepared announcement to a Telegram channel or chat.

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_CHAT_ID="@your_channel_name"

python send_telegram.py \
  --text-file dist/telegram-open-source-signal-2026-05-13.uk.txt \
  --disable-preview
```

Dry run:

```bash
python send_telegram.py \
  --text-file dist/telegram-open-source-signal-2026-05-13.uk.txt \
  --chat-id @your_channel_name \
  --dry-run
```

### 5. Build and deploy through GitHub Pages

The repository-ready GitHub Actions workflow is included:

```text
.github/workflows/pages.yml
```

On every push to `main`, it installs dependencies, runs tests, builds `dist/`, uploads the Pages artifact and deploys it. Manual runs are available from the Actions tab.

Setup instructions are in:

```text
docs/GITHUB_PAGES_SETUP.md
```

### 6. Publish Telegram announcement through GitHub Actions

A manual Telegram workflow is included:

```text
.github/workflows/telegram.yml
```

Add repository secrets:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Then run:

```text
Actions → Publish Telegram announcement → Run workflow
```

The workflow is manual on purpose, so regular rebuild commits do not spam the channel.

Setup instructions are in:

```text
docs/TELEGRAM_SETUP.md
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Test

```bash
python -m pytest -q
```

## Data model

The main editable issue files live in:

```text
issues/
```

Each item contains both English and Ukrainian adapted text:

- rubric / emoji / theme
- source name, date and URL
- what happened
- why it matters
- how to use it
- limits
- tags

Internal editorial notes are stored in `internal_notes` inside issue JSON, but they are **not rendered** on public issue pages.

## Site URL

The public base URL is configured in:

```text
site.json
```

Default:

```text
https://deisign.github.io/open-source-signal
```

The Telegram workflow uses this `base_url` when the manual `issue_url` input is left empty.

## Typography

The HTML templates use:

- Fraunces for the Latin masthead.
- Source Serif 4 for Ukrainian display typography.
- Inter for body text.
- Arimo for rubric labels and field labels such as `What happened`, `Why it matters`, `Що сталося`, `Чому це важливо`.
- JetBrains Mono for technical/meta elements.

## Telegram duplicate protection

The manual Telegram workflow records successful sends in `data/telegram_sent.json`. Re-running the workflow for the same issue/language will not post again unless the `force` input is set to `true`.
