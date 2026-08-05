"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Transport Layer
"""

from __future__ import annotations

from dataclasses import dataclass

from .message import FINMessage


@dataclass(slots=True)
class FINTransport:

    message: FINMessage

    @property
    def sender(self):

        if self.message.metadata:

            return self.message.metadata.sender_bic

        return None

    @property
    def receiver(self):

        if self.message.metadata:

            return self.message.metadata.receiver_bic

        return None

    @property
    def message_type(self):

        if self.message.metadata:

            return self.message.metadata.message_type

        return None

    @property
    def priority(self):

        if self.message.metadata:

            return self.message.metadata.priority

        return None

    @property
    def direction(self):

        if self.message.metadata:

            return self.message.metadata.direction

        return None


__all__ = [

    "FINTransport",

]