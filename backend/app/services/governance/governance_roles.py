from __future__ import annotations

from enum import StrEnum


class GovernanceRole(StrEnum):

    OWNER = "owner"

    OPERATOR = "operator"

    AUDITOR = "auditor"

    MEMBER = "member"

    @classmethod
    def normalize(
        cls,
        value: str | None,
    ) -> "GovernanceRole":

        if value is None:
            return cls.MEMBER

        normalized = value.strip().lower()

        for role in cls:
            if role.value == normalized:
                return role

        return cls.MEMBER