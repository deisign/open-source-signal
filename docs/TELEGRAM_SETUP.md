# Telegram delivery

`telegram_digest.py` renders a short announcement from an issue JSON file. `send_telegram.py` sends that prepared `.txt` announcement to a Telegram channel or chat.

## 1. Create a bot

1. Open Telegram and talk to `@BotFather`.
2. Run `/newbot`.
3. Copy the bot token.
4. Add the bot as an administrator to your channel.
5. Give the bot the `Post Messages` permission.

Do not commit the bot token into the repository.

## 2. Choose the chat id

For a public channel, use the channel username:

```text
@your_channel_name
```

For a private channel, use its numeric chat id. The easiest practical route is to first test with a public or test channel.

## 3. Local dry run

```bash
python telegram_digest.py issues/2026-05-13.json \
  --lang uk \
  --url https://deisign.github.io/open-source-signal/issues/open-source-signal-2026-05-13.html \
  --out dist

python send_telegram.py \
  --text-file dist/telegram-open-source-signal-2026-05-13.uk.txt \
  --chat-id @your_channel_name \
  --dry-run
```

## 4. Send locally for real

Set secrets in your shell:

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_CHAT_ID="@your_channel_name"
```

Send:

```bash
python send_telegram.py \
  --text-file dist/telegram-open-source-signal-2026-05-13.uk.txt \
  --disable-preview
```

## 5. Send from GitHub Actions

The repository includes a manual workflow:

```text
.github/workflows/telegram.yml
```

Add these repository secrets:

```text
Settings → Secrets and variables → Actions → New repository secret
```

Required secrets:

```text
TELEGRAM_BOT_TOKEN = bot token from BotFather
TELEGRAM_CHAT_ID = @your_channel_name
```

Then run:

```text
Actions → Publish Telegram announcement → Run workflow
```

Inputs:

```text
issue: 2026-05-13.json
lang: uk or en
issue_url: leave empty to use site.json base_url
max_items: 7
```

This workflow is manual on purpose. It should not post to Telegram on every push, because rebuild commits and small fixes would otherwise spam the channel like a bureaucratic trumpet.
