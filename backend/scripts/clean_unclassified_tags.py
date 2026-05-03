from app.core.db import SessionLocal
from app.models.trade import Trade
from app.models.trade_tag import TradeTag
from app.models.trade_tag_map import TradeTagMap


def run(dry_run=True):
    db = SessionLocal()

    print("🔍 Cleaning 'unclassified' tags...")
    print("DRY RUN:", dry_run)
    print("-" * 50)

    # get unclassified tag id
    unclassified_tag = db.query(TradeTag).filter(
        TradeTag.name == "unclassified"
    ).first()

    if not unclassified_tag:
        print("❌ No 'unclassified' tag found. Nothing to clean.")
        return

    trades = db.query(Trade).all()

    removed_count = 0

    for trade in trades:
        mappings = db.query(TradeTagMap).filter(
            TradeTagMap.trade_id == trade.id
        ).all()

        if not mappings:
            continue

        tag_ids = [m.tag_id for m in mappings]

        # skip if only one tag
        if len(tag_ids) <= 1:
            continue

        # if trade has multiple tags AND one is unclassified → remove it
        if unclassified_tag.id in tag_ids:
            for m in mappings:
                if m.tag_id == unclassified_tag.id:
                    print(f"🧹 Trade {trade.id}: removing 'unclassified'")

                    if not dry_run:
                        db.delete(m)
                        removed_count += 1

    if not dry_run:
        db.commit()
        print(f"\n✅ CLEAN COMPLETE. Removed: {removed_count}")
    else:
        print("\n⚠️ DRY RUN COMPLETE — no changes applied")

    db.close()


if __name__ == "__main__":
    run(dry_run=False)

    # 🔁 Step 2: after verification → switch to False
    # run(dry_run=False)