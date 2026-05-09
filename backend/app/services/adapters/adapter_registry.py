from app.services.adapters.csv_adapter import CSVTradeAdapter
from app.services.adapters.mt5_adapter import MT5TradeAdapter
from app.services.adapters.ibkr_adapter import IBKRTradeAdapter


ADAPTER_REGISTRY = {
    "csv": CSVTradeAdapter,
    "mt5": MT5TradeAdapter,
    "ibkr": IBKRTradeAdapter,
}