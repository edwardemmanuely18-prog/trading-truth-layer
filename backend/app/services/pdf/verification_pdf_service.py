from io import BytesIO


def build_verification_pdf(
    workspace_id,
    db,
):
    buffer = BytesIO()
    return buffer, "verification.pdf"