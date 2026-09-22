from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Decision:
    text_matches: bool
    source_matches: bool
    should_delete: bool
    reason: str


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def decide(
    *,
    content: str,
    placeholder_text: str,
    author_id: int | None,
    webhook_id: int | None,
    application_id: int | None,
    source_author_ids: set[int],
    source_webhook_ids: set[int],
    source_application_ids: set[int],
    allow_text_only_delete: bool,
) -> Decision:
    """Return a conservative deletion decision.

    Exact text is always required. By default, a second source signature is
    also required so a human typing the same sentence is not deleted.
    """
    if content != placeholder_text:
        return Decision(False, False, False, "content does not exactly match")

    configured_guard = bool(
        source_author_ids or source_webhook_ids or source_application_ids
    )

    source_matches = any(
        (
            author_id is not None and author_id in source_author_ids,
            webhook_id is not None and webhook_id in source_webhook_ids,
            application_id is not None
            and application_id in source_application_ids,
        )
    )

    if configured_guard:
        if source_matches:
            return Decision(True, True, True, "exact text + configured source signature")
        return Decision(True, False, False, "text matched but source signature did not")

    if allow_text_only_delete:
        return Decision(
            True, False, True, "exact text match; text-only deletion explicitly enabled"
        )

    return Decision(
        True,
        False,
        False,
        "text matched, but no source signature is configured (safe observe-only fallback)",
    )


def ids_from_raw_message(
    payload: dict[str, Any],
) -> tuple[int | None, int | None, int | None]:
    author = payload.get("author") or {}
    return (
        _as_int(author.get("id")),
        _as_int(payload.get("webhook_id")),
        _as_int(payload.get("application_id")),
    )
