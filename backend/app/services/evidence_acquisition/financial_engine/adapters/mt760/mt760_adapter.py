"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Adapter

Thin orchestration layer for MT760 messages.

Responsibilities
----------------
• Parse MT760 messages
• Validate MT760 messages
• Normalize MT760 messages
• Produce canonical Financial Engine evidence
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Dict

from ..base_adapter import (
    AdapterCapability,
    AdapterDescriptor,
    FinancialAdapter,
)

from .parser import MT760Parser
from .validator import MT760Validator
from .normalizer import (
    MT760Normalizer,
    BankGuaranteeEvidence,
)


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class MT760Configuration:
    """
    MT760 adapter configuration.
    """

    provider_name: str = "SWIFT"

    message_type: str = "MT760"

    version: str = "1.0"


# ============================================================================
# Adapter
# ============================================================================


class MT760Adapter(FinancialAdapter):
    """
    Canonical MT760 adapter.
    """

    def __init__(
        self,
        configuration: MT760Configuration,
    ) -> None:

        super().__init__()

        self.configuration = configuration

        self.parser = MT760Parser()

        self.validator = MT760Validator()

        self.normalizer = MT760Normalizer()

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def descriptor(
        self,
    ) -> AdapterDescriptor:

        return AdapterDescriptor(

            provider=self.configuration.provider_name,

            name="MT760",

            version=self.configuration.version,

            description=(
                "SWIFT MT760 Bank Guarantee Adapter"
            ),
        )

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capability(
        self,
    ) -> AdapterCapability:

        return AdapterCapability(

            acquisition=False,

            synchronization=False,

            streaming=False,

            webhook=False,

            parsing=True,

            validation=True,

            normalization=True,
        )

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def acquire(
        self,
        raw_message: str,
        **kwargs: Dict[str, Any],
    ) -> BankGuaranteeEvidence:

        message = self.parser.parse(
            raw_message,
        )

        validation = self.validator.validate(
            message,
        )

        if not validation.valid:

            raise ValueError(

                "\n".join(validation.errors)
            )

        return self.normalizer.normalize(
            message,
        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "MT760Configuration",

    "MT760Adapter",
]