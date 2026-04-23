from flask import request, jsonify
from models import User, Transaction
from database import db
from auth import hash_password, verify_password, generate_token, decode_token
# fraud_model imports pandas and other heavy deps; import lazily
# so that starting the server (e.g. during migrations or tests) is faster.

import functools
from sqlalchemy import func

def register_routes(app, socketio):
    
    def token_required(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):

            print("HEADERS:", request.headers)
            print("AUTH HEADER:", request.headers.get('Authorization'))
            token = None
            auth_header = request.headers.get("Authorization")

            if auth_header:
                        if auth_header.startswith("Bearer "):
                            token = auth_header.split(" ")[1]
                        else:
                            token = auth_header
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            
            data = decode_token(token)
            if isinstance(data, str):
                return jsonify({'message': data}), 401
                
            current_user = User.query.get(int(data['sub']))
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
            return f(current_user, *args, **kwargs)
        return decorated

    def admin_required(f):
        @functools.wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if current_user.role != 'admin':
                return jsonify({'message': 'Admin privilege required.'}), 403
            return f(current_user, *args, **kwargs)
        return decorated

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing data'}), 400
            
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'User already exists'}), 400
            
        role = data.get('role', 'user')
        if role not in ['user', 'admin']:
            role = 'user'
            
        hashed_pw = hash_password(data['password'])
        new_user = User(username=data['username'], password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing data'}), 400
            
        user = User.query.filter_by(username=data['username']).first()
        if not user or not verify_password(data['password'], user.password):
            return jsonify({'message': 'Invalid credentials'}), 401
            
        token = generate_token(user.id, user.role)
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'balance': user.balance
            }
        }), 200

    @app.route('/api/transactions', methods=['POST'])
    @token_required
    def create_transaction(current_user):
        data = request.get_json() or {}

        amount = float(data.get('amount', 0))
        receiver_id = data.get('receiver_id')
        txn_type = data.get('type', 'TRANSFER')

        if receiver_id is None:
            return jsonify({'message': 'Receiver id is required'}), 400
        try:
            receiver_id = int(receiver_id)
        except ValueError:
            return jsonify({'message': 'Invalid receiver id'}), 400

        if receiver_id == current_user.id:
            return jsonify({'message': 'Cannot send to yourself'}), 400

        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'message': 'Receiver not found'}), 404

        # enforce balance rule
        if amount <= 0 or amount > current_user.balance:
            return jsonify({'message': 'Insufficient balance'}), 400

        oldbalanceOrg = current_user.balance
        oldbalanceDest = receiver.balance
        newbalanceOrig = oldbalanceOrg - amount
        newbalanceDest = oldbalanceDest + amount

        # update balances first
        current_user.balance = newbalanceOrig
        receiver.balance = newbalanceDest
        db.session.commit()

        txn_data = {
            'type': txn_type,
            'amount': amount,
            'oldbalanceOrg': oldbalanceOrg,
            'newbalanceOrig': newbalanceOrig,
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,
        }

        # Predict fraud (import lazily to avoid startup delays)
        from fraud_model import predict_fraud
        is_fraud, risk_score, explanations, advanced_metrics = predict_fraud(txn_data)

        new_txn = Transaction(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            type=txn_type,
            amount=amount,
            oldbalanceOrg=oldbalanceOrg,
            newbalanceOrig=newbalanceOrig,
            oldbalanceDest=oldbalanceDest,
            newbalanceDest=newbalanceDest,
            risk_score=risk_score,
            is_fraud=is_fraud,
            advanced_metrics=advanced_metrics
        )
        db.session.add(new_txn)
        db.session.commit()

        txn_dict = new_txn.to_dict()
        txn_dict['explanations'] = explanations
        txn_dict['sender_balance'] = newbalanceOrig

        socketio.emit('new_transaction', txn_dict)
        if is_fraud:
            socketio.emit('fraud_alert', txn_dict)

        return jsonify(txn_dict), 201

    @app.route('/api/transactions', methods=['GET'])
    @token_required
    def get_transactions(current_user):
        if current_user.role == 'admin':
            txns = Transaction.query.order_by(Transaction.created_at.desc()).limit(100).all()
        else:
            # show transactions where user is sender or receiver
            txns = Transaction.query.filter(
                (Transaction.sender_id == current_user.id) |
                (Transaction.receiver_id == current_user.id)
            ).order_by(Transaction.created_at.desc()).all()
        return jsonify([txn.to_dict() for txn in txns]), 200

    # endpoint for retrieving a single transaction (admin only)
    @app.route('/api/transactions/<int:txn_id>', methods=['GET'])
    @admin_required
    def get_transaction(current_user, txn_id):
        txn = Transaction.query.get(txn_id)
        if not txn:
            return jsonify({'message': 'Transaction not found'}), 404
        return jsonify(txn.to_dict()), 200

    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats(current_user):
        total_txns = Transaction.query.count()
        fraud_txns = Transaction.query.filter_by(is_fraud=True).count()
        fraud_percentage = (fraud_txns / total_txns * 100) if total_txns > 0 else 0
        
        # Volume by type
        type_stats = db.session.query(
            Transaction.type, func.count(Transaction.id)
        ).group_by(Transaction.type).all()
        
        # Fraud strictly by type
        fraud_type_stats = db.session.query(
            Transaction.type, func.count(Transaction.id)
        ).filter_by(is_fraud=True).group_by(Transaction.type).all()

        # Recent timeline data (mocked grouping by day placeholder, we just use raw recent for frontend)
        recent_txns = Transaction.query.order_by(Transaction.created_at.desc()).limit(50).all()

        return jsonify({
            'total_transactions': total_txns,
            'fraud_transactions': fraud_txns,
            'fraud_percentage': round(fraud_percentage, 2),
            'by_type': {k: v for k, v in type_stats},
            'fraud_by_type': {k: v for k, v in fraud_type_stats},
            'recent_timeline': [t.to_dict() for t in recent_txns]
        }), 200

    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_all_users(current_user):
        users = User.query.order_by(User.id.desc()).all()
        return jsonify([user.to_dict() for user in users]), 200

    # allow any authenticated user to get a list of other users (for receiver dropdown)
    @app.route('/api/users', methods=['GET'])
    @token_required
    def list_users(current_user):
        users = User.query.filter(User.id != current_user.id).all()
        return jsonify([{'id': u.id, 'username': u.username, 'balance': u.balance} for u in users]), 200

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @admin_required
    def delete_user(current_user, user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Don't allow deleting the default admin for safety
        if user.username == 'admin':
            return jsonify({'message': 'Cannot delete default admin'}), 400

        # Delete all transactions where this user was sender or receiver
        Transaction.query.filter((Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)).delete()
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
