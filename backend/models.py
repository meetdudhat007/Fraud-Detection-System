from database import db
from datetime import datetime, timezone

def utc_now():
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # relationships for sent and received transactions
    sent_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.sender_id',
        backref='sender',
        lazy=True
    )
    received_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.receiver_id',
        backref='receiver',
        lazy=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'balance': self.balance,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    oldbalanceOrg = db.Column(db.Float, nullable=False)
    newbalanceOrig = db.Column(db.Float, nullable=False)
    oldbalanceDest = db.Column(db.Float, nullable=False)
    newbalanceDest = db.Column(db.Float, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    is_fraud = db.Column(db.Boolean, default=False)
    advanced_metrics = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username if hasattr(self, 'sender') and self.sender else None,
            'receiver_id': self.receiver_id,
            'receiver_username': self.receiver.username if hasattr(self, 'receiver') and self.receiver else None,
            'type': self.type,
            'amount': self.amount,
            'oldbalanceOrg': self.oldbalanceOrg,
            'newbalanceOrig': self.newbalanceOrig,
            'oldbalanceDest': self.oldbalanceDest,
            'newbalanceDest': self.newbalanceDest,
            'risk_score': self.risk_score,
            'is_fraud': self.is_fraud,
            'advanced_metrics': self.advanced_metrics,
            'created_at': self.created_at.isoformat()
        }
