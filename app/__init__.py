from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_jwt_extended import JWTManager
import redis

db = SQLAlchemy()
jwt = JWTManager()
redis_client = redis.from_url(Config.REDIS_URL)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.get(f"bl:{jti}") is not None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app.models import user
        db.create_all()

    from app.routes.auth import auth_bp
    from flask_smorest import Api
    api = Api(app)

    api.spec.components.security_scheme(
        "BearerAuth",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    )
    api.register_blueprint(auth_bp)

    return app
