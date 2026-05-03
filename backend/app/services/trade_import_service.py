from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.trade_tag import TradeTag
from app.models.trade_tag_map import TradeTagMap


def attach_strategy_tag(db: Session, trade: Trade, strategy_name: str | None):
    """
    Ensures:
    - Tag exists
    - Mapping exists
    - No duplicates
    """

    tag_name = strategy_name or "unclassified"

    # 1. get or create tag
    tag = db.query(TradeTag).filter(TradeTag.name == tag_name).first()

    if not tag:
        tag = TradeTag(name=tag_name)
        db.add(tag)
        db.flush()

    # 2. prevent duplicate mapping
    exists = db.query(TradeTagMap).filter(
        TradeTagMap.trade_id == trade.id,
        TradeTagMap.tag_id == tag.id
    ).first()

    if not exists:
        db.add(TradeTagMap(
            trade_id=trade.id,
            tag_id=tag.id
        ))


def create_trade_with_tag(db: Session, trade_data: dict):
    """
    Standardized trade creation pipeline
    """

    strategy_name = trade_data.pop("strategy_tag", None)

    # 1. create trade WITHOUT relying on strategy_tag column
    trade = Trade(**trade_data)
    db.add(trade)
    db.flush()

    # 2. attach tag properly
    attach_strategy_tag(db, trade, strategy_name)

    return trade