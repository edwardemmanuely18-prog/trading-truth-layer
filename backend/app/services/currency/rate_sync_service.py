import requests

from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

import xml.etree.ElementTree as ET

from app.models.currency_rate import CurrencyRate


ECB_DAILY_XML_URL = (
    "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
)


class CurrencyRateSyncService:

    @staticmethod
    def sync(
        db: Session,
    ) -> int:

        response = requests.get(
            ECB_DAILY_XML_URL,
            timeout=30,
        )

        response.raise_for_status()

        xml_data = response.text

        print(
            xml_data[:1000],
            flush=True,
        )

        rates = (
            CurrencyRateSyncService
            ._extract_rates(
                xml_data,
            )
        )

        CurrencyRateSyncService._persist_rates(
            db=db,
            rates=rates,
        )

        return len(
            rates,
        )

    @staticmethod
    def _extract_rates(
        xml_data: str,
    ) -> dict[str, Decimal]:

        rates = {

            "EUR": Decimal("1.0"),

        }

        root = ET.fromstring(
            xml_data,
        )

        for element in root.iter():

            currency = element.attrib.get(
                "currency",
            )

            rate = element.attrib.get(
                "rate",
            )

            if currency and rate:

                rates[
                    currency.upper()
                ] = Decimal(
                    rate,
                )

        return rates

    @staticmethod
    def _persist_rates(
        db: Session,
        rates: dict[str, Decimal],
    ) -> None:

        today = datetime.utcnow().date()

        #
        # ECB publishes EUR as the canonical
        # reference currency.
        #
        BASE_CURRENCY = "EUR"

        for currency, rate in rates.items():

            existing = (
                db.query(
                    CurrencyRate,
                )
                .filter(
                    CurrencyRate.from_currency == BASE_CURRENCY,
                    CurrencyRate.to_currency == currency,
                    CurrencyRate.rate_date == today,
                )
                .first()
            )

            if existing:

                existing.exchange_rate = float(
                    rate,
                )

            else:

                db.add(
                    CurrencyRate(

                        from_currency=BASE_CURRENCY,

                        to_currency=currency,

                        exchange_rate=float(
                            rate,
                        ),

                        provider="ECB",

                        rate_date=today,

                    )
                )

        db.commit()