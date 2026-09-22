from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _ids(name: str) -> set[int]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return set()
    result: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if part:
            result.add(int(part))
    return result


@dataclass(frozen=True)
class Settings:
    token: str
    target_channel_id: int
    mode: str
    placeholder_text: str
    allow_text_only_delete: bool
    source_author_ids: set[int]
    source_webhook_ids: set[int]
    source_application_ids: set[int]
    raw_rest_inspect: bool
    log_all_target_messages: bool
    log_dir: Path

    @property
    def delete_enabled(self) -> bool:
        return self.mode == "clean"

    @property
    def has_source_guard(self) -> bool:
        return bool(
            self.source_author_ids
            or self.source_webhook_ids
            or self.source_application_ids
        )


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    channel = os.getenv("TARGET_CHANNEL_ID", "").strip()
    mode = os.getenv("MODE", "observe").strip().lower()

    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN is missing from .env")
    if not channel:
        raise SystemExit("TARGET_CHANNEL_ID is missing from .env")
    if mode not in {"observe", "clean"}:
        raise SystemExit("MODE must be either 'observe' or 'clean'")

    return Settings(
        token=token,
        target_channel_id=int(channel),
        mode=mode,
        placeholder_text=os.getenv(
            "PLACEHOLDER_TEXT",
            "Sent a message to guild chat but has not yet linked their Discord account.",
        ),
        allow_text_only_delete=_bool("ALLOW_TEXT_ONLY_DELETE", False),
        source_author_ids=_ids("SOURCE_AUTHOR_IDS"),
        source_webhook_ids=_ids("SOURCE_WEBHOOK_IDS"),
        source_application_ids=_ids("SOURCE_APPLICATION_IDS"),
        raw_rest_inspect=_bool("RAW_REST_INSPECT", True),
        log_all_target_messages=_bool("LOG_ALL_TARGET_MESSAGES", True),
        log_dir=Path(os.getenv("LOG_DIR", "logs")),
    )
