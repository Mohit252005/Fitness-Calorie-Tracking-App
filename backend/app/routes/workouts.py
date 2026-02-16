from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Workout

workouts_bp = Blueprint("workouts", __name__, url_prefix="/api/workouts")


@workouts_bp.get("")
@jwt_required()
def list_workouts():
    user_id = int(get_jwt_identity())
    workouts = (
        Workout.query.filter_by(user_id=user_id)
        .order_by(Workout.workout_date.desc())
        .limit(50)
        .all()
    )
    return jsonify([workout.to_dict() for workout in workouts]), 200


@workouts_bp.post("")
@jwt_required()
def create_workout():
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    workout_type = (payload.get("workout_type") or "").strip()
    duration_minutes = payload.get("duration_minutes")
    calories_burned = payload.get("calories_burned")
    notes = payload.get("notes")

    if not workout_type or duration_minutes is None or calories_burned is None:
        return jsonify({"error": "workout_type, duration_minutes, and calories_burned are required."}), 400

    try:
        duration_minutes = int(duration_minutes)
        calories_burned = int(calories_burned)
    except (TypeError, ValueError):
        return jsonify({"error": "duration_minutes and calories_burned must be integers."}), 400

    workout_date = payload.get("workout_date")
    parsed_workout_date = datetime.utcnow()
    if workout_date:
        try:
            parsed_workout_date = datetime.fromisoformat(workout_date)
        except ValueError:
            return jsonify({"error": "workout_date must be ISO-8601 format."}), 400

    workout = Workout(
        user_id=user_id,
        workout_type=workout_type,
        duration_minutes=duration_minutes,
        calories_burned=calories_burned,
        workout_date=parsed_workout_date,
        notes=notes,
    )
    db.session.add(workout)
    db.session.commit()

    return jsonify(workout.to_dict()), 201
