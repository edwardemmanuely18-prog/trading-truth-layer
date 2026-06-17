import xml.etree.ElementTree as ET


class IBKRFlexImporter:

    def parse(
        self,
        xml_text: str,
    ):

        root = ET.fromstring(
            xml_text
        )

        trades = []

        positions = []

        for trade in root.findall(
            ".//Trade"
        ):

            trades.append(
                {
                    "broker": "ibkr",

                    "account_id": trade.attrib.get(
                        "accountId"
                    ),

                    "symbol": trade.attrib.get(
                        "symbol"
                    ),

                    "side": trade.attrib.get(
                        "buySell"
                    ),

                    "trade_id": trade.attrib.get(
                        "tradeID"
                    ),

                    "executed_at": trade.attrib.get(
                        "dateTime"
                    ),

                    "currency": trade.attrib.get(
                        "currency"
                    ),

                    "asset_class": trade.attrib.get(
                        "assetCategory"
                    ),

                    "broker_order_type": trade.attrib.get(
                        "orderType"
                    ),

                    "broker_exchange": trade.attrib.get(
                        "exchange"
                    ),

                    "broker_conid": trade.attrib.get(
                        "conid"
                    ),

                    "isin": trade.attrib.get(
                        "isin"
                    ),

                    "net_cash": float(
                        trade.attrib.get(
                            "netCash",
                            0,
                        )
                    ),

                    "proceeds": float(
                        trade.attrib.get(
                            "proceeds",
                            0,
                        )
                    ),
                }
            )

        for position in root.findall(
            ".//OpenPosition"
        ):

            positions.append(
                {
                    "broker": "ibkr",

                    "account_id": position.attrib.get(
                        "accountId"
                    ),

                    "symbol": position.attrib.get(
                        "symbol"
                    ),

                    "asset_class": position.attrib.get(
                        "assetCategory"
                    ),

                    "quantity": float(
                        position.attrib.get(
                            "position",
                            0,
                        )
                    ),

                    "avg_cost": float(
                        position.attrib.get(
                            "costBasisPrice",
                            0,
                        )
                    ),

                    "mark_price": float(
                        position.attrib.get(
                            "markPrice",
                            0,
                        )
                    ),

                    "unrealized_pnl": float(
                        position.attrib.get(
                            "fifoPnlUnrealized",
                            0,
                        )
                    ),

                    "position_value": float(
                        position.attrib.get(
                            "positionValue",
                            0,
                        )
                    ),
                }
            )

        return {
            "trades": trades,
            "positions": positions,
        }