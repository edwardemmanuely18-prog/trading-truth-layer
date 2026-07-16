from __future__ import annotations

"""
Institutional Investigation Report

Canonical PDF generator for the
Institutional Investigation System (IIS).

This package assembles the Investigation
Report using the shared institutional
PDF framework.
"""

from .generator import (
    generate_investigation_report_pdf,
)

__all__ = [

    "generate_investigation_report_pdf",

]