from reportlab.platypus import (
    Paragraph,
    Spacer,
)

from app.services.pdf.common.institutional_theme import (
    SECTION_STYLE,
)


def build_section_title(
    title: str,
):
    """
    Standard section heading used by all
    allocator report modules.
    """

    return [
        Paragraph(
            title,
            SECTION_STYLE,
        ),
        Spacer(
            1,
            10,
        ),
    ]