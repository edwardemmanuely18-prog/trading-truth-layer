from __future__ import annotations

"""
Trading Truth Layer
Institutional QR Framework

Generates high-quality QR codes suitable for:

• Claim Reports
• Investigation Reports
• Verification Reports
• Allocator Reports
• Due Diligence Reports

Uses PIL + qrcode instead of ReportLab's
native QR implementation to produce much
sharper printable QR codes.
"""

from io import BytesIO

import qrcode

from qrcode.constants import ERROR_CORRECT_H

from PIL import Image

from reportlab.lib.utils import ImageReader

from reportlab.platypus import Image as RLImage

from .institutional_theme import (
    QR_SIZE,
)


# ==========================================================
# SETTINGS
# ==========================================================

QR_BORDER = 4

QR_BOX_SIZE = 12

QR_ERROR_CORRECTION = ERROR_CORRECT_H


# ==========================================================
# QR IMAGE
# ==========================================================


def _generate_qr_image(
    url: str,
) -> Image.Image:

    qr = qrcode.QRCode(

        version=None,

        error_correction=QR_ERROR_CORRECTION,

        box_size=QR_BOX_SIZE,

        border=QR_BORDER,

    )

    qr.add_data(url)

    qr.make(
        fit=True,
    )

    return qr.make_image(

        fill_color="black",

        back_color="white",

    ).convert("RGB")


# ==========================================================
# PUBLIC BUILDER
# ==========================================================


def build_qr(
    url: str,
    size: int = QR_SIZE,
):

    if not url:

        raise ValueError(
            "QR code URL cannot be empty."
        )

    image = _generate_qr_image(
        url,
    )

    buffer = BytesIO()

    image.save(

        buffer,

        format="PNG",

        optimize=True,

    )

    buffer.seek(0)

    return RLImage(

        buffer,

        width=size,

        height=size,

    )


# ==========================================================
# FUTURE EXTENSIONS
# ==========================================================


def build_qr_with_logo(
    url: str,
    logo_path: str | None = None,
    size: int = QR_SIZE,
):

    """
    Reserved for TTL branded QR codes.

    Future versions will support:

    • TTL logo
    • Partner logos
    • Digital signature
    • Watermark overlay
    """

    return build_qr(
        url,
        size,
    )


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================


def build_institutional_qr(
    url: str,
    size: int = QR_SIZE,
):

    return build_qr(

        url=url,

        size=size,

    )


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "build_qr",

    "build_qr_with_logo",

    "build_institutional_qr",

]