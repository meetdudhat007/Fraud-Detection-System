from app import app
from models import User

with app.app_context():
    count = User.query.count()
    print(f"Total users: {count}")
    users = User.query.order_by(User.id).all()
    if users:
        print("\nFirst 5:")
        for u in users[:5]:
            print(f"  {u.id} - {u.username} - {u.role} - ₹{u.balance:,.2f}")
