from app import db
from app.models.user import User
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

class UserService:

    @staticmethod
    def register_user(data):
        existing = User.query.filter(
            (User.email == data["email"]) | (User.account_name == data["account_name"])
        ).first()
        if existing:
            return None

        hashed_pw = generate_password_hash(data["password"]).decode("utf-8")

        user = User(
            account_name=data["account_name"],
            email=data["email"],
            password=hashed_pw,
            preferred_currency=data.get("preferred_currency", "CAD"),
            notification_opt_in=data.get("notification_opt_in", True)
        )
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return user
        return None
