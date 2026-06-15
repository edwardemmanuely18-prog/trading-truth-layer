import MetaTrader5 as mt5

mt5.initialize()

print(mt5.history_deals_total())
print(mt5.last_error())

print(mt5.history_orders_total())
print(mt5.last_error())