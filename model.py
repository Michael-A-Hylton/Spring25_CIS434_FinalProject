from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    email = db.Column(db.String(120), unique=True, nullable=False)
    two_factor_code = db.Column(db.String(6))
    two_factor_expiry = db.Column(db.DateTime)
    two_factor_attempts = db.Column(db.Integer, default=0)
    two_factor_locked_until = db.Column(db.DateTime)

    public_key = db.Column(db.Text)


    def generate_2fa_code(self):
        self.two_factor_code = f"{secrets.randbelow(1000000):06}"  # 6-digit code
        self.two_factor_expiry = datetime.utcnow() + timedelta(minutes=10)

    def verify_2fa_code(self, code):
        now = datetime.utcnow()
        commit_required = False

        if self.two_factor_locked_until and now < self.two_factor_locked_until:
            return False, "Too many incorrect attempts. Try again later.", commit_required

        if self.two_factor_code == code and self.two_factor_expiry and now < self.two_factor_expiry:
            self.two_factor_attempts = 0
            commit_required = True
            return True, "2FA code verified successfully.", commit_required
        else:
            self.two_factor_attempts += 1
            commit_required = True
            if self.two_factor_attempts >= 5:
                self.two_factor_locked_until = now + timedelta(minutes=5)
                return False, "Too many incorrect attempts. Locked out for 5 minutes.", commit_required
            return False, "Incorrect code. Try again.", commit_required

    def __repr__(self):
        return f'<User {self.username}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.receiver_id}>'
