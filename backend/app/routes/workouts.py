from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app import db
from app.models import Workout

workouts_bp = Blueprint("workouts", __name__)


@workouts_bp.route("", methods=["GET"])
@jwt_required()
def list_workouts():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    q = Workout.query.filter_by(user_id=user_id)
    if from_date:
        try:
            q = q.filter(Workout.logged_at >= datetime.fromisoformat(from_date.replace("Z", "+00:00")))
        except ValueError:
            pass
    if to_date:
        try:
            q = q.filter(Workout.logged_at <= datetime.fromisoformat(to_date.replace("Z", "+00:00")))
        except ValueError:
            pass
    q = q.order_by(Workout.logged_at.desc())
    pagination = q.paginate(page=page, per_page=per_page)
    return jsonify(
        workouts=[w.to_dict() for w in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
    )


@workouts_bp.route("", methods=["POST"])
@jwt_required()
def create_workout():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("name") or data.get("duration_minutes") is None:
        return jsonify({"error": "name and duration_minutes required"}), 400
    logged_at = data.get("logged_at")
    if logged_at:
        try:
            logged_at = datetime.fromisoformat(logged_at.replace("Z", "+00:00"))
        except ValueError:
            logged_at = datetime.now(timezone.utc)
    else:
        logged_at = datetime.now(timezone.utc)
    workout = Workout(
        user_id=user_id,
        name=data["name"].strip(),
        duration_minutes=int(data["duration_minutes"]),
        calories_burned=data.get("calories_burned"),
        notes=data.get("notes"),
        logged_at=logged_at,
    )
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout.to_dict()), 201


@workouts_bp.route("/<int:workout_id>", methods=["GET"])
@jwt_required()
def get_workout(workout_id):
    user_id = get_jwt_identity()
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout.to_dict())


@workouts_bp.route("/<int:workout_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_workout(workout_id):
    user_id = get_jwt_identity()
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    data = request.get_json() or {}
    for key in ("name", "duration_minutes", "calories_burned", "notes", "logged_at"):
        if key not in data:
            continue
        if key == "logged_at":
            if data[key]:
                try:
                    workout.logged_at = datetime.fromisoformat(data[key].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            continue
        if key == "duration_minutes":
            try:
                workout.duration_minutes = int(data[key])
            except (TypeError, ValueError):
                pass
            continue
        if key == "calories_burned":
            try:
                val = data[key]
                workout.calories_burned = float(val) if val is not None else None
            except (TypeError, ValueError):
                pass
            continue
        setattr(workout, key, data[key])
    db.session.commit()
    return jsonify(workout.to_dict())


@workouts_bp.route("/<int:workout_id>", methods=["DELETE"])
@jwt_required()
def delete_workout(workout_id):
    user_id = get_jwt_identity()
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    db.session.delete(workout)
    db.session.commit()
    return "", 204
