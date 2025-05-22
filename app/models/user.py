import uuid
from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    preferred_currency = db.Column(db.String(10))
    risk_profile_level = db.Column(db.Integer)
    notification_opt_in = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default="User")  # User, Admin

    def __repr__(self):
        return f"<User {self.email}>"