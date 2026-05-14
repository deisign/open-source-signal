# Import Daily Signal into an issue JSON

`import_daily_signal.py` converts a structured Daily Signal markdown/text file into a complete issue JSON file.

This removes the need to fill `issues/YYYY-MM-DD.json` by hand.

## Expected input format

Each item should use this structure:

```markdown
## 1. Rubric English / Рубрика українською

### EN — English title

**Source:** Source name, date — [link](https://example.org/article)

**What happened:** ...

**Why it matters:** ...

**How to use it:** ...

**Limits:** ...

**Tags:** `tag-one`, `tag-two`

### UK — Український заголовок

**Джерело:** Назва джерела, дата — [посилання](https://example.org/article)

**Що сталося:** ...

**Чому це важливо:** ...

**Як це застосувати:** ...

**Обмеження:** ...

**Теги:** `тег`, `інший-тег`
```

Internal notes can remain at the end:

```markdown
# EDITORIAL NOTES — INTERNAL

- Note one.
- Note two.
```

They will be preserved in JSON as `internal_notes`, but the public HTML template does not render them.

## Local import

Save the Daily Signal text as:

```text
drafts/daily_signal_2026-05-15.md
```

Then run:

```bash
python import_daily_signal.py drafts/daily_signal_2026-05-15.md \
  --date 2026-05-15 \
  --issue 002 \
  --out issues
```

Build and test:

```bash
python -m pytest -q
python build_site.py
```

Commit and push:

```bash
git add issues dist
git commit -m "Import Daily Signal 2026-05-15"
git push
```

## GitHub Actions import

The manual workflow is included:

```text
.github/workflows/import_daily_signal.yml
```

Use it from GitHub:

```text
Actions → Import Daily Signal → Run workflow
```

Inputs:

```text
date: 2026-05-15
issue: 002
signal_text: paste the full Daily Signal markdown/text
force: false
```

The workflow writes the text to `drafts/daily_signal_input.md`, imports it into `issues/YYYY-MM-DD.json`, runs tests, builds the site and commits the resulting issue/pages.

## Limitations

The importer expects the agreed Daily Signal structure. It is intentionally strict: if a card lacks EN/UK sections or required fields, it fails instead of producing a broken public issue.

For source URLs, use markdown links or plain URLs in the `Source` / `Джерело` line. Citation markers copied from ChatGPT are not reliable as machine-readable URLs.
