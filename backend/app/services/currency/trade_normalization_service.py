from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.workspace_preferences import (
    WorkspacePreferences,
)

from app.services.currency.currency_rate_cache_service import (
    CurrencyRateCacheService,
)


class TradeNormalizationService:
    """
    Canonical trade currency normalization layer.

    Responsibilities:

        - Normalize Trade.net_pnl.

        - Convert every trade into the
          workspace reporting currency.

        - Preserve all trade metadata.

    This service performs NO performance
    calculations.

    It only normalizes monetary values
    before TPS consumes the trades.
    """

    @staticmethod
    def get_reporting_currency(
        *,
        db: Session,
        workspace_id: int,
    ) -> str:

        preferences = (

            db.query(
                WorkspacePreferences,
            )
            .filter(
                WorkspacePreferences.workspace_id
                == workspace_id
            )
            .first()

        )

        return (

            preferences.currency.upper()

            if preferences

            else "USD"

        )
        

    @staticmethod
    def normalize(
        *,
        db: Session,
        workspace_id: int,
        trades: list[Trade],
    ) -> list[Trade]:

        preferences = (

            db.query(
                WorkspacePreferences,
            )
            .filter(
                WorkspacePreferences.workspace_id
                == workspace_id
            )
            .first()

        )

        #
        # Workspace default.
        #

        reporting_currency = (

            preferences.currency

            if preferences

            else "USD"

        )

        currencies = {

            (
                trade.currency.upper()

                if trade.currency

                else reporting_currency
            )

            for trade in trades

        }

        (
            reporting_currency,
            rate_cache,
        ) = (

            CurrencyRateCacheService.build_rate_cache(

                db=db,

                workspace_id=workspace_id,

                currencies=currencies,

            )

        )

        normalized_trades = []

        for trade in trades:

            normalized_trade = deepcopy(
                trade,
            )

            trade_currency = (

                trade.currency.upper()

                if trade.currency

                else reporting_currency

            )

            #
            # Nothing to convert.
            #

            if (

                trade_currency

                ==

                reporting_currency

            ):

                normalized_trades.append(
                    normalized_trade,
                )

                continue

            if trade.net_pnl is not None:

                conversion_rate = rate_cache.get(
                    trade_currency,
                )

                #
                # Missing exchange rate.
                # Preserve the original trade.
                #

                if conversion_rate is None:

                    normalized_trades.append(
                        normalized_trade,
                    )

                    continue

                converted_pnl = (

                    Decimal(
                        str(
                            trade.net_pnl,
                        )
                    )

                    * conversion_rate

                )

                normalized_trade.net_pnl = float(
                    converted_pnl,
                )

            #
            # Canonical reporting currency.
            #

            normalized_trade.currency = (
                reporting_currency
            )

            normalized_trades.append(
                normalized_trade,
            )

        return normalized_trades