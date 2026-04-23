#!/usr/bin/env python
"""
Generate user credentials CSV with simple passwords and random balances.
"""
import random
import csv

def generate_credentials(count=100):
    """Generate user credentials with simple passwords and random balances"""
    random.seed(42)
    
    rows = [['ID', 'Username', 'Password', 'Role', 'Initial Balance', 'Notes']]
    
    for i in range(1, count + 1):
        username = f"user{i:03d}"
        password = f"user_{i:03d}"  # Simple format: user_001, user_002, etc.
        role = "admin" if i == 1 else "user"
        # Random balance between ₹10,000 and ₹500,000
        balance = round(random.uniform(10000, 500000), 2)
        notes = "Admin account" if role == "admin" else "Test account"
        
        rows.append([i, username, password, role, f"₹{balance:,.2f}", notes])
    
    return rows

def save_csv(rows, filename='USER_CREDENTIALS.csv'):
    """Save to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"✓ Generated {len(rows)-1} users in {filename}")

if __name__ == '__main__':
    rows = generate_credentials(100)
    save_csv(rows)
    
    # Print sample
    print("\nSample credentials:")
    print(f"{'ID':<5} {'Username':<15} {'Password':<15} {'Role':<10} {'Balance':>15}")
    print("-" * 65)
    for row in rows[1:11]:
        print(f"{row[0]:<5} {row[1]:<15} {row[2]:<15} {row[3]:<10} {row[4]:>15}")
    print("...")
