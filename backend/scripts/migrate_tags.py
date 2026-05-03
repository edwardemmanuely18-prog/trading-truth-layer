from app.core.db import SessionLocal
from app.models.trade import Trade
from app.models.trade_tag import TradeTag
from app.models.trade_tag_map import TradeTagMap

db = SessionLocal()

trades = db.query(Trade).all()

for trade in trades:
    if trade.strategy_tag and trade.strategy_tag.strip():
        tag_name = trade.strategy_tag.strip().lower()

        tag = db.query(TradeTag).filter_by(
            workspace_id=trade.workspace_id,
            name=tag_name
        ).first()

        if not tag:
            tag = TradeTag(
                workspace_id=trade.workspace_id,
                name=tag_name
            )
            db.add(tag)
            db.flush()

        exists = db.query(TradeTagMap).filter_by(
            trade_id=trade.id,
            tag_id=tag.id
        ).first()

        if not exists:
            db.add(TradeTagMap(
                trade_id=trade.id,
                tag_id=tag.id
            ))

db.commit()
print("Migration complete")