# Broker Adapter Framework

## Objective

Separate broker-specific logic from ingestion logic.

Current broker mapping functions:

* map_mt5_row()
* map_ibkr_row()
* map_csv_row()

should eventually become adapters.

---

## Future Structure

services/

brokers/

csv/
adapter.py

mt4/
adapter.py

mt5/
adapter.py

ibkr/
adapter.py

ctrader/
adapter.py

tradestation/
adapter.py

binance/
adapter.py

bybit/
adapter.py

kraken/
adapter.py

---

## Adapter Contract

Adapter Input

Raw source data

Adapter Output

Normalized trade payload

Example

Raw MT5 Export
↓
MT5 Adapter
↓
Normalized Trade

---

## Design Goal

Adding a broker should never require modifying ingestion_service.py.
