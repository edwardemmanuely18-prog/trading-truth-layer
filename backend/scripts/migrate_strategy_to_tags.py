from app.core.db import SessionLocal
from app.models.trade import Trade
from app.models.trade_tag import TradeTag
from app.models.trade_tag_map import TradeTagMap

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run():
    db = SessionLocal()

    trades = db.query(Trade).all()

    tag_cache = {}

    for trade in trades:
        tag_name = trade.strategy_tag or "unclassified"

        key = (trade.workspace_id, tag_name)

        if key not in tag_cache:
            tag = db.query(TradeTag).filter(
                TradeTag.workspace_id == trade.workspace_id,
                TradeTag.name == tag_name
            ).first()

            if not tag:
                tag = TradeTag(
                    workspace_id=trade.workspace_id,
                    name=tag_name
                )
                db.add(tag)
                db.flush()

            tag_cache[key] = tag

        tag = tag_cache[key]

        exists = db.query(TradeTagMap).filter(
            TradeTagMap.trade_id == trade.id,
            TradeTagMap.tag_id == tag.id
        ).first()

        if not exists:
            db.add(TradeTagMap(
                trade_id=trade.id,
                tag_id=tag.id
            ))

    db.commit()
    db.close()

    print("✅ Migration completed")


if __name__ == "__main__":
    run()