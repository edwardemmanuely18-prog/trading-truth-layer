from io import BytesIO


def build_due_diligence_pdf(
    workspace_id,
    db,
):
    buffer = BytesIO()
    return buffer, "due_diligence.pdf"