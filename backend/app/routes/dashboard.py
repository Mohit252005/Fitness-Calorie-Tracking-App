from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from ..models import FoodLog, Workout

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("")
@jwt_required()
def get_dashboard():
    user_id = int(get_jwt_identity())

    workout_totals = (
        Workout.query.with_entities(
            func.coalesce(func.sum(Workout.duration_minutes), 0),
            func.coalesce(func.sum(Workout.calories_burned), 0),
        )
        .filter_by(user_id=user_id)
        .first()
    )
    food_totals = (
        FoodLog.query.with_entities(
            func.coalesce(func.sum(FoodLog.calories), 0.0),
            func.coalesce(func.sum(FoodLog.protein), 0.0),
            func.coalesce(func.sum(FoodLog.carbs), 0.0),
            func.coalesce(func.sum(FoodLog.fat), 0.0),
        )
        .filter_by(user_id=user_id)
        .first()
    )

    recent_workouts = (
        Workout.query.filter_by(user_id=user_id)
        .order_by(Workout.workout_date.desc())
        .limit(5)
        .all()
    )
    recent_food_logs = (
        FoodLog.query.filter_by(user_id=user_id).order_by(FoodLog.created_at.desc()).limit(5).all()
    )

    return (
        jsonify(
            {
                "totals": {
                    "workout_minutes": int(workout_totals[0]),
                    "calories_burned": int(workout_totals[1]),
                    "calories_consumed": round(float(food_totals[0]), 2),
                    "protein": round(float(food_totals[1]), 2),
                    "carbs": round(float(food_totals[2]), 2),
                    "fat": round(float(food_totals[3]), 2),
                },
                "recent_workouts": [workout.to_dict() for workout in recent_workouts],
                "recent_food_logs": [log.to_dict() for log in recent_food_logs],
            }
        ),
        200,
    )
