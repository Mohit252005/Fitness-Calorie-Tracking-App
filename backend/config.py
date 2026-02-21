import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PostgreSQL (default for local dev; override with DATABASE_URL)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        user = os.environ.get("PGUSER", "postgres")
        pwd = os.environ.get("PGPASSWORD", "postgres")
        host = os.environ.get("PGHOST", "localhost")
        port = os.environ.get("PGPORT", "5432")
        db = os.environ.get("PGDATABASE", "fitness_app")
        # Encode user and password so special chars (@, #, :, etc.) don't break the URL
        user_enc = quote(user, safe="")
        pwd_enc = quote(pwd, safe="")
        DATABASE_URL = f"postgresql://{user_enc}:{pwd_enc}@{host}:{port}/{db}"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 days

    # Uploads (for meal images)
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "uploads"
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
