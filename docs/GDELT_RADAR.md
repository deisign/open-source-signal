# GDELT Radar for Open Source Signal

GDELT Radar is a lead-discovery layer for Open Source Signal / Сигнал відкритих джерел.

It is not an autopublishing system. It collects candidate links from the GDELT DOC 2.0 API, writes local JSONL files, deduplicates them, applies local filters, and produces a shortlist for human editorial review.

The rule is simple:

```text
GDELT lead ≠ publishable source
```

## Pipeline

```text
GDELT API
→ per-pack raw JSONL
→ combined JSONL
→ locally filtered shortlist JSONL
→ locally filtered shortlist Markdown
→ human editorial review
→ Daily Signal issue JSON
```

## Main scripts

```text
scripts/gdelt_radar.py
scripts/gdelt_slow_runner.py
```

`gdelt_radar.py` performs direct GDELT collection for one or more query packs.

`gdelt_slow_runner.py` runs collection slowly, combines results, deduplicates URLs, filters low-value candidates, and writes an editor-friendly shortlist.

## Query packs

Current query packs:

```text
war_crimes_verification
losses_captivity_missing
ukraine_osint_geolocation
ai_verification
platform_watch
```

These correspond to core Open Source Signal rubrics:

```text
War Crimes Verification / Верифікація воєнних злочинів
Losses, Captivity & Missing / Втрати, полон, зниклі
Ukraine Lens / Українська оптика
AI Verification / ШІ та верифікація
Platform Watch / Платформний радар
```

## Normal daily run

Run before preparing a Daily Signal issue:

```bash
cd ~/projects/open-source-signal-v0.4

python3 scripts/gdelt_slow_runner.py \
  --timespan 24h \
  --maxrecords 10 \
  --delay 300 \
  --timeout 90 \
  --retries 1 \
  --backoff 120 \
  --min-score 3 \
  --top 30
```

This produces local generated files under:

```text
data/leads/gdelt/
```

The most important output for editorial work is:

```text
data/leads/gdelt/YYYY-MM-DD-priority-shortlist.md
```

To read it:

```bash
TODAY="$(date +%F)"
sed -n '1,220p' data/leads/gdelt/${TODAY}-priority-shortlist.md
```

## Fast single-pack run

When GDELT is rate-limiting heavily, run only one pack:

```bash
cd ~/projects/open-source-signal-v0.4

python3 scripts/gdelt_slow_runner.py \
  --pack platform_watch \
  --timespan 24h \
  --maxrecords 10 \
  --delay 0 \
  --timeout 90 \
  --retries 0 \
  --min-score 3 \
  --top 30
```

This is useful when we only need a quick platform/disinformation radar check.

## Local filtering without calling GDELT

If a combined JSONL file already exists, filter it locally:

```bash
cd ~/projects/open-source-signal-v0.4

TODAY="$(date +%F)"
IN="data/leads/gdelt/${TODAY}-priority-combined.jsonl"

python3 scripts/gdelt_slow_runner.py \
  --input-jsonl "$IN" \
  --min-score 3 \
  --top 30
```

This does not call the GDELT API.

It rewrites:

```text
data/leads/gdelt/YYYY-MM-DD-priority-shortlist.jsonl
data/leads/gdelt/YYYY-MM-DD-priority-shortlist.md
```

## Output files

Typical generated files:

```text
data/leads/gdelt/YYYY-MM-DD-slow-run/
data/leads/gdelt/YYYY-MM-DD-priority-combined.jsonl
data/leads/gdelt/YYYY-MM-DD-priority-shortlist.jsonl
data/leads/gdelt/YYYY-MM-DD-priority-shortlist.md
```

These files are local working artifacts and are ignored by git.

## Git hygiene

Generated leads are ignored through `.gitignore`:

```text
/data/leads/
/scripts/*.bak.*
```

Do not commit generated GDELT lead files.

Commit only code and documentation changes.

## How to interpret shortlist items

Each shortlist item is a candidate, not a finished editorial source.

A useful item may still need replacement with a stronger source:

```text
GDELT candidate
→ find primary source / stronger publication / original report
→ verify date and claims
→ check against previous issues
→ write Daily Signal card
```

Examples of stronger replacements:

```text
Reuters
AP
Bellingcat
Citizen Lab
The Record
404 Media
official platform blog
official Ukrainian institution
recognized investigative outlet
research report
court / sanctions / prosecution record
```

Low-quality reposts, aggregators, vague blogs and random syndications should normally be used only as pointers.

## Safety rules

Do not publish from GDELT leads when they contain or point to:

```text
private phone numbers
home addresses
family data
passport scans
credential dumps
stolen-data workflows
doxxing calls
revenge calls
live targeting details
air-defense locations
malware execution instructions
```

If a lead points to accusation-heavy material, treat it as a verification pointer only.

For alleged perpetrators, keep status labels precise:

```text
alleged
identified by investigators
sanctioned
charged
convicted
```

For casualty, POW and MIA data, keep status labels precise:

```text
confirmed by open sources
listed by an official project
reported by relatives
statistically estimated
unverified
```

## Rate limits and 429

GDELT may return:

```text
HTTP Error 429: Too Many Requests
```

This is normal.

The current runner handles this by using retries, backoff and slow pack-by-pack execution.

If 429 persists:

```text
1. Stop the run.
2. Wait 30–60 minutes.
3. Run a single pack with --retries 0.
4. Use local filtering on existing combined JSONL if available.
```

Do not repeatedly hammer the API. A frantic woodpecker is not a monitoring strategy.

## Recommended editorial workflow

Daily workflow:

```text
1. Run GDELT slow runner.
2. Open priority-shortlist.md.
3. Mark items as DROP / CHECK / USE-AS-POINTER.
4. Search stronger sources for CHECK items.
5. Check against previous issues for duplicates.
6. Write Daily Signal JSON only from verified or clearly limited sources.
```

GDELT should help discover smoke. It should not be allowed to declare the building legally on fire.

## Test commands

Before committing changes to the GDELT scripts:

```bash
cd ~/projects/open-source-signal-v0.4

python3 scripts/gdelt_radar.py --self-test
python3 scripts/gdelt_slow_runner.py --self-test
git diff --check
```

Expected result:

```text
gdelt_radar.py — OK
gdelt_slow_runner.py — OK
git diff --check — no output
```
