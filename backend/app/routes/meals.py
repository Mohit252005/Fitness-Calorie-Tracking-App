from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app import db
from app.models import Meal

meals_bp = Blueprint("meals", __name__)


@meals_bp.route("", methods=["GET"])
@jwt_required()
def list_meals():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    from_date = request.args.get("from")  # ISO date
    to_date = request.args.get("to")
    q = Meal.query.filter_by(user_id=user_id)
    if from_date:
        try:
            q = q.filter(Meal.logged_at >= datetime.fromisoformat(from_date.replace("Z", "+00:00")))
        except ValueError:
            pass
    if to_date:
        try:
            q = q.filter(Meal.logged_at <= datetime.fromisoformat(to_date.replace("Z", "+00:00")))
        except ValueError:
            pass
    q = q.order_by(Meal.logged_at.desc())
    pagination = q.paginate(page=page, per_page=per_page)
    return jsonify(
        meals=[m.to_dict() for m in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
    )


@meals_bp.route("", methods=["POST"])
@jwt_required()
def create_meal():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or data.get("calories") is None:
        return jsonify({"error": "calories required"}), 400
    logged_at = data.get("logged_at")
    if logged_at:
        try:
            logged_at = datetime.fromisoformat(logged_at.replace("Z", "+00:00"))
        except ValueError:
            logged_at = datetime.now(timezone.utc)
    else:
        logged_at = datetime.now(timezone.utc)
    meal = Meal(
        user_id=user_id,
        calories=float(data.get("calories", 0)),
        protein=float(data.get("protein", 0)),
        carbs=float(data.get("carbs", 0)),
        fats=float(data.get("fats", 0)),
        name=data.get("name"),
        image_path=data.get("image_path"),
        logged_at=logged_at,
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify(meal.to_dict()), 201


@meals_bp.route("/<int:meal_id>", methods=["GET"])
@jwt_required()
def get_meal(meal_id):
    user_id = get_jwt_identity()
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not meal:
        return jsonify({"error": "Meal not found"}), 404
    return jsonify(meal.to_dict())


@meals_bp.route("/<int:meal_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_meal(meal_id):
    user_id = get_jwt_identity()
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not meal:
        return jsonify({"error": "Meal not found"}), 404
    data = request.get_json() or {}
    numeric_float_keys = ("calories", "protein", "carbs", "fats")
    for key in ("calories", "protein", "carbs", "fats", "name", "image_path", "logged_at"):
        if key not in data:
            continue
        if key == "logged_at":
            if data[key]:
                try:
                    meal.logged_at = datetime.fromisoformat(data[key].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            continue
        if key in numeric_float_keys:
            try:
                setattr(meal, key, float(data[key]))
            except (TypeError, ValueError):
                pass
            continue
        setattr(meal, key, data[key])
    db.session.commit()
    return jsonify(meal.to_dict())


@meals_bp.route("/<int:meal_id>", methods=["DELETE"])
@jwt_required()
def delete_meal(meal_id):
    user_id = get_jwt_identity()
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not meal:
        return jsonify({"error": "Meal not found"}), 404
    db.session.delete(meal)
    db.session.commit()
    return "", 204
