import sys, os
# ensure backend directory is on path regardless of cwd
base = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from app import app
from models import User
from database import db

with app.app_context():
    u = User.query.filter_by(username='admin').first()
    if u:
        u.balance = 1e13
        db.session.commit()
        print('updated admin balance to', u.balance)
    else:
        print('admin user not found')
