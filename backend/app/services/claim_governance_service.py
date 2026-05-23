from app.models.claim_schema import ClaimSchema


PUBLIC_VISIBILITY = "public"
UNLISTED_VISIBILITY = "unlisted"
PRIVATE_VISIBILITY = "private"

DRAFT_STATUS = "draft"
VERIFIED_STATUS = "verified"
PUBLISHED_STATUS = "published"
LOCKED_STATUS = "locked"


def is_claim_verified(schema: ClaimSchema) -> bool:
    return schema.status in [VERIFIED_STATUS, PUBLISHED_STATUS, LOCKED_STATUS]


def is_claim_published(schema: ClaimSchema) -> bool:
    return schema.status in [PUBLISHED_STATUS, LOCKED_STATUS]


def is_claim_locked(schema: ClaimSchema) -> bool:
    return schema.status == LOCKED_STATUS


def can_access_verify_route(schema) -> bool:
    """
    Verify routes are only available for
    institutionally finalized claims.
    """

    if schema.status not in {"published", "locked"}:
        return False

    if schema.visibility not in {"public", "unlisted"}:
        return False

    return True


def can_show_in_public_directory(schema: ClaimSchema) -> bool:
    """
    Public directories should ONLY contain:
    - published/locked
    - public visibility
    """

    if not is_claim_published(schema):
        return False

    return schema.visibility == PUBLIC_VISIBILITY


def can_show_in_profile(schema: ClaimSchema) -> bool:
    """
    Profiles may include:
    - public
    - unlisted

    but only after publication.
    """

    if not is_claim_published(schema):
        return False

    return schema.visibility in [
        PUBLIC_VISIBILITY,
        UNLISTED_VISIBILITY,
    ]


def can_show_in_leaderboard(schema: ClaimSchema) -> bool:
    """
    Leaderboards should only include:
    - public claims
    - locked claims

    because rankings require finalized integrity posture.
    """

    return (
        schema.visibility == PUBLIC_VISIBILITY
        and schema.status == LOCKED_STATUS
    )


def can_embed_claim(schema: ClaimSchema) -> bool:
    """
    Embeds support:
    - public
    - unlisted

    after publication.
    """

    return can_show_in_profile(schema)