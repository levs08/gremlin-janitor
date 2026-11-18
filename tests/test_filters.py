from filters import decide

PLACEHOLDER = (
    "Sent a message to guild chat but has not yet linked their Discord account."
)


def test_nonmatch_is_never_deleted():
    decision = decide(
        content="hello", placeholder_text=PLACEHOLDER, author_id=1,
        webhook_id=None, application_id=None, source_author_ids={1},
        source_webhook_ids=set(), source_application_ids=set(),
        allow_text_only_delete=True,
    )
    assert not decision.should_delete


def test_guarded_source_match_deletes():
    decision = decide(
        content=PLACEHOLDER, placeholder_text=PLACEHOLDER, author_id=42,
        webhook_id=None, application_id=None, source_author_ids={42},
        source_webhook_ids=set(), source_application_ids=set(),
        allow_text_only_delete=False,
    )
    assert decision.should_delete


def test_guarded_source_mismatch_does_not_delete():
    decision = decide(
        content=PLACEHOLDER, placeholder_text=PLACEHOLDER, author_id=7,
        webhook_id=None, application_id=None, source_author_ids={42},
        source_webhook_ids=set(), source_application_ids=set(),
        allow_text_only_delete=False,
    )
    assert not decision.should_delete


def test_text_only_requires_explicit_opt_in():
    decision = decide(
        content=PLACEHOLDER, placeholder_text=PLACEHOLDER, author_id=7,
        webhook_id=None, application_id=None, source_author_ids=set(),
        source_webhook_ids=set(), source_application_ids=set(),
        allow_text_only_delete=False,
    )
    assert not decision.should_delete

    fallback = decide(
        content=PLACEHOLDER, placeholder_text=PLACEHOLDER, author_id=7,
        webhook_id=None, application_id=None, source_author_ids=set(),
        source_webhook_ids=set(), source_application_ids=set(),
        allow_text_only_delete=True,
    )
    assert fallback.should_delete


def test_application_id_guard_handles_multiple_guild_bridge_authors():
    """One integration app can post as many different WoW players."""
    bridge_application_id = 1384671873593512078
    for author_id in (1569045729631010908, 1568656462623019008):
        decision = decide(
            content=PLACEHOLDER,
            placeholder_text=PLACEHOLDER,
            author_id=author_id,
            webhook_id=None,
            application_id=bridge_application_id,
            source_author_ids=set(),
            source_webhook_ids=set(),
            source_application_ids={bridge_application_id},
            allow_text_only_delete=False,
        )
        assert decision.text_matches
        assert decision.source_matches
        assert decision.should_delete


def test_application_guard_rejects_other_apps_and_regular_members():
    bridge_application_id = 1384671873593512078
    for actual_application_id in (None, 987654321012345678):
        decision = decide(
            content=PLACEHOLDER,
            placeholder_text=PLACEHOLDER,
            author_id=42,
            webhook_id=None,
            application_id=actual_application_id,
            source_author_ids=set(),
            source_webhook_ids=set(),
            source_application_ids={bridge_application_id},
            allow_text_only_delete=False,
        )
        assert not decision.source_matches
        assert not decision.should_delete


def test_application_guard_never_deletes_non_placeholder_text():
    bridge_application_id = 1384671873593512078
    decision = decide(
        content="Hello from guild chat",
        placeholder_text=PLACEHOLDER,
        author_id=42,
        webhook_id=None,
        application_id=bridge_application_id,
        source_author_ids=set(),
        source_webhook_ids=set(),
        source_application_ids={bridge_application_id},
        allow_text_only_delete=False,
    )
    assert not decision.text_matches
    assert not decision.should_delete
