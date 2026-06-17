import xml.etree.ElementTree as ET


def parse_flex(xml_text):

    root = ET.fromstring(xml_text)

    trades = []

    for node in root.findall(".//Trade"):

        trades.append(
            {
                "trade_id":
                    node.get("tradeID"),

                "symbol":
                    node.get("symbol"),

                "side":
                    node.get(
                        "buySell"
                    ),

                "quantity":
                    abs(
                        float(
                            node.get(
                                "proceeds",
                                0,
                            )
                        )
                    ),

                "currency":
                    node.get(
                        "currency",
                        "USD",
                    ),

                "executed_at":
                    node.get(
                        "dateTime"
                    ),

                "account_id":
                    node.get(
                        "accountId"
                    ),

                "proceeds":
                    float(
                        node.get(
                            "proceeds",
                            0,
                        )
                    ),

                "net_cash":
                    float(
                        node.get(
                            "netCash",
                            0,
                        )
                    ),
            }
        )

    positions = []

    for node in root.findall(
        ".//OpenPosition"
    ):

        positions.append(
            {
                "symbol":
                    node.get(
                        "symbol"
                    ),

                "quantity":
                    float(
                        node.get(
                            "position",
                            0,
                        )
                    ),

                "avg_cost":
                    float(
                        node.get(
                            "costBasisPrice",
                            0,
                        )
                    ),

                "mark_price":
                    float(
                        node.get(
                            "markPrice",
                            0,
                        )
                    ),

                "unrealized_pnl":
                    float(
                        node.get(
                            "fifoPnlUnrealized",
                            0,
                        )
                    ),
            }
        )

    return trades, positions