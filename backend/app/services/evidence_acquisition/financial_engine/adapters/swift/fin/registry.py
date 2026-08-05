"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Message Registry
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Dict


@dataclass(frozen=True, slots=True)
class MessageSpecification:

    message_type: str

    category: str

    description: str


class MessageRegistry:

    def __init__(self):

        self._messages: Dict[
            str,
            MessageSpecification,
        ] = {}

    def register(

        self,

        specification: MessageSpecification,

    ) -> None:

        self._messages[
            specification.message_type
        ] = specification

    def specification(

        self,

        message_type: str,

    ) -> MessageSpecification | None:

        return self._messages.get(
            message_type
        )

    def supported_messages(

        self,

    ) -> list[str]:

        return sorted(
            self._messages.keys()
        )

    def supports(
        self,
        message_type: str,
    ) -> bool:

        return (
            message_type
            in self._messages
        )


    def category(
        self,
        message_type: str,
    ) -> str | None:

        specification = self.specification(
            message_type,
        )

        if specification is None:
            return None

        return specification.category


    def description(
        self,
        message_type: str,
    ) -> str | None:

        specification = self.specification(
            message_type,
        )

        if specification is None:
            return None

        return specification.description

    def count(
        self,
    ) -> int:

        return len(
            self._messages
        )


    def statistics(
        self,
    ) -> dict:

        return {

            "supported_messages": self.count(),

            "categories": sorted(

                {

                    specification.category

                    for specification

                    in self._messages.values()

                }

            ),

        }

    def __contains__(
        self,
        message_type: str,
    ) -> bool:

        return self.supports(
            message_type,
        )


    def __len__(
        self,
    ) -> int:

        return self.count()


    def __iter__(
        self,
    ):

        return iter(
            self._messages.values()
        )


FIN_REGISTRY = MessageRegistry()

FIN_REGISTRY.register(

    MessageSpecification(

        "MT760",

        "7",

        "Guarantee / Standby Letter of Credit",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT799",

        "7",

        "Free Format Message",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT767",

        "7",

        "Guarantee Amendment",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT700",

        "7",

        "Issue of Documentary Credit",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT707",

        "7",

        "Amendment to Documentary Credit",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT103",

        "1",

        "Customer Credit Transfer",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT202",

        "2",

        "Financial Institution Transfer",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT940",

        "9",

        "Customer Statement Message",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT950",

        "9",

        "Statement Message",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT535",

        "5",

        "Statement of Holdings",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT536",

        "5",

        "Statement of Transactions",

    )

)

FIN_REGISTRY.register(

    MessageSpecification(

        "MT564",

        "5",

        "Corporate Action Notification",

    )

)

MX_REGISTRY = {

    "pacs.008",

    "pacs.009",

    "camt.052",

    "camt.053",

    "camt.054",

    "pain.001",

    "pain.002",

}


__all__ = [

    "MessageSpecification",

    "MessageRegistry",

    "FIN_REGISTRY",

]