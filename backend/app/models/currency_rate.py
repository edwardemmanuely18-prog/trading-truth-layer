from datetime import date
from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
)

from app.core.db import Base


class CurrencyRate(Base):
    """
    Canonical exchange rate model.

    Currency rates are persisted for
    institutional reporting, auditability
    and provider provenance.

    Historical and live rate behaviour is
    determined by the currency services and
    cache policies rather than the database
    model itself.
    """

    __tablename__ = "currency_rates"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    from_currency = Column(
        String,
        nullable=False,
        index=True,
    )

    to_currency = Column(
        String,
        nullable=False,
        index=True,
    )

    exchange_rate = Column(
        Float,
        nullable=False,
    )

    provider = Column(
        String,
        nullable=False,
    )

    rate_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )