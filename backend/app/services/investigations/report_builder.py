from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from datetime import datetime


class InvestigationReportBuilder:
    """
    Canonical IIS serializer.

    Converts the institutional InvestigationReport into
    transport-safe JSON.

    Every API endpoint should return the output of this
    builder instead of raw dataclasses.
    """

    @classmethod
    def build(cls, report):

        return cls._serialize(report)

    @classmethod
    def _serialize(cls, value):

        if value is None:
            return None

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, datetime):
            return value.isoformat()

        if is_dataclass(value):
            return {
                key: cls._serialize(val)
                for key, val in asdict(value).items()
            }

        if isinstance(value, dict):
            return {
                key: cls._serialize(val)
                for key, val in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                cls._serialize(item)
                for item in value
            ]

        return value