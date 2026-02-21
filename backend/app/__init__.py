from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from config import config_by_name

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    config_name = config_name or "default"
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.models import User, Meal, Workout  # noqa: F401 - register models for Flask-Migrate
    from app.routes import auth_bp, meals_bp, workouts_bp, analyze_bp, dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(meals_bp, url_prefix="/api/meals")
    app.register_blueprint(workouts_bp, url_prefix="/api/workouts")
    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    @app.route("/")
    def home():
        return {"message": "Backend is running"}

    return app
