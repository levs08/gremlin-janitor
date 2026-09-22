# Gremlin Janitor 🧹

I built Gremlin Janitor because a Discord integration kept leaving behind a useless placeholder message:

> Sent a message to guild chat but has not yet linked their Discord account.

It was repetitive, annoying, and exactly the kind of thing that makes me ask, **“How can I eliminate this annoyance?”**

Deleting the message was the easy part. The more interesting problem was figuring out how to delete the *right* message without creating a bot that could cheerfully eat something it shouldn't.

## What it does

Gremlin Janitor watches one configured Discord channel for the exact placeholder text. Before it deletes anything, it can inspect the message through Discord's API and capture the metadata I need to identify where the message actually came from.

The normal progression is:

```text
observe → identify → clean
```

I start it in `observe` mode. It logs what Discord is actually sending, including author, webhook, and application IDs when available. Once I have a source identifier I trust, I can configure that as a guard and switch the Janitor to `clean`.

Then it does the boring part for me.

## Why I built it this way

My first thought could have been:

```text
If message == annoying sentence:
    delete message
```

That would work right up until a person typed the same sentence.

So Gremlin Janitor requires an exact text match **and**, by default, a matching source signature. It supports author, webhook, and application IDs as guards.

If Discord doesn't expose a useful source identifier, there is a text-only fallback, but it has to be deliberately enabled with:

```dotenv
ALLOW_TEXT_ONLY_DELETE=true
```

It is off by default.

That is intentional. If an automation is going to perform a destructive action, I'd rather make the unsafe assumption explicit than hide it in the code.

## How it works

```text
Discord message
      ↓
Is it in the configured channel?
      ↓
Inspect message + optional raw REST payload
      ↓
Does the text match exactly?
      ↓
Does the source match a configured guard?
      ↓
Observe / log ───── or ───── delete + audit
```

I separated the deletion decision from the Discord runtime so I can test the risky part without needing a live Discord connection.

`filters.py` decides whether a message is safe to delete.

`janitor.py` handles Discord events, API inspection, logging, and deletion.

`config.py` keeps configuration and environment handling out of the runtime logic.

## Built with

- Python 3.10+
- `discord.py`
- `aiohttp`
- Discord REST API
- JSON / JSONL
- `python-dotenv`
- PowerShell
- pytest
- Docker

## A few guardrails

Gremlin Janitor:

- watches only one configured channel;
- requires the placeholder text to match exactly;
- does not delete on text alone unless I explicitly allow it;
- starts in `MODE=observe`;
- uses minimal Discord gateway intents;
- keeps the bot token in a local `.env`, not in source;
- keeps runtime logs out of Git;
- records deletion decisions so I can see what it did and why.

The goal isn't to make a tiny Discord bot look like a mission-critical enterprise platform. It's to make a small automation behave responsibly.

## Setup

Copy `.env.example` to `.env` and add the bot token and target channel:

```dotenv
DISCORD_BOT_TOKEN=...
TARGET_CHANNEL_ID=...
MODE=observe
```

After observing the integration, add any source IDs that reliably identify its messages:

```dotenv
SOURCE_AUTHOR_IDS=
SOURCE_WEBHOOK_IDS=
SOURCE_APPLICATION_IDS=
```

When the match criteria look right:

```dotenv
MODE=clean
```

### Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_windows.ps1
.\run_windows.ps1
```

### Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

or:

```bash
python -m pytest
```

### Docker

```bash
docker build -t gremlin-janitor .
docker run --env-file .env gremlin-janitor
```

## Logs

Depending on configuration, the Janitor writes JSONL records to `logs/`:

- `messages.jsonl` — normalized messages from the target channel
- `raw_messages.jsonl` — raw REST responses used while investigating source metadata
- `placeholder_candidates.jsonl` — messages that matched the placeholder text and the resulting decision
- `deletions.jsonl` — what was deleted and why

The entire directory is ignored by Git because real message content and Discord IDs do not belong in a public repository.

## Where AI fit

I used AI while building Gremlin Janitor the same way I use it in other technical work: to help me research unfamiliar API behavior, work through implementation options, review and troubleshoot code, and get from an idea to something testable faster.

It did not decide what the automation should do.

The problem, operating rules, safety decisions, testing, and final judgment were mine. I knew the outcome I wanted: **make the gremlin disappear without creating a bigger gremlin.**

And now I don't have to clean it up by hand.
