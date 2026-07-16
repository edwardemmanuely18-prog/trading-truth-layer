# ============================================================
# FIAT CURRENCIES
# ============================================================

SUPPORTED_FIAT_CURRENCIES = {

    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
    "SEK",
    "NOK",
    "SGD",
    "HKD",
    "CNY",
    "INR",
    "AED",
    "SAR",
    "ZAR",
    "TZS",
    "KES",
    "NGN",

}


# ============================================================
# ASSET DENOMINATED CURRENCIES
# ============================================================

SUPPORTED_ASSET_CURRENCIES = {

    "BTC",
    "ETH",
    "SOL",
    "USDT",
    "USDC",
    "XAU",
    "XAG",

}


# ============================================================
# VALIDATION HELPERS
# ============================================================

def is_supported_currency(
    currency: str,
) -> bool:

    currency = currency.upper()

    return (

        currency in SUPPORTED_FIAT_CURRENCIES

        or

        currency in SUPPORTED_ASSET_CURRENCIES

    )


def is_fiat_currency(
    currency: str,
) -> bool:

    return (

        currency.upper()

        in

        SUPPORTED_FIAT_CURRENCIES

    )


def is_asset_currency(
    currency: str,
) -> bool:

    return (

        currency.upper()

        in

        SUPPORTED_ASSET_CURRENCIES

    )