from app import app
from models import User
from werkzeug.security import check_password_hash

c = app.app_context()
c.push()

# Get user001
user = User.query.filter_by(username='user001').first()
print(f'User found: {user is not None}')
if user:
    print(f'Username: {user.username}')
    print(f'Role: {user.role}')
    print(f'Balance: ₹{user.balance}')
    print(f'Password hash exists: {user.password is not None}')
    
    # Test password
    if user.password:
        password_test = check_password_hash(user.password, 'user_001')
        print(f'Password matches "user_001": {password_test}')
    else:
        print('ERROR: No password hash stored!')
else:
    print('ERROR: user001 not found!')
