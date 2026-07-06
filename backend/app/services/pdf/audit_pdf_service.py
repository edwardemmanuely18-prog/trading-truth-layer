from io import BytesIO


def build_audit_pdf(
    workspace_id,
    db,
):
    buffer = BytesIO()
    return buffer, "audit.pdf"