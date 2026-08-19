"""
Trading Truth Layer (TTL)

Desktop Trading Engine

Desktop Package → Raw Evidence Adapter

This adapter converts a DesktopEvidencePackage into the broker-neutral
RawEvidence transport objects consumed by the Universal Evidence Adapter.

Responsibilities
----------------

• Consume DesktopEvidencePackage
• Produce broker-neutral RawEvidence objects
• Preserve provider metadata
• Preserve synchronization metadata
• Never canonicalize evidence
• Never deduplicate evidence
• Never publish evidence

Those responsibilities remain owned by the
Universal Evidence Adapter.
"""

from __future__ import annotations

from typing import List

from datetime import datetime
from uuid import uuid4

from app.services.universal_evidence_adapter.domain.transport.raw_metadata import (
    RawMetadata,
    SynchronizationInformation,
    ProviderInformation,
    BrokerAccountInformation,
    WorkspaceInformation,
    TransportInformation,
)

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    EvidenceTiming,
    EvidenceType,
    InstrumentInformation,
    ProviderIdentifiers,
    TradingInformation,
)

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    RawEvidence,
)

from app.services.universal_evidence_adapter.domain.transport.raw_metadata_builder import (
    raw_metadata_builder,
)

from .models import (
    DesktopEvidencePackage,
    SynchronizationStatus,
)

from dataclasses import asdict

# ============================================================================
# Desktop Package Raw Evidence Adapter
# ============================================================================


