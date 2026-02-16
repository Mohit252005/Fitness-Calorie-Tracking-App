from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, jwt
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.food import food_bp
from .routes.workouts import workouts_bp
from .services.task_queue import InMemoryTaskQueue


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    app.task_queue = InMemoryTaskQueue(max_workers=2)

    app.register_blueprint(auth_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(food_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    with app.app_context():
        db.create_all()

    return app
