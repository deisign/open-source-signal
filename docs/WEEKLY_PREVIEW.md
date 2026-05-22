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


## v1.2.0b — Weekly landing and build integration

Weekly is built as a separate section after the normal Daily build:

```bash
python3 build_site.py --issues issues --templates templates --out dist --config site.json
python3 build_weekly_site.py --weekly weekly --templates templates --out dist --config site.json
```

Generated public files:

```text
dist/weekly/index.html
dist/weekly/open-source-signal-weekly-2026-W20.html
```

The weekly builder also patches the generated homepage and archive with Weekly links and appends Weekly URLs to `sitemap.xml`.

RSS and Telegram integration are intentionally left for later iterations.
