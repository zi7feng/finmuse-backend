# app/config.py
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 根据传入的环境变量加载不同的 .env 文件
env = os.getenv("FLASK_ENV", "development")
dotenv_path = ".env.prod" if env == "production" else ".env.dev"
load_dotenv(dotenv_path)

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_COOKIE_CSRF_PROTECT = False

    API_TITLE = "FinMuse API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    DB_USER = quote_plus(os.getenv("DB_USER", ""))
    DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "")
    DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSLMODE}"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 60 * 60
    REDIS_URL = os.getenv("REDIS_URL")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    JWT_COOKIE_CSRF_PROTECT = True  # 可以上线时再开启


# 工厂使用方式
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
