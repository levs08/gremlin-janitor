# Gremlin Janitor 🧹

## What I built

Gremlin Janitor is a small Discord bot I built to automatically remove a specific unwanted message created by a chat integration.

## Why I built it

The integration was repeatedly posting a placeholder message when someone had not linked their Discord account. I was cleaning those messages up manually and decided there was no reason to keep doing that by hand.

Before letting a bot delete anything, I needed to know how Discord identified messages coming from the integration. I built the first version to observe those messages and capture the available metadata. Once I had a reliable way to identify them, I added the cleanup step.

## What it does

Gremlin Janitor runs in two modes:

- **Observe** — watches one configured channel and records message metadata.
- **Clean** — removes the placeholder when both the message and its source match the configured criteria.

It requires an exact text match and, by default, a matching author, webhook, or application ID. There is a text-only option, but it has to be turned on explicitly.

## Tools I used

- Python
- discord.py
- aiohttp
- Discord REST API
- JSON / JSONL
- python-dotenv
- pytest
- PowerShell
- Docker

## Project files

- `janitor.py` — Discord events, API inspection, logging, and deletion
- `filters.py` — matching and deletion rules
- `config.py` — configuration and environment handling
- `tests/` — tests for the deletion logic
- `.env.example` — configuration template

## Running it

Copy `.env.example` to `.env` and add the bot token and target channel ID.

Start in observation mode:

```dotenv
DISCORD_BOT_TOKEN=...
TARGET_CHANNEL_ID=...
MODE=observe
```

After identifying the source, add the appropriate source ID to the configuration and switch to:

```dotenv
MODE=clean
```

On Windows:

```powershell
.\setup_windows.ps1
.\run_windows.ps1
```

Run the tests with:

```bash
python -m pytest
```

Bot tokens, runtime logs, and real Discord IDs are excluded from the repository.
