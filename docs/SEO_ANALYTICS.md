# SEO + analytics foundation

## Generated files

`build_site.py` now generates:

- `dist/sitemap.xml`
- `dist/robots.txt`
- JSON-LD structured data on the homepage, archive and issue pages
- issue-specific meta descriptions based on the first issue items

## GoatCounter

Analytics is configured in `site.json` but disabled by default:

```json
{
  "analytics_provider": "goatcounter",
  "analytics_id": "",
  "analytics_domain": ""
}
```

When `analytics_id` is empty, no analytics script is inserted.

To enable GoatCounter after creating the counter, set:

```json
{
  "analytics_provider": "goatcounter",
  "analytics_id": "YOUR_GOATCOUNTER_CODE"
}
```

This inserts:

```html
<script data-goatcounter="https://YOUR_GOATCOUNTER_CODE.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```

If using a custom GoatCounter domain, set `analytics_domain` to the full `/count` endpoint.

## Checks

After deploy:

- `https://osintsignal.org/sitemap.xml`
- `https://osintsignal.org/robots.txt`
- View source on an issue page and check `application/ld+json`.