class DesktopPackageRawEvidenceAdapter:
    """
    Converts DesktopEvidencePackage into RawEvidence transport objects.
    """

    def adapt(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:
        """
        Convert the complete desktop evidence package into
        broker-neutral RawEvidence transport objects.
        """

        # --------------------------------------------------------------
        # Synchronization Context
        #
        # The DesktopEvidencePackage owns the canonical synchronization
        # identity for this acquisition cycle.
        #
        # Propagate it into every canonical Desktop evidence object
        # before those objects are serialized into RawEvidence.raw_payload.
        # --------------------------------------------------------------

        package.apply_synchronization_context(
            status=SynchronizationStatus.RUNNING,
        )

        evidence: List[RawEvidence] = []

        evidence.extend(
            self._build_terminal(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_user(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_broker(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_server(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_account(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_balance(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_margin(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_equity(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_buying_power(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_symbols(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_prices(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_orders(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_executions(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_deals(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_trades(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_positions(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_history(
                package,
                workspace_id=workspace_id,
            )
        )
        evidence.extend(
            self._build_activities(
                package,
                workspace_id=workspace_id,
            )
        )

        # --------------------------------------------------------------
        # Canonical synchronization context
        #
        # One DesktopEvidencePackage represents one acquisition cycle.
        # Every RawEvidence emitted from this package must therefore
        # inherit the same synchronization identity.
        # --------------------------------------------------------------

        synchronization_id = package.synchronization_id

        synchronization_session = (
            package.terminal.session_id
            if (
                package.terminal is not None
                and getattr(package.terminal, "session_id", None)
            )
            else str(uuid4())
        )

        synchronization_batch = str(uuid4())

        for sequence, item in enumerate(evidence, start=1):

            item.metadata.synchronization.synchronization_id = (
                synchronization_id
            )

            item.metadata.synchronization.synchronization_session = (
                synchronization_session
            )

            item.metadata.synchronization.synchronization_batch = (
                synchronization_batch
            )

            item.metadata.synchronization.synchronization_sequence = (
                sequence
            )

            item.metadata.synchronization.synchronization_method = (
                "desktop"
            )

            self._finalize_raw_evidence(item)

        return evidence

    # =====================================================================
    # Shared Builders
    # =====================================================================

    def _build_metadata(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> RawMetadata:

        synchronization = SynchronizationInformation(
            synchronization_id=package.synchronization_id,
            synchronization_session="pending",
            synchronization_batch="pending",
            synchronization_sequence=0,
            synchronization_method="desktop",
        )

        provider = ProviderInformation(
            provider_name=package.connector_name,

            provider_platform=(
                package.terminal.identity.platform_name.value
                if package.terminal is not None
                else ""
            ),

            broker_company=(
                package.broker.legal_name
                if package.broker is not None
                else None
            ),

            broker_server=(
                package.server.server_name
                if package.server is not None
                else None
            ),

            provider_version=(
                package.terminal.identity.platform_version
                if package.terminal is not None
                else None
            ),

        )

        account = BrokerAccountInformation(

            broker_account_id=(

                package.account.broker_account_id

                if package.account is not None

                else ""

            ),

            broker_account_name=(

                package.account.account_name

                if package.account is not None

                else None

            ),

            broker_account_type=(

                package.account.account_type

                if package.account is not None

                else None

            ),

            account_state=(

                package.account.account_state.value

                if package.account is not None

                else None

            ),

            account_currency=(

                package.account.currency

                if package.account is not None

                else None

            ),

            leverage=(

                str(package.account.leverage)

                if (
                    package.account is not None
                    and package.account.leverage is not None
                )
                else None

            ),

        )

        workspace = WorkspaceInformation(
            workspace_id=workspace_id,
        )

        transport = TransportInformation(
            desktop_engine_version="1.0.0",
        )

        return RawMetadata(

            synchronization=synchronization,

            provider=provider,

            account=account,

            workspace=workspace,

            transport=transport,

        )


    def _build_provider_ids(
        self,
        *,
        ticket_id: str | None = None,
        order_id: str | None = None,
        deal_id: str | None = None,
        position_id: str | None = None,
        execution_id: str | None = None,
        trade_id: str | None = None,
    ) -> ProviderIdentifiers:

        return ProviderIdentifiers(

            ticket_id=ticket_id,

            order_id=order_id,

            deal_id=deal_id,

            position_id=position_id,

            execution_id=execution_id,

            trade_id=trade_id,

        )


    def _build_instrument(
        self,
    ) -> InstrumentInformation:

        return InstrumentInformation()


    def _build_trading(
        self,
    ) -> TradingInformation:

        return TradingInformation()


    def _build_timing(
        self,
    ) -> EvidenceTiming:

        return EvidenceTiming(

            synchronized_at=datetime.utcnow(),

        )


    def _empty_raw_evidence(
        self,
        *,
        metadata: RawMetadata,
        evidence_type,
    ) -> RawEvidence:

        return RawEvidence(

            evidence_type=evidence_type,

            metadata=metadata,

            provider_ids=self._build_provider_ids(),

            instrument=self._build_instrument(),

            trading=self._build_trading(),

            timing=self._build_timing(),

        )

    def _finalize_raw_evidence(
        self,
        evidence: RawEvidence,
    ) -> RawEvidence:
        """
        Finalize transport integrity for a completed RawEvidence object.

        The evidence payload must be fully populated before its transport
        hashes are calculated.

        Canonical integrity contract:
            payload_hash  = SHA-256(repr(raw_payload))
            evidence_hash = payload_hash
            payload_size  = len(repr(raw_payload).encode("utf-8"))
        """

        payload = evidence.raw_payload

        payload_hash = raw_metadata_builder.hash_payload(
            payload,
        )

        payload_size = raw_metadata_builder.payload_size(
            payload,
        )

        evidence.metadata.transport.payload_hash = payload_hash
        evidence.metadata.transport.evidence_hash = payload_hash
        evidence.metadata.transport.payload_size = payload_size

        return evidence

    # =====================================================================
    # Builders
    # =====================================================================

    def _build_terminal(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        return []

    def _build_user(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        return []

    def _build_broker(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        return []

    def _build_server(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        return []

    def _build_account(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        if package.account is None:
            return []

        metadata = self._build_metadata(
            package,
            workspace_id=workspace_id,
        )

        evidence = self._empty_raw_evidence(
            metadata=metadata,
            evidence_type=EvidenceType.ACCOUNT,
        )

        account = package.account

        metadata.account.broker_account_id = (
            account.broker_account_id or ""
        )

        metadata.account.broker_account_name = (
            account.account_name
        )

        metadata.account.broker_account_type = (
            account.account_type
        )

        metadata.account.account_state = (
            account.account_state.value
        )

        metadata.account.account_currency = (
            account.currency
        )

        metadata.account.leverage = (
            str(account.leverage)
            if account.leverage is not None
            else None
        )

        evidence.raw_payload = asdict(account)

        return [evidence]

    def _build_balance(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        if package.balance is None:
            return []

        metadata = self._build_metadata(
            package,
            workspace_id=workspace_id,
        )

        evidence = self._empty_raw_evidence(
            metadata=metadata,
            evidence_type=EvidenceType.BALANCE,
        )

        balance = package.balance

        evidence.trading.balance = balance.balance
        evidence.trading.equity = balance.equity
        evidence.raw_payload = asdict(balance)

        return [evidence]

    def _build_margin(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        if package.margin is None:
            return []

        metadata = self._build_metadata(
            package,
            workspace_id=workspace_id,
        )

        evidence = self._empty_raw_evidence(
            metadata=metadata,
            evidence_type=EvidenceType.MARGIN,
        )

        margin = package.margin

        evidence.trading.margin = margin.margin_used
        evidence.trading.free_margin = margin.free_margin
        evidence.trading.margin_level = margin.margin_level

        evidence.raw_payload = asdict(margin)

        return [evidence]

    def _build_equity(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        if package.equity is None:
            return []

        metadata = self._build_metadata(
            package,
            workspace_id=workspace_id,
        )

        evidence = self._empty_raw_evidence(
            metadata=metadata,
            evidence_type=EvidenceType.EQUITY,
        )

        equity = package.equity

        evidence.trading.equity = equity.current_equity
        evidence.trading.balance = equity.current_balance
        evidence.trading.profit = equity.net_pnl if hasattr(equity, "net_pnl") else equity.unrealized_profit

        evidence.raw_payload = asdict(equity)

        return [evidence]

    def _build_buying_power(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        if package.buying_power is None:
            return []

        metadata = self._build_metadata(
            package,
            workspace_id=workspace_id,
        )

        evidence = self._empty_raw_evidence(
            metadata=metadata,
            evidence_type=EvidenceType.MARGIN,
        )

        buying_power = package.buying_power

        evidence.trading.free_margin = (
            buying_power.available_margin
        )

        evidence.raw_payload = asdict(buying_power)

        return [evidence]

    def _build_symbols(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for symbol in package.symbols:

            symbol_name = (
                symbol.symbol.strip()
                if isinstance(symbol.symbol, str)
                else symbol.symbol
            )

            # SYMBOL evidence requires a valid instrument identity.
            # Do not emit null or empty symbols into the canonical pipeline.
            if not symbol_name:
                continue

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.SYMBOL,
            )

            raw.instrument.symbol = symbol_name
            raw.instrument.asset_class = symbol.asset_class
            raw.instrument.exchange = symbol.exchange
            raw.instrument.market = symbol.market
            raw.instrument.contract_size = symbol.contract_size
            raw.instrument.point_size = symbol.point_size

            # Stable SYMBOL fingerprint payload.
            #
            # Instrument-defining fields are included.
            # Synchronization/session/timestamp/provenance fields are deliberately
            # excluded so an unchanged instrument does not create a new hash
            # on every synchronization.
            #
            # Stable source scope is included because the current deduplicator
            # keys directly on evidence_hash.
            raw.raw_payload = {
                "scope": {
                    "workspace_id": (
                        metadata.workspace.workspace_id
                    ),
                    "provider_id": (
                        metadata.workspace.provider_id
                    ),
                    "provider_name": (
                        metadata.provider.provider_name
                    ),
                    "provider_platform": (
                        metadata.provider.provider_platform
                    ),
                    "broker_server": (
                        metadata.provider.broker_server
                    ),
                    "broker_account_id": (
                        metadata.account.broker_account_id
                    ),
                },
                "instrument": {
                    "symbol": symbol_name,
                    "asset_class": symbol.asset_class,
                    "exchange": symbol.exchange,
                    "market": symbol.market,
                    "contract_size": symbol.contract_size,
                    "point_size": symbol.point_size,
                },
            }

            evidence.append(raw)

        return evidence

    def _build_prices(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for price in package.prices:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.CUSTOM,
            )

            raw.instrument.symbol = price.symbol
            raw.instrument.asset_class = price.asset_class
            raw.instrument.exchange = price.exchange
            raw.instrument.market = price.market

            raw.custom_fields.update({

                "bid": price.bid,
                "ask": price.ask,
                "last": price.last,
                "open": price.open,
                "high": price.high,
                "low": price.low,
                "close": price.close,
                "spread": price.spread,
                "volume": price.volume,

            })

            raw.raw_payload = asdict(price)

            evidence.append(raw)

        return evidence

    def _build_orders(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for order in package.orders:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.ORDER,
            )

            raw.provider_ids = self._build_provider_ids(
                order_id=order.order_id,
            )

            raw.instrument.symbol = order.symbol
            raw.instrument.asset_class = order.asset_class
            raw.instrument.exchange = order.exchange
            raw.instrument.market = order.market

            raw.trading.side = order.side
            raw.trading.volume = order.quantity
            raw.trading.entry_price = order.price
            raw.trading.stop_loss = order.stop_price
            raw.trading.take_profit = order.limit_price
            raw.trading.commission = order.commission
            raw.trading.swap = order.swap

            raw.timing.created_at = order.created_at
            raw.timing.modified_at = order.updated_at

            raw.raw_payload = asdict(order)

            evidence.append(raw)

        return evidence

    def _build_executions(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for execution in package.executions:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.EXECUTION,
            )

            raw.provider_ids = self._build_provider_ids(
                execution_id=execution.execution_id,
                order_id=execution.order_id,
            )

            raw.instrument.symbol = execution.symbol
            raw.instrument.asset_class = execution.asset_class
            raw.instrument.exchange = execution.exchange
            raw.instrument.market = execution.market

            raw.trading.side = execution.side
            raw.trading.volume = execution.execution_quantity
            raw.trading.entry_price = execution.execution_price
            raw.trading.commission = execution.commission
            raw.trading.fees = execution.fees

            raw.timing.executed_at = execution.execution_time

            raw.raw_payload = asdict(execution)

            evidence.append(raw)

        return evidence

    def _build_deals(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for deal in package.deals:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.DEAL,
            )

            raw.provider_ids = self._build_provider_ids(
                deal_id=deal.deal_id,
                execution_id=deal.execution_id,
                order_id=deal.order_id,
            )

            raw.instrument.symbol = deal.symbol
            raw.instrument.asset_class = deal.asset_class
            raw.instrument.exchange = deal.exchange
            raw.instrument.market = deal.market

            raw.trading.side = deal.side
            raw.trading.side = deal.side
            raw.trading.volume = deal.quantity
            raw.trading.entry_price = deal.price
            raw.trading.profit = deal.realized_pnl
            raw.trading.commission = deal.commission
            raw.trading.swap = deal.swap
            raw.trading.fees = deal.fee

            raw.timing.executed_at = deal.deal_time

            raw.raw_payload = asdict(deal)

            evidence.append(raw)

        return evidence

    def _build_trades(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for trade in package.trades:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.TRADE,
            )

            raw.provider_ids = self._build_provider_ids(
                trade_id=trade.trade_id,
                order_id=trade.order_id,
                position_id=trade.position_id,
                deal_id=trade.deal_id,
            )

            raw.instrument.symbol = trade.symbol
            raw.instrument.asset_class = trade.asset_class
            raw.instrument.exchange = trade.exchange
            raw.instrument.market = trade.market
            raw.instrument.contract_size = trade.contract_size
            raw.instrument.point_size = trade.point_size

            raw.trading.side = trade.side
            raw.trading.volume = trade.volume
            raw.trading.entry_price = trade.entry_price
            raw.trading.exit_price = trade.exit_price
            raw.trading.stop_loss = trade.stop_loss
            raw.trading.take_profit = trade.take_profit
            raw.trading.commission = trade.commission
            raw.trading.swap = trade.swap
            raw.trading.fees = trade.fees
            raw.trading.profit = trade.net_profit

            raw.timing.opened_at = trade.opened_at
            raw.timing.closed_at = trade.closed_at

            raw.raw_payload = asdict(trade)

            evidence.append(raw)

        return evidence

    def _build_positions(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for position in package.positions:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.POSITION,
            )

            raw.provider_ids = self._build_provider_ids(
                position_id=position.position_id,
                trade_id=position.trade_id,
            )

            raw.instrument.symbol = position.symbol
            raw.instrument.asset_class = position.asset_class
            raw.instrument.exchange = position.exchange
            raw.instrument.market = position.market

            #
            # PositionEvidence no longer owns instrument
            # sizing information.
            #
            # Contract specifications belong to SymbolEvidence.
            #

            raw.trading.side = position.side

            # Position sizing
            raw.trading.volume = position.quantity

            # Position pricing
            raw.trading.entry_price = position.open_price
            raw.trading.exit_price = position.current_price

            # Risk
            raw.trading.stop_loss = position.stop_loss
            raw.trading.take_profit = position.take_profit

            # Current floating PnL
            raw.trading.profit = position.unrealized_pnl

            raw.custom_fields.update(
                {
                    "position_status": position.position_status,
                    "realized_pnl": position.realized_pnl,
                    "gross_pnl": position.gross_pnl,
                    "net_pnl": position.net_pnl,
                    "margin_used": position.margin_used,
                    "exposure": position.exposure,
                    "overnight_swap": position.overnight_swap,
                    "liquidation_price": position.liquidation_price,
                    "risk_percentage": position.risk_percentage,
                    "account_exposure_pct": position.account_exposure_pct,
                    "floating_drawdown": position.floating_drawdown,
                    "highest_profit": position.highest_profit,
                    "maximum_drawdown": position.maximum_drawdown,
                    "hedge_group": position.hedge_group,
                }
            )

            raw.timing.opened_at = (
                position.time
                if hasattr(position, "time")
                else None
            )

            raw.timing.modified_at = (
                position.time_update
                if hasattr(position, "time_update")
                else None
            )

            raw.raw_payload = asdict(position)

            evidence.append(raw)

        return evidence

    def _build_history(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        if package.history is None:
            return []

        metadata = self._build_metadata(
            package,
            workspace_id=workspace_id,
        )

        raw = self._empty_raw_evidence(

            metadata=metadata,

            evidence_type=EvidenceType.HISTORY,

        )

        raw.raw_payload = asdict(package.history)

        return [raw]

    def _build_activities(
        self,
        package: DesktopEvidencePackage,
        *,
        workspace_id: int | None = None,
    ) -> List[RawEvidence]:

        evidence: List[RawEvidence] = []

        for activity in package.activities:

            metadata = self._build_metadata(
                package,
                workspace_id=workspace_id,
            )

            raw = self._empty_raw_evidence(
                metadata=metadata,
                evidence_type=EvidenceType.CUSTOM,
            )

            raw.custom_fields.update(asdict(activity))

            raw.raw_payload = asdict(activity)

            evidence.append(raw)

        return evidence