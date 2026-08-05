"""
===============================================================================
Universal Evidence Adapter (UEA)
Synchronization Infrastructure
===============================================================================

The synchronization package is responsible for institutional evidence
synchronization inside the Trading Truth Layer (TTL).

It does NOT communicate with brokers.

Broker communication belongs to the Desktop Trading Engine.

Responsibilities

    • Receive standardized broker evidence
    • Buffer evidence
    • Register evidence
    • Detect duplicates
    • Build provenance
    • Canonicalize evidence
    • Publish canonical evidence
    • Orchestrate synchronization

Consumers

    • Trading Verification System (TVS)
    • Institutional Investigation Service (IIS)
    • Evidence Graph
    • Claim Engine
"""

from .evidence_buffer import EvidenceBuffer
from .evidence_registry import EvidenceRegistry
from .deduplicator import EvidenceDeduplicator
from .provenance_builder import ProvenanceBuilder
from .canonicalizer import EvidenceCanonicalizer
from .publisher import EvidencePublisher
from .synchronizer import EvidenceSynchronizer

__all__ = [
    "EvidenceBuffer",
    "EvidenceRegistry",
    "EvidenceDeduplicator",
    "ProvenanceBuilder",
    "EvidenceCanonicalizer",
    "EvidencePublisher",
    "EvidenceSynchronizer",
]