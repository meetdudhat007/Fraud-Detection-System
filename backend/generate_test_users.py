#!/usr/bin/env python
"""
Generate bulk test users with login credentials for testing.
Each user gets a simple password: user_<username>_123
"""

import sys
import csv
from werkzeug.security import generate_password_hash

# Simple user generation without flask imports to be fast
def generate_users(count=100, start_balance=50000):
    """Generate user data"""
    users = []
    
    for i in range(1, count + 1):
        username = f"user{i:03d}"
        password = f"user_{username}_123"  # Simple predictable password
        role = "admin" if i == 1 else "user"
        balance = start_balance
        
        users.append({
            'id': i,
            'username': username,
            'password_plain': password,
            'password_hash': generate_password_hash(password),
            'role': role,
            'initial_balance': balance
        })
    
    return users

def export_credentials_csv(users, filename='user_credentials.csv'):
    """Export credentials to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['User ID', 'Username', 'Password', 'Role', 'Initial Balance', 'Notes'])
        
        for user in users:
            notes = "Admin account" if user['role'] == 'admin' else "Test account"
            writer.writerow([
                user['id'],
                user['username'],
                user['password_plain'],
                user['role'],
                f"₹{user['initial_balance']:,.2f}",
                notes
            ])
    
    print(f"✓ Credentials exported to {filename}")
    return filename

def export_import_sql(users, filename='import_users.sql'):
    """Generate SQL INSERT statements"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Insert users into database\n")
        f.write("-- Run this in backend context after connecting to DB\n\n")
        
        for user in users:
            # Escape single quotes in username/password
            username = user['username'].replace("'", "''")
            pwd_hash = user['password_hash'].replace("'", "''")
            
            f.write(f"INSERT INTO users (username, password, role, balance) VALUES ('{username}', '{pwd_hash}', '{user['role']}', {user['initial_balance']});\n")
    
    print(f"✓ SQL import script generated: {filename}")
    return filename

def print_sample(users, num=10):
    """Print sample users"""
    print("\n" + "="*100)
    print(f"SAMPLE USERS (showing first {num} of {len(users)})")
    print("="*100)
    print(f"{'ID':<5} {'Username':<15} {'Password':<25} {'Role':<10} {'Initial Balance':<15}")
    print("-"*100)
    
    for user in users[:num]:
        print(f"{user['id']:<5} {user['username']:<15} {user['password_plain']:<25} {user['role']:<10} ₹{user['initial_balance']:>13,.2f}")
    
    if len(users) > num:
        print(f"... and {len(users) - num} more accounts")
    
    print("="*100 + "\n")

if __name__ == '__main__':
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    print(f"Generating {count} test users...")
    users = generate_users(count=count, start_balance=50000)
    
    print_sample(users, num=15)
    
    # Export to CSV
    export_credentials_csv(users)
    
    # Export SQL
    export_import_sql(users)
    
    print(f"\n✓ Generated {count} users with:")
    print(f"  - Usernames: user001 to user{count:03d}")
    print(f"  - Passwords: user_user<###>_123")
    print(f"  - Initial balance: ₹50,000.00 each")
    print(f"\nFiles created:")
    print(f"  1. user_credentials.csv - All credentials list")
    print(f"  2. import_users.sql - SQL statements to import into DB")
    print(f"\n⚠️  NOTE: To actually add users to database, run from backend context.")
