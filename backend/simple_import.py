#!/usr/bin/env python
"""
Simple user import script - faster version
Uses pbkdf2 for faster password hashing.
"""
import csv
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def import_users():
    with app.app_context():
        imported = 0
        skipped = 0
        
        print("Reading USER_CREDENTIALS.csv...")
        
        with open('USER_CREDENTIALS.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                username = row['Username'].strip()
                password_plain = row['Password'].strip()
                role = row['Role'].strip()
                balance = float(row['Initial Balance'].replace('₹', '').replace(',', ''))
                
                # Check if user exists
                existing = User.query.filter_by(username=username).first()
                if existing:
                    skipped += 1
                    continue
                
                # Create and hash password (pbkdf2 is faster)
                password_hash = generate_password_hash(password_plain, method='pbkdf2')
                user = User(
                    username=username,
                    password=password_hash,
                    role=role,
                    balance=balance
                )
                db.session.add(user)
                imported += 1
                
                # Commit every 10 for progress
                if i % 10 == 0:
                    db.session.commit()
                    print(f"  Added {i} users...")
        
        # Final commit
        db.session.commit()
        
        total = User.query.count()
        print(f"\nDone!")
        print(f"  Imported: {imported}")
        print(f"  Skipped: {skipped}")
        print(f"  Total in DB: {total}")
        
        # Show sample
        if total > 0:
            print(f"\nFirst 3 users:")
            for u in User.query.order_by(User.id).limit(3).all():
                print(f"  Login: {u.username} / Password: user_{u.id:03d} / Balance: ₹{u.balance:,.2f}")

if __name__ == '__main__':
    import_users()
