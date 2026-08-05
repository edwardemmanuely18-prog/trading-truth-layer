"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Public Package Interface
"""

from .connectors import (
    BaseConnector,
    ConnectorConfiguration,
    ConnectorFactory,
)

from .engine import (
    DesktopTradingEngine,
    desktop_trading_engine,
)

from .exceptions import (
    ConfigurationError,
    ConnectionError,
    EngineError,
    PackageError,
    ProviderError,
    RegistryError,
    SynchronizationError,
    TranslationError,
    UEAError,
    UnsupportedProviderError,
    ValidationError,
)

from .models import (
    ActivityEvidence,
    AccountEvidence,
    BalanceEvidence,
    BrokerEvidence,
    BuyingPowerEvidence,
    DealEvidence,
    DesktopEvidencePackage,
    EquityEvidence,
    Evidence,
    EvidenceIdentity,
    EvidenceMetadata,
    EvidenceProvenance,
    ExecutionEvidence,
    FinancialEvidence,
    HistoryEvidence,
    InfrastructureEvidence,
    MarginEvidence,
    MarketEvidence,
    OrderEvidence,
    PositionEvidence,
    PriceEvidence,
    PricedEvidence,
    ServerEvidence,
    SymbolEvidence,
    TerminalEvidence,
    TimeStampedEvidence,
    TradeEvidence,
    UserEvidence,
)

from .registry import (
    ProviderDescriptor,
    ProviderRegistry,
    provider_registry,
)

from .synchronizer import (
    BatchSynchronizer,
    DesktopSynchronizer,
    SynchronizationSession,
)

from .translators import (
    BaseTranslator,
    TranslationContext,
    TranslationHelper,
    TranslationPipeline,
)

from .validators import (
    is_valid_evidence,
    is_valid_package,
    validate_collection,
    validate_evidence,
    validate_identity,
    validate_metadata,
    validate_package,
    validate_provenance,
)


__version__ = "1.0.0"

__author__ = "Trading Truth Layer"

__all__ = [
    # Engine
    "DesktopTradingEngine",
    "desktop_trading_engine",

    # Registry
    "ProviderDescriptor",
    "ProviderRegistry",
    "provider_registry",

    # Connectors
    "BaseConnector",
    "ConnectorConfiguration",
    "ConnectorFactory",

    # Synchronization
    "SynchronizationSession",
    "DesktopSynchronizer",
    "BatchSynchronizer",

    # Translation
    "BaseTranslator",
    "TranslationContext",
    "TranslationHelper",
    "TranslationPipeline",

    # Validation
    "validate_identity",
    "validate_metadata",
    "validate_provenance",
    "validate_evidence",
    "validate_collection",
    "validate_package",
    "is_valid_evidence",
    "is_valid_package",

    # Models
    "EvidenceIdentity",
    "EvidenceMetadata",
    "EvidenceProvenance",
    "Evidence",
    "InfrastructureEvidence",
    "FinancialEvidence",
    "MarketEvidence",
    "TimeStampedEvidence",
    "PricedEvidence",
    "TerminalEvidence",
    "UserEvidence",
    "BrokerEvidence",
    "ServerEvidence",
    "AccountEvidence",
    "BalanceEvidence",
    "MarginEvidence",
    "EquityEvidence",
    "BuyingPowerEvidence",
    "SymbolEvidence",
    "PriceEvidence",
    "OrderEvidence",
    "ExecutionEvidence",
    "DealEvidence",
    "TradeEvidence",
    "PositionEvidence",
    "HistoryEvidence",
    "ActivityEvidence",
    "DesktopEvidencePackage",

    # Exceptions
    "UEAError",
    "ConfigurationError",
    "ValidationError",
    "TranslationError",
    "ConnectionError",
    "SynchronizationError",
    "ProviderError",
    "UnsupportedProviderError",
    "PackageError",
    "RegistryError",
    "EngineError",
]