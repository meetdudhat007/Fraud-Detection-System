import urllib.request
import json

login_data = json.dumps({"username":"admin", "password":"admin123"}).encode('utf-8')
req = urllib.request.Request("http://localhost:5000/api/auth/login", data=login_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            print("Login failed!", resp.read().decode())
            exit(1)
        body = json.loads(resp.read().decode())
        token = body["token"]
        print("login response", body)
except Exception as e:
    print("Login error:", getattr(e, 'read', lambda: b'()')().decode())
    exit(1)

# Create a transaction
# for demonstration assume receiver id 2 exists (default user)
# you may need to adjust if different
receiver_id = 2

data = json.dumps({
    "type": "TRANSFER",
    "amount": 500.0,
    "receiver_id": receiver_id
}).encode('utf-8')

txn_req = urllib.request.Request("http://localhost:5000/api/transactions", data=data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
})

try:
    with urllib.request.urlopen(txn_req) as txn_resp:
        print("Status Code:", txn_resp.status)
        print("Response:", txn_resp.read().decode())
except urllib.error.HTTPError as e:
    print("Transaction error:", e.code, e.read().decode())
