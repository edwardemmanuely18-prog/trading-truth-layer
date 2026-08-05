"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Exceptions
"""

from __future__ import annotations


class SwiftFINError(Exception):
    """
    Base FIN exception.
    """


class InvalidFINMessage(SwiftFINError):
    """
    Invalid FIN message.
    """


class InvalidBlock(SwiftFINError):
    """
    Invalid FIN block.
    """


class InvalidField(SwiftFINError):
    """
    Invalid FIN field.
    """


class InvalidFormat(SwiftFINError):
    """
    Invalid field format.
    """


class ValidationError(SwiftFINError):
    """
    Validation failure.
    """


class UnsupportedMessageType(SwiftFINError):
    """
    Unsupported MT message.
    """


class UnsupportedBlock(SwiftFINError):
    """
    Unsupported FIN block.
    """


__all__ = [

    "SwiftFINError",

    "InvalidFINMessage",

    "InvalidBlock",

    "InvalidField",

    "InvalidFormat",

    "ValidationError",

    "UnsupportedMessageType",

    "UnsupportedBlock",

]