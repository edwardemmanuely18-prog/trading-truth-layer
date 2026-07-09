def serialize_public_claim(
    schema,
    db,
    issuer_profile=None,
):
    from app.api.routes.claim_schemas import (
        build_claim_list_row,
    )

    return build_claim_list_row(
        schema,
        db,
        issuer_profile=issuer_profile,
    )