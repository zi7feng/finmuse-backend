from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from app.config import config_by_name
import redis
import os
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()

redis_client = None  # 初始化为空，稍后在 app factory 中注入配置

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.get(f"bl:{jti}") is not None




def create_app():
    app = Flask(__name__)

    # 🔁 加载环境变量配置（FLASK_ENV 默认 development）
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name[env])

    print(env)

    for key in ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']:
        print(f"{key} = {os.getenv(key)}")

    print(111)
    print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    print(111)

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:3039")
    origins = frontend_origin.split(',')
    CORS(app, origins=origins, supports_credentials=True)

    # ✅ 初始化数据库
    db.init_app(app)

    # ✅ 初始化 JWT
    jwt.init_app(app)

    # ✅ 初始化 Redis（基于当前配置）
    global redis_client
    redis_client = redis.from_url(app.config["REDIS_URL"])

    # ✅ 加载模型
    with app.app_context():
        from app.models import user
        db.create_all()

    # ✅ 注册蓝图和 API 文档
    api = Api(app)
    api.spec.components.security_scheme(
        "BearerAuth",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    )

    from app.routes.auth import auth_bp
    api.register_blueprint(auth_bp)

    @app.route("/ping")
    def ping():
        return {"message": "pong"}

    print("Current env:", env)
    print("origins setup:", origins)

    return app
