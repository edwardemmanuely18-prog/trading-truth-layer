from __future__ import annotations

from reportlab.graphics.barcode import (
    createBarcodeDrawing,
)

from .institutional_theme import (
    QR_SIZE,
)


def build_qr(
    url: str,
    size: int = QR_SIZE,
):
    """
    Build an institutional QR code.

    Uses ReportLab's stable barcode API instead
    of the older QrCodeWidget implementation.
    """

    if not url:
        raise ValueError(
            "QR code URL cannot be empty."
        )

    return createBarcodeDrawing(
        "QR",
        value=url,
        width=size,
        height=size,
    )

# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def build_institutional_qr(
    url: str,
    size: int = QR_SIZE,
):
    """
    Backward-compatible wrapper.
    """

    return build_qr(
        url=url,
        size=size,
    )


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "build_qr",

    "build_institutional_qr",

]