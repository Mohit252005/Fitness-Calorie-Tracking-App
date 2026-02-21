from app.routes.auth import auth_bp
from app.routes.meals import meals_bp
from app.routes.workouts import workouts_bp
from app.routes.analyze import analyze_bp
from app.routes.dashboard import dashboard_bp

__all__ = ["auth_bp", "meals_bp", "workouts_bp", "analyze_bp", "dashboard_bp"]
