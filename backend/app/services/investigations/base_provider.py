from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class InvestigationProvider(ABC):

    """
    Canonical data provider.

    Providers retrieve canonical information
    from TTL.

    Providers NEVER perform investigation.

    Providers NEVER generate findings.

    Providers NEVER generate recommendations.

    Providers NEVER mutate TTL.

    They only expose trusted institutional data.
    """

    name: str = "Unnamed Provider"

    version: str = "1.0"

    priority: int = 100

    enabled: bool = True

    dependencies: tuple[
        str,
        ...
    ] = ()

    @abstractmethod
    def collect(

        self,

        *,

        db: Session,

        workspace_id: int,

    ) -> Any:
        ...

    def validate(

        self,

        payload: Any,

    ) -> None:

        return