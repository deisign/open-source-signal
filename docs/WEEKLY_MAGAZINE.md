# Weekly Magazine / Недільний випуск

This is the first Weekly Magazine scaffold for Open Source Signal.

Weekly Magazine is not a mechanical merge of Daily Signal cards. It is an editorial Sunday issue that selects the strongest signals of the week and develops them into a magazine structure.

## Schedule

- Daily Signal: Monday–Friday.
- Saturday: pause / emergency-only.
- Weekly Magazine: Sunday evening.
- On Weekly day, a separate Daily Signal is not needed unless there is an emergency Flash Signal.

## Public structure

1. Editorial note / Редакційна нотатка
2. Signal of the Week
3. Ukraine Lens / Українська оптика
4. War Crimes Verification / Верифікація воєнних злочинів
5. Losses, Captivity & Missing / Втрати, полон, зниклі
6. Tradecraft / Методика
7. Tools / Datasets
8. Risk Watch
9. Reading List

## Current implementation status

v1.2.0 adds the first working template layer:

- `weekly.schema.json`
- `templates/weekly.html.j2`
- `render_weekly.py`
- `tests/test_weekly_template.py`

It does not yet add Weekly issues to the homepage, archive, RSS, sitemap, or Telegram announcements. That integration should come in the next step after the template and schema are stable.

## Render command

```bash
python render_weekly.py drafts/weekly-2026-05-17.json --out dist/weekly
```

The output filename is:

```text
weekly-open-source-signal-YYYY-MM-DD.html
```

where `YYYY-MM-DD` is `week_end_iso`.
