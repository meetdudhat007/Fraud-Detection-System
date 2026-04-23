#!/usr/bin/env python
"""
Bulk insert test users into the database from the CSV file.
Run this from the backend directory while the app context is active.
"""

import csv
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def bulk_import_users(csv_file='USER_CREDENTIALS.csv'):
    """Import users from CSV into database"""
    
    with app.app_context():
        users_added = 0
        users_skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                username = row['Username'].strip()
                password_plain = row['Password'].strip()
                role = row['Role'].strip()
                balance = float(row['Initial Balance'].replace('₹', '').replace(',', ''))
                
                # Check if user already exists
                existing = User.query.filter_by(username=username).first()
                if existing:
                    print(f"⊘ User '{username}' already exists, skipping...")
                    users_skipped += 1
                    continue
                
                # Create new user
                password_hash = generate_password_hash(password_plain)
                user = User(
                    username=username,
                    password=password_hash,
                    role=role,
                    balance=balance
                )
                
                db.session.add(user)
                users_added += 1
                
                if users_added % 10 == 0:
                    print(f"Added {users_added} users...")
        
        # Commit all at once
        db.session.commit()
        
        total = User.query.count()
        print(f"\nDone!")
        print(f"  Added: {users_added} users")
        print(f"  Skipped: {users_skipped}")
        print(f"  Total in DB: {total}")
        
        return users_added, users_skipped

if __name__ == '__main__':
    print("Bulk User Import")
    print("-" * 50)
    bulk_import_users()
