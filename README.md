# Gremlin Janitor 🧹

## What I built

Gremlin Janitor is a small Discord automation that identifies and removes a specific unwanted message created by a chat integration.

## Why

The integration was repeatedly posting a placeholder message when a user had not linked their Discord account. Cleaning those messages up manually was repetitive, so I automated it.

I also did not want the bot deleting a legitimate message just because the text happened to match. I needed to determine what identifying information Discord exposed for the integration before allowing automated deletion.

## What it does

Gremlin Janitor has two modes:

- **Observe** — watches one configured channel and logs message metadata so I can identify a reliable source signature.
- **Clean** — deletes the placeholder only when the message matches the configured criteria.

By default, deletion requires the exact message text plus a configured author, webhook, or application ID. Text-only deletion is available, but has to be explicitly enabled.

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

## How it is structured

- `janitor.py` — Discord events, API inspection, logging, and deletion
- `filters.py` — message matching and deletion rules
- `config.py` — environment and configuration handling
- `tests/` — tests for the deletion logic
- `.env.example` — configuration template

## Running it

Copy `.env.example` to `.env`, add the Discord bot token and target channel ID, and leave the bot in observation mode first.

```dotenv
DISCORD_BOT_TOKEN=...
TARGET_CHANNEL_ID=...
MODE=observe
```

After identifying a reliable source ID, add it to the configuration and change:

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

The bot token, runtime logs, and real Discord IDs are excluded from the repository.
