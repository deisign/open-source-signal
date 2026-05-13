# Telegram delivery

`send_telegram.py` sends a prepared `.txt` announcement to a Telegram channel or chat.

## 1. Create a bot

1. Open Telegram and talk to `@BotFather`.
2. Run `/newbot`.
3. Copy the bot token.
4. Add the bot as an administrator to your channel.

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

## 4. Send for real

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

Or pass the chat id explicitly:

```bash
python send_telegram.py \
  --text-file dist/telegram-open-source-signal-2026-05-13.uk.txt \
  --chat-id @your_channel_name \
  --disable-preview
```

Do not commit bot tokens into the repository.
