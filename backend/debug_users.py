#!/usr/bin/env python
"""Check database users and test login"""
from app import app
from models import User
from werkzeug.security import check_password_hash

with app.app_context():
    count = User.query.count()
    print(f"Total users in DB: {count}\n")
    
    if count > 0:
        print("First 10 users:")
        users = User.query.order_by(User.id).limit(10).all()
        for u in users:
            print(f"  ID {u.id}: {u.username} ({u.role}) - Balance: ₹{u.balance:,.2f}")
        
        # Test password for user001
        print("\nPassword verification test:")
        user001 = User.query.filter_by(username='user001').first()
        if user001:
            test_pwd = 'user_001'
            is_valid = check_password_hash(user001.password, test_pwd)
            print(f"  user001 exists: YES")
            print(f"  Password 'user_001' valid: {is_valid}")
            print(f"  Stored hash: {user001.password[:50]}...")
    else:
        print("No users in database. Run bulk_import_users.py")
