from typing import Dict, List


# =========================================================
# INSTITUTIONAL STRATEGY CLASSIFICATION MAP
# =========================================================

STRATEGY_MAP: Dict[str, List[str]] = {

    # -----------------------------------------------------
    # METALS / GOLD
    # -----------------------------------------------------
    "gold": [
        "XAUUSD",
        "GLD",
        "GC",
        "GOLD",
        "XAGUSD",
        "SILVER",
        "SI",
    ],

    # -----------------------------------------------------
    # CRYPTO
    # -----------------------------------------------------
    "crypto": [
        "BTCUSD",
        "ETHUSD",
        "SOLUSD",
        "XRPUSD",
        "ADAUSD",
        "DOGEUSD",
        "BTCUSDT",
        "ETHUSDT",
    ],

    # -----------------------------------------------------
    # FOREX
    # -----------------------------------------------------
    "forex": [
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "AUDUSD",
        "NZDUSD",
        "USDCAD",
        "USDCHF",
        "EURJPY",
        "GBPJPY",
        "EURGBP",
    ],

    # -----------------------------------------------------
    # EXOTIC FX
    # -----------------------------------------------------
    "exotic_fx": [
        "USDTRY",
        "USDZAR",
        "USDMXN",
        "EURTRY",
        "USDSEK",
        "USDNOK",
    ],

    # -----------------------------------------------------
    # INDICES
    # -----------------------------------------------------
    "indices": [
        "NAS100",
        "US30",
        "SPX500",
        "GER40",
        "UK100",
        "DJI",
        "NDX",
        "SPY",
        "QQQ",
    ],

    # -----------------------------------------------------
    # EQUITIES
    # -----------------------------------------------------
    "equities": [
        "AAPL",
        "TSLA",
        "META",
        "AMZN",
        "MSFT",
        "NVDA",
        "NFLX",
        "GOOGL",
        "AMD",
        "INTC",
    ],

    # -----------------------------------------------------
    # FUTURES
    # -----------------------------------------------------
    "futures": [
        "ES",
        "NQ",
        "YM",
        "RTY",
        "CL",
        "GC",
        "SI",
        "HG",
        "ZN",
        "ZB",
    ],

    # -----------------------------------------------------
    # COMMODITIES
    # -----------------------------------------------------
    "commodities": [
        "WTI",
        "BRENT",
        "NATGAS",
        "COFFEE",
        "CORN",
        "WHEAT",
        "SOYBEAN",
        "COTTON",
    ],

    # -----------------------------------------------------
    # VOLATILITY
    # -----------------------------------------------------
    "volatility": [
        "VIX",
        "UVXY",
        "SVIX",
    ],

    # -----------------------------------------------------
    # RATES / BONDS
    # -----------------------------------------------------
    "rates": [
        "TLT",
        "IEF",
        "SHY",
        "BUND",
    ],
}


# =========================================================
# SYMBOL CLASSIFICATION
# =========================================================

def classify_symbol(symbol: str | None) -> str:
    """
    Institutional-grade symbol classification engine.

    Returns:
        strategy_tag string
    """

    if not symbol:
        return "unclassified"

    normalized = symbol.strip().upper()

    for strategy, symbols in STRATEGY_MAP.items():
        if normalized in symbols:
            return strategy

    return "unclassified"