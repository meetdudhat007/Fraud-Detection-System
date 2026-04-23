#!/usr/bin/env python
"""
Export user credentials to CSV file for reference/testing.
Passwords are hashed in DB, so this script just shows username and role.
For demo purposes, we'll show the usernames so you can track which account is which.
"""

from app import app, db
from models import User
import csv
import os

def export_users_csv(filename='user_credentials.csv'):
    """Export all users to a CSV file"""
    with app.app_context():
        users = User.query.order_by(User.id).all()
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['User ID', 'Username', 'Role', 'Balance', 'Created At'])
            
            for user in users:
                writer.writerow([
                    user.id,
                    user.username,
                    user.role,
                    f"{user.balance:.2f}",
                    user.created_at.isoformat()
                ])
        
        print(f"✓ Exported {len(users)} users to {filename}")
        print(f"Location: {filepath}")
        return filepath

def print_users_table(limit=20):
    """Print users in a formatted table"""
    with app.app_context():
        users = User.query.order_by(User.id).limit(limit).all()
        total = User.query.count()
        
        print(f"\n{'ID':<4} {'Username':<25} {'Role':<12} {'Balance':>15} {'Created':<20}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<4} {user.username:<25} {user.role:<12} ₹{user.balance:>13,.2f} {user.created_at.strftime('%Y-%m-%d %H:%M'):<20}")
        
        if total > limit:
            print(f"... and {total - limit} more users")
        
        print(f"\nTotal users: {total}")

if __name__ == '__main__':
    print("User Credentials Export")
    print("=" * 80)
    
    # Print sample
    print_users_table(limit=15)
    
    # Export to CSV
    print("\nExporting to CSV...")
    export_users_csv()
