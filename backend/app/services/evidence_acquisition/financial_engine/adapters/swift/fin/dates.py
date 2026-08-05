"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Date Utilities
"""

from __future__ import annotations

from datetime import datetime


DATE_FORMAT = "%y%m%d"


def parse_date(

    value: str,

) -> datetime:

    return datetime.strptime(

        value,

        DATE_FORMAT,

    )


def validate_date(

    value: str,

) -> bool:

    try:

        parse_date(value)

        return True

    except ValueError:

        return False


__all__ = [

    "parse_date",

    "validate_date",

]