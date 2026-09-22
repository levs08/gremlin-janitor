from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp
import discord

from config import Settings, load_settings
from filters import decide, ids_from_raw_message

API_BASE = "https://discord.com/api/v10"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


class GremlinJanitor(discord.Client):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = False
        intents.presences = False
        intents.typing = False
        super().__init__(intents=intents)
        self.settings = settings
        self.http_session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.http_session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bot {self.settings.token}",
                "User-Agent": "GremlinJanitor/1.0 (safety-first integration cleaner)",
            }
        )

    async def close(self) -> None:
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
        await super().close()

    async def on_ready(self) -> None:
        assert self.user is not None
        channel = self.get_channel(self.settings.target_channel_id)
        logging.info("Logged in as %s (%s)", self.user, self.user.id)
        logging.info("Mode: %s", self.settings.mode.upper())
        logging.info(
            "Target channel: %s (%s)",
            getattr(channel, "name", "not cached / unknown"),
            self.settings.target_channel_id,
        )
        if self.settings.delete_enabled and not (
            self.settings.has_source_guard or self.settings.allow_text_only_delete
        ):
            logging.warning(
                "CLEAN mode is selected, but deletion is SAFEGUARDED OFF until a "
                "source signature is configured or ALLOW_TEXT_ONLY_DELETE=true."
            )

    async def fetch_raw_message(
        self, channel_id: int, message_id: int
    ) -> dict[str, Any] | None:
        if not self.http_session:
            return None
        url = f"{API_BASE}/channels/{channel_id}/messages/{message_id}"
        try:
            async with self.http_session.get(url) as response:
                body = await response.text()
                if response.status != 200:
                    logging.warning(
                        "REST inspect failed HTTP %s: %s", response.status, body[:300]
                    )
                    return None
                return json.loads(body)
        except Exception:
            logging.exception("REST inspect failed")
            return None

    def high_level_snapshot(self, message: discord.Message) -> dict[str, Any]:
        application = getattr(message, "application", None)
        application_id = getattr(application, "id", None)
        return {
            "captured_at": utc_now(),
            "message_id": message.id,
            "guild_id": message.guild.id if message.guild else None,
            "channel_id": message.channel.id,
            "channel_name": getattr(message.channel, "name", None),
            "content": message.content,
            "type": getattr(message.type, "value", str(message.type)),
            "flags": message.flags.value,
            "author": {
                "id": message.author.id,
                "name": str(message.author),
                "display_name": getattr(message.author, "display_name", None),
                "bot": message.author.bot,
                "system": message.author.system,
            },
            "webhook_id": message.webhook_id,
            "application_id": application_id,
            "attachments": [
                {
                    "id": attachment.id,
                    "filename": attachment.filename,
                    "content_type": attachment.content_type,
                    "url": attachment.url,
                }
                for attachment in message.attachments
            ],
            "embeds": [embed.to_dict() for embed in message.embeds],
        }

    async def on_message(self, message: discord.Message) -> None:
        if self.user and message.author.id == self.user.id:
            return
        if message.channel.id != self.settings.target_channel_id:
            return

        snapshot = self.high_level_snapshot(message)
        raw: dict[str, Any] | None = None

        if self.settings.raw_rest_inspect:
            raw = await self.fetch_raw_message(message.channel.id, message.id)
            if raw is not None:
                append_jsonl(
                    self.settings.log_dir / "raw_messages.jsonl",
                    {"captured_at": utc_now(), "payload": raw},
                )

        if self.settings.log_all_target_messages:
            append_jsonl(self.settings.log_dir / "messages.jsonl", snapshot)

        source_payload = raw or {
            "author": {"id": message.author.id},
            "webhook_id": message.webhook_id,
            "application_id": snapshot["application_id"],
        }
        author_id, webhook_id, application_id = ids_from_raw_message(source_payload)

        decision = decide(
            content=message.content,
            placeholder_text=self.settings.placeholder_text,
            author_id=author_id,
            webhook_id=webhook_id,
            application_id=application_id,
            source_author_ids=self.settings.source_author_ids,
            source_webhook_ids=self.settings.source_webhook_ids,
            source_application_ids=self.settings.source_application_ids,
            allow_text_only_delete=self.settings.allow_text_only_delete,
        )

        if decision.text_matches:
            logging.info(
                "Placeholder candidate: id=%s author=%s(%s) webhook=%s "
                "application=%s -> %s",
                message.id, message.author, author_id, webhook_id,
                application_id, decision.reason,
            )
            append_jsonl(
                self.settings.log_dir / "placeholder_candidates.jsonl",
                {
                    **snapshot,
                    "raw_message": raw,
                    "decision": {
                        "text_matches": decision.text_matches,
                        "source_matches": decision.source_matches,
                        "should_delete": decision.should_delete,
                        "reason": decision.reason,
                    },
                },
            )

        if not self.settings.delete_enabled or not decision.should_delete:
            return

        try:
            await message.delete()
            logging.info("Deleted placeholder message %s", message.id)
            append_jsonl(
                self.settings.log_dir / "deletions.jsonl",
                {
                    "deleted_at": utc_now(),
                    "message_id": message.id,
                    "channel_id": message.channel.id,
                    "author_id": author_id,
                    "webhook_id": webhook_id,
                    "application_id": application_id,
                    "reason": decision.reason,
                },
            )
        except discord.Forbidden:
            logging.error(
                "Discord refused deletion. Check View Channel, Read Message History, "
                "and Manage Messages permissions."
            )
        except discord.NotFound:
            logging.info("Message %s was already deleted", message.id)
        except discord.HTTPException:
            logging.exception("Discord API error while deleting message %s", message.id)


async def main() -> None:
    settings = load_settings()
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    client = GremlinJanitor(settings)
    async with client:
        await client.start(settings.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
