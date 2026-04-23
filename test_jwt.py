import sys
sys.path.append('c:/Users/Admin/.gemini/antigravity/scratch/fraud-detection-system/backend')
from auth import generate_token, SECRET_KEY
import jwt

token = generate_token(1, 'admin')
print("Generated:", token)

try:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print("Decoded:", decoded)
except Exception as e:
    print("Exception thrown:", type(e), e)
