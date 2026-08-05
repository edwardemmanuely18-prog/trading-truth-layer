"""
===============================================================================
Universal Evidence Adapter (UEA)
Transport Layer
===============================================================================

The transport layer defines the canonical transport contracts exchanged
between the Desktop Trading Engine and the Universal Evidence Adapter.

These models are broker-neutral and represent standardized evidence
before canonicalization.

Flow

Desktop Trading Engine
        │
        ▼
RawEvidence
        │
        ▼
Evidence Synchronizer
        │
        ▼
Canonical Evidence

Every supported broker must produce RawEvidence before entering the UEA.
"""

from .raw_metadata import RawMetadata
from .raw_evidence import RawEvidence

__all__ = [
    "RawMetadata",
    "RawEvidence",
]