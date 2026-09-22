# Gremlin Janitor 🧹

Gremlin Janitor is a safety-first Discord automation for diagnosing and cleaning a specific unwanted integration message.

It was built around a deliberately conservative operating model:

1. **Observe first.** Capture normalized and raw Discord message metadata.
2. **Identify a stable source signature.** Prefer author, webhook, or application IDs over text alone.
3. **Clean only when the evidence is strong enough.** Exact text is always required, and deletion remains disabled by default until a source guard is configured or an explicit text-only fallback is enabled.

This project is intentionally small, but the engineering goal is broader: automate a repetitive operational problem without turning ambiguity into destructive behavior.

## Why this project exists

A linked chat integration was producing an unwanted placeholder message. The challenge was not simply deleting a string. The first problem was discovering **how those integration-generated messages were represented through Discord's API** and whether they exposed a stable identifier that could be used safely.

Gremlin Janitor therefore starts in diagnostic mode and records enough message metadata to answer that question before any cleanup logic is enabled.

## Safety design

- Watches **one configured channel ID only**.
- Requires an **exact text match** for the unwanted placeholder.
- By default, exact text alone is **not enough to delete**.
- Supports author, webhook, and application ID source guards.
- Starts in `MODE=observe`; nothing is deleted until explicitly switched to `MODE=clean`.
- Uses minimal Discord gateway intents.
- Keeps secrets in a local `.env` file that is excluded from Git.
- Separates decision logic from runtime behavior so deletion rules can be unit tested independently.
- Emits structured JSONL logs for diagnosis and auditability.

## Tech stack

Python 3.10+, `discord.py`, `aiohttp`, Discord REST API, JSON/JSONL, `python-dotenv`, PowerShell, pytest, and Docker.

## Architecture

```text
Discord message
    ↓
Target-channel filter
    ↓
High-level + optional raw REST inspection
    ↓
Normalize source identifiers
    ↓
Conservative deletion decision
    ↓
Observe/log  ───────────────┐
                            │
MODE=clean + safe match ────┴──→ Delete + audit log
```

The safety-critical decision logic lives in `filters.py`, separate from Discord I/O in `janitor.py`.

## Configuration

Copy `.env.example` to `.env` and configure:

```dotenv
DISCORD_BOT_TOKEN=...
TARGET_CHANNEL_ID=...
MODE=observe
```

Optional source guards:

```dotenv
SOURCE_AUTHOR_IDS=
SOURCE_WEBHOOK_IDS=
SOURCE_APPLICATION_IDS=
```

If no stable source signature is available, text-only deletion can be enabled explicitly:

```dotenv
ALLOW_TEXT_ONLY_DELETE=true
MODE=clean
```

That fallback is intentionally off by default.

## Windows setup

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_windows.ps1
```

Then edit `.env` and start the bot:

```powershell
.\run_windows.ps1
```

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

or:

```bash
python -m pytest
```

## Docker

```bash
docker build -t gremlin-janitor .
docker run --env-file .env gremlin-janitor
```

## Logs

The bot can write:

- `logs/messages.jsonl` — normalized target-channel messages
- `logs/raw_messages.jsonl` — raw REST payloads
- `logs/placeholder_candidates.jsonl` — exact-text candidates plus the deletion decision
- `logs/deletions.jsonl` — deletion audit records

The `logs/` directory is excluded from Git because message content and IDs may be sensitive.

## What it can and cannot do

It can diagnose how integration-generated messages appear through Discord's API, remove a known placeholder after it appears, prefer stable source metadata over unsafe assumptions, and preserve a structured audit trail.

It cannot recover message content that an upstream system never sends to Discord, prevent Discord from briefly receiving the placeholder before deletion, or guarantee that a client notification was not triggered before deletion.

## AI-assisted development

This project was built with AI-assisted development as a working engineering tool: translating the operational problem into implementation options, reviewing API behavior, iterating on Python logic, developing safety checks and tests, and improving deployment documentation.

AI output was treated as a starting point to inspect and validate, not as an authority. Final behavior, safeguards, and technical decisions remained human-reviewed.

## Repository hygiene

Do not commit `.env`, Discord bot tokens, production logs, or real user, guild, channel, webhook, or application IDs. The included `.gitignore` excludes those local artifacts.
