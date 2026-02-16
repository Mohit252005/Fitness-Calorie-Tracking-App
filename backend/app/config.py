import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    # Production should use PostgreSQL via DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///fitness_tracker.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
