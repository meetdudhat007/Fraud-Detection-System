#!/usr/bin/env python
"""
Reset users in database - deletes all and reimports from CSV
"""
import csv
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_users():
    with app.app_context():
        # Clear all users
        print("Clearing existing users...")
        count_before = User.query.count()
        User.query.delete()
        db.session.commit()
        print(f"Deleted {count_before} users")
        
        # Import from CSV
        print("\nImporting new users from USER_CREDENTIALS.csv...")
        imported = 0
        
        with open('USER_CREDENTIALS.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                username = row['Username'].strip()
                password_plain = row['Password'].strip()
                role = row['Role'].strip()
                balance = float(row['Initial Balance'].replace('₹', '').replace(',', ''))
                
                # Create and hash password
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
        print(f"  Total in DB: {total}")
        
        # Show sample
        if total > 0:
            print(f"\nTest Login Credentials (first 5):")
            for u in User.query.order_by(User.id).limit(5).all():
                print(f"  Username: {u.username:15s} | Password: {u.password.split('$')[0]:20s} | Balance: ₹{u.balance:>13,.2f}")

if __name__ == '__main__':
    reset_users()
