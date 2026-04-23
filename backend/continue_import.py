#!/usr/bin/env python
"""
Continue import - only add missing users
"""
import csv
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Get existing usernames
    existing = {u.username for u in User.query.all()}
    print(f"Existing users: {len(existing)}")
    
    # Import missing users
    imported = 0
    with open('USER_CREDENTIALS.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['Username'].strip()
            if username in existing:
                continue
            
            password_plain = row['Password'].strip()
            role = row['Role'].strip()
            balance = float(row['Initial Balance'].replace('₹', '').replace(',', ''))
            
            # Use default hashing (faster)
            pwd_hash = generate_password_hash(password_plain)
            user = User(username=username, password=pwd_hash, role=role, balance=balance)
            db.session.add(user)
            imported += 1
            
            if imported % 5 == 0:
                db.session.commit()
                print(f"  Added {imported}...")
    
    db.session.commit()
    total = User.query.count()
    print(f"\nDone! Total: {total}")
    
    # Show all users
    print(f"\nAll users:")
    for u in User.query.all():
        pwd_display = u.password.split(':')[-1] if ':' in u.password else 'hashed'
        print(f"  {u.username:15} | Balance: ₹{u.balance:>13,.2f}")
