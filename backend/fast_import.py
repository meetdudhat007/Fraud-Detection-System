#!/usr/bin/env python
"""
Quick user import - use simpler/faster password handling
"""
import csv
from app import app, db
from models import User

def fast_import():
    with app.app_context():
        # Clear all
        print("Clearing database...")
        User.query.delete()
        db.session.commit()
        
        # Import from CSV with FAST password hashing (just use the password as-is for now)
        print("Importing users...")
        imported = 0
        
        with open('USER_CREDENTIALS.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                username = row['Username'].strip()
                password_plain = row['Password'].strip()
                role = row['Role'].strip()
                balance = float(row['Initial Balance'].replace('₹', '').replace(',', ''))
                
                # For speed, use werkzeug's default (faster than pbkdf2)
                from werkzeug.security import generate_password_hash
                try:
                    pwd_hash = generate_password_hash(password_plain)
                except:
                    # If hashing fails, use a simple approach
                    pwd_hash = f"simple:{password_plain}"
                
                user = User(
                    username=username,
                    password=pwd_hash,
                    role=role,
                    balance=balance
                )
                db.session.add(user)
                
                if i % 10 ==0:
                    db.session.commit()
                    print(f"{i} users added...")
        
        db.session.commit()
        total = User.query.count()
        
        print(f"\nImport complete!")
        print(f"Total: {total}")
        print(f"\nUse these credentials to login:")
        for u in User.query.order_by(User.id).limit(5).all():
            pwd = u.password.split('$')[-1][:8] if '$' in u.password else u.password[:20]
            print(f"  Username: {u.username:15} | Password: {u.password.split(':')[-1] if ':' in u.password else 'hashed'}")

if __name__ == '__main__':
    fast_import()
