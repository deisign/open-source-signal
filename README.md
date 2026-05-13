# Open Source Signal v0.5

Static prototype and generator for the bilingual OSINT journal **Open Source Signal / Сигнал відкритих джерел**.

## What it does

There are four working build modes.


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

Output:

```text
dist/open-source-signal-2026-05-13.html
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
python telegram_digest.py issues/2026-05-13.json --lang uk --url https://example.org/issues/open-source-signal-2026-05-13.html --out dist
python telegram_digest.py issues/2026-05-13.json --lang en --url https://example.org/issues/open-source-signal-2026-05-13.html --out dist
```

Output:

```text
dist/telegram-open-source-signal-2026-05-13.uk.txt
dist/telegram-open-source-signal-2026-05-13.en.txt
```


### 4. Build and deploy through GitHub Pages

The repository-ready GitHub Actions workflow is included:

```text
.github/workflows/pages.yml
```

On every push to `main`, it installs dependencies, runs tests, builds `dist/`, uploads the Pages artifact and deploys it. Manual runs are available from the Actions tab.

Setup instructions are in:

```text
docs/GITHUB_PAGES_SETUP.md
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

Expected result:

```text
16 passed
```

## Data model

The main editable file is:

```text
issues/2026-05-13.json
```

Each item contains both English and Ukrainian adapted text:

- rubric / emoji / theme
- source name, date and URL
- what happened
- why it matters
- how to use it
- limits
- tags

Internal editorial notes are stored separately in `internal_notes` and rendered only in the clearly marked internal section of the issue page.

## Site structure

```text
open-source-signal-v0.3/
  build_site.py
  create_issue.py
  render_issue.py
  telegram_digest.py
  site.json
  issue.schema.json
  drafts/
    .gitkeep
  issues/
    2026-05-13.json
  templates/
    index.html.j2
    archive.html.j2
    issue.html.j2
  dist/
    telegram-open-source-signal-2026-05-13.uk.txt
    telegram-open-source-signal-2026-05-13.en.txt
    index.html
    archive.html
    issues/
      open-source-signal-2026-05-13.html
  tests/
    test_build_site.py
    test_create_issue.py
    test_render_issue.py
    test_telegram_digest.py
```

## Typography

The HTML templates use:

- Fraunces for the Latin masthead.
- Source Serif 4 for Ukrainian display typography.
- Inter for body text.
- Arimo for rubric labels and field labels such as `What happened`, `Why it matters`, `Що сталося`, `Чому це важливо`.
- JetBrains Mono for technical/meta elements.

## Next step

Use `create_issue.py` and `docs/ADD_ISSUE.md` to add new issues safely. GitHub Pages packaging is included in `.github/workflows/pages.yml`. See `docs/GITHUB_PAGES_SETUP.md` for repository setup and publishing instructions.
