# Gremlin Janitor 🧹

## What I built

Gremlin Janitor is a small Discord bot I built to automatically remove a specific unwanted message created by a chat integration.

## Why I built it

The integration was repeatedly posting a placeholder message when someone had not linked their Discord account. I was cleaning those messages up manually and decided there was no reason to keep doing that by hand.

Before letting a bot delete anything, I needed to know how Discord identified messages coming from the integration. I built the first version to observe those messages and capture the available metadata. Once I had a reliable way to identify them, I added the cleanup step.

## What it does

Gremlin Janitor runs in two modes:

- **Observe** — watches the configured channel allowlist and records message metadata.
- **Clean** — removes the placeholder when both the message and its source match the configured criteria.

It requires an exact text match and, by default, a matching author, webhook, or application ID. There is a text-only option, but it has to be turned on explicitly.


## Kerit Cloud / Pterodactyl deployment

Use the public GitHub repository, branch `main`, `janitor.py` as the **App PY File**, and `requirements.txt` as the requirements file. Keep bot credentials in the server's private `.env` file, **never in GitHub**.

On the Kerit **Files** page, create/edit `.env` using the variables in `.env.example`. Set `TARGET_CHANNEL_IDS` to the specific channels and start with `MODE=observe`. After watching a real placeholder appear, inspect the console's `application=<ID>` value and set:

```dotenv
SOURCE_APPLICATION_IDS=<verified integration application ID>
ALLOW_TEXT_ONLY_DELETE=false
MODE=observe
```

**Validate before deleting:** restart and generate another placeholder from an unlinked player. The console should report `OBSERVE: would delete placeholder`. Test a normal guild message to ensure it is not selected. Confirm the same application ID is used in both target channels.

When the dry run is correct, stop the server, change only `MODE=clean` in `.env`, save it, and start the server. Deletion then requires both the *exact* placeholder sentence **and** a matching authorized source ID, in a configured target channel. Keep `ALLOW_TEXT_ONLY_DELETE=false`.

The Pterodactyl Startup page's **Auto Update** toggle can pull changes from GitHub on restart. Enable it only if you want automatic code updates. A Git pull does **not** update your private `.env`. Do not use reinstall to deploy code changes after you've created `.env` unless you have backed it up, since reinstall can overwrite or remove local files.

The bot needs Discord **Message Content Intent** plus View Channel, Read Message History, and Manage Messages permissions in the monitored channels. Be sure the Discord token is current and private; rotate it immediately if exposed. The bot observes only messages received while connected; it does not sweep historical messages.

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

Copy `.env.example` to `.env` and add the bot token and target channel ID(s).

Start in observation mode:

```dotenv
DISCORD_BOT_TOKEN=...
TARGET_CHANNEL_IDS=123456789012345678,234567890123456789
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

Bot tokens, runtime logs, and real Discord IDs are excluded from the repository. Existing deployments using the legacy `TARGET_CHANNEL_ID` variable remain supported; use `TARGET_CHANNEL_IDS` for one or more comma-separated channels going forward.
