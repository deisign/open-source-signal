# Add a new issue

This project now has a safe draft-to-publish flow.

## 1. Create a draft JSON

```bash
python create_issue.py --date 2026-05-14 --issue 001
```

Output:

```text
drafts/2026-05-14.json
```

If `--issue` is omitted, the script reads existing files in `issues/` and uses the next issue number:

```bash
python create_issue.py --date 2026-05-14
```

The draft has complete issue metadata and empty `items` / `internal_notes` arrays. It is stored in `drafts/` so an unfinished issue cannot break the public site build.

## 2. Fill the draft

Copy the finished Daily Signal materials into `drafts/YYYY-MM-DD.json`.

Each item must contain:

```text
theme, emoji, rubric_en, rubric_uk, title_en, title_uk,
source_name, source_url, source_date_label_en, source_date_label_uk,
what_happened_en, what_happened_uk,
why_it_matters_en, why_it_matters_uk,
how_to_use_en, how_to_use_uk,
limits_en, limits_uk,
tags
```

## 3. Publish the completed draft into issues/

```bash
python create_issue.py --publish drafts/2026-05-14.json
```

The command validates the issue before copying it to:

```text
issues/2026-05-14.json
```

If the issue is incomplete, publishing fails and the public site remains untouched.

## 4. Build and test

```bash
python -m pytest -q
python build_site.py
```

## 5. Commit and deploy

```bash
git add .
git commit -m "Add issue 001"
git push
```

GitHub Actions will rebuild and deploy the site.
