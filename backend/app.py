from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from database import db
from routes import register_routes
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# always store the sqlite file next to this module, not depending on the
# current working directory. this prevents "no such column" errors when
# launching from a different folder.
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'fraud_detection.db')

# useful debugging information when starting
logging.info("current working directory: %s", os.getcwd())
logging.info("using database file: %s", db_path)

app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# initialize socketio
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def home():
    return "Fraud Detection API Running"

# Register our API routes
register_routes(app, socketio)

if __name__ == '__main__':
    # log again since the reloader may spawn a new process
    logging.info("[main] cwd=%s", os.getcwd())
    logging.info("[main] db_path=%s", db_path)
    with app.app_context():
        # ensure database schema is up-to-date: when we added sender_id/receiver_id we
        # must drop & recreate existing tables if the old column isn't present. a
        # simple heuristic for development environments.
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if inspector.has_table('transactions'):
            cols = [c['name'] for c in inspector.get_columns('transactions')]
            if 'sender_id' not in cols:
                logging.info("migrating: dropping existing tables due to schema change")
                db.drop_all()
                db.create_all()
        else:
            db.create_all()

        # You can add a default admin user here optionally
        from models import User
        from auth import hash_password
        import random

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=hash_password('admin123'), role='admin', balance=1000000.0)
            db.session.add(admin)
            db.session.commit()
            logging.info("Default admin user created: admin / admin123")
            
        # Add a default standard user
        if not User.query.filter_by(username='user').first():
            user = User(username='user', password=hash_password('user123'), role='user', balance=random.uniform(1000, 50000))
            db.session.add(user)
            db.session.commit()
            logging.info("Default standard user created: user / user123")

        # Add 100 random users
        current_user_count = User.query.count()
        if current_user_count < 100:
            logging.info("Generating 100 random users for testing...")
            for i in range(1, 101):
                username = f"testuser_{i}"
                if not User.query.filter_by(username=username).first():
                    balance = float(f"{random.uniform(100, 100000):.2f}")
                    new_user = User(username=username, password=hash_password('password123'), role='user', balance=balance)
                    db.session.add(new_user)
            db.session.commit()
            logging.info("Generated 100 random users (password: password123).")

    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
