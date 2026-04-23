from app import app
from models import Transaction
from datetime import datetime, timezone

c = app.app_context()
c.push()

# Get latest transactions
txns = Transaction.query.order_by(Transaction.id.desc()).limit(5).all()
print(f"Current UTC time: {datetime.now(timezone.utc)}")
print(f"Current local time: {datetime.now()}")
print("\nLatest transactions:")
for txn in txns:
    print(f"ID {txn.id}: created_at = {txn.created_at} (type: {type(txn.created_at)})")
