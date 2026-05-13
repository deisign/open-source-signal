# GitHub Pages setup

This project is ready to publish through GitHub Pages using GitHub Actions.

## 1. Create the repository

Create a new GitHub repository, for example:

```text
open-source-signal
```

A public repository is the simplest option for GitHub Pages.

## 2. Upload the project

From the project folder:

```bash
git init
git add .
git commit -m "Initial Open Source Signal static generator"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/open-source-signal.git
git push -u origin main
```

Use the HTTPS remote instead of SSH if that is how your GitHub account is configured.

## 3. Enable GitHub Pages from Actions

In the repository:

```text
Settings → Pages → Build and deployment → Source → GitHub Actions
```

The workflow file is already included:

```text
.github/workflows/pages.yml
```

On every push to `main`, it will:

```text
install Python dependencies → run tests → build dist/ → deploy dist/ to GitHub Pages
```

## 4. Expected public URLs

If the repo is named `open-source-signal`, the site will usually appear at:

```text
https://YOUR_USERNAME.github.io/open-source-signal/
```

The first issue page will be:

```text
https://YOUR_USERNAME.github.io/open-source-signal/issues/open-source-signal-2026-05-13.html
```

## 5. Local build check

Before pushing:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python build_site.py --issues issues --templates templates --out dist --config site.json
```

Open:

```text
dist/index.html
```

## 6. Add future issues

Create a new JSON file:

```text
issues/YYYY-MM-DD.json
```

Then run:

```bash
pytest -q
python build_site.py --issues issues --templates templates --out dist --config site.json
```

Commit and push. GitHub Actions will rebuild the archive and publish the new issue.
