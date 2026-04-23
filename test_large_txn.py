import urllib.request, json

login_data = json.dumps({"username":"admin","password":"admin123"}).encode('utf-8')
req = urllib.request.Request("http://localhost:5000/api/auth/login", data=login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())["token"]

large_amount = 9999999999999.0
print("sending amount", large_amount)
# use receiver id 2 (default normal user)
data = json.dumps({"type": "TRANSFER", "amount": large_amount, "receiver_id": 2}).encode('utf-8')
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
except Exception as e:
    print("Error:", e)
