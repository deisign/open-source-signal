# Weekly preview

This is the first isolated Weekly Magazine preview.

It is intentionally not wired into `build_site.py`, RSS, sitemap, or Telegram yet.

Render manually:

```bash
python3 render_weekly.py weekly/open-source-signal-weekly-2026-W20.json --templates templates --out dist/weekly --config site.json
```

Current preview output:

```text
dist/weekly/open-source-signal-weekly-2026-W20.html
```

Next steps:

1. Weekly index.
2. Weekly sitemap integration.
3. Weekly RSS or separate weekly feed.
4. Weekly Telegram announcement.
5. Issue-specific OG images.
