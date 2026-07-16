from __future__ import annotations

from .permission_matrix import ROLE_CAPABILITIES


class IAMRegistry:

    @staticmethod
    def capabilities_for_role(role: str) -> set[str]:
        return ROLE_CAPABILITIES.get(role.lower(), set())