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
