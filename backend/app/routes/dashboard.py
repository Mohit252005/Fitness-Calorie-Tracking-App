from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone, timedelta
from app import db
from app.models import Meal, Workout

dashboard_bp = Blueprint("dashboard", __name__)


def _parse_date(s, default=None):
    if not s:
        return default
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        return default


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """
    Daily and optional weekly summary: total calories (meals), total burned (workouts),
    and macro breakdown for the given date or range.
    """
    user_id = get_jwt_identity()
    today = datetime.now(timezone.utc).date()
    date_str = request.args.get("date")
    from_str = request.args.get("from")
    to_str = request.args.get("to")

    # Single day summary
    if date_str:
        day = _parse_date(date_str, today)
        start = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        meals = Meal.query.filter(
            Meal.user_id == user_id,
            Meal.logged_at >= start,
            Meal.logged_at < end,
        ).all()
        workouts = Workout.query.filter(
            Workout.user_id == user_id,
            Workout.logged_at >= start,
            Workout.logged_at < end,
        ).all()
        calories_in = sum(m.calories for m in meals)
        protein = sum(m.protein for m in meals)
        carbs = sum(m.carbs for m in meals)
        fats = sum(m.fats for m in meals)
        calories_out = sum(w.calories_burned or 0 for w in workouts)
        return jsonify({
            "date": day.isoformat(),
            "calories_in": round(calories_in, 1),
            "calories_out": round(calories_out, 1),
            "protein": round(protein, 1),
            "carbs": round(carbs, 1),
            "fats": round(fats, 1),
            "meals_count": len(meals),
            "workouts_count": len(workouts),
        })

    # Range summary (e.g. last 7 days)
    from_date = _parse_date(from_str, today - timedelta(days=6))
    to_date = _parse_date(to_str, today)
    if from_date > to_date:
        from_date, to_date = to_date, from_date
    start = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(to_date, datetime.min.time()).replace(tzinfo=timezone.utc) + timedelta(days=1)

    meals = Meal.query.filter(
        Meal.user_id == user_id,
        Meal.logged_at >= start,
        Meal.logged_at < end,
    ).all()
    workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.logged_at >= start,
        Workout.logged_at < end,
    ).all()

    calories_in = sum(m.calories for m in meals)
    protein = sum(m.protein for m in meals)
    carbs = sum(m.carbs for m in meals)
    fats = sum(m.fats for m in meals)
    calories_out = sum(w.calories_burned or 0 for w in workouts)

    return jsonify({
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "calories_in": round(calories_in, 1),
        "calories_out": round(calories_out, 1),
        "protein": round(protein, 1),
        "carbs": round(carbs, 1),
        "fats": round(fats, 1),
        "meals_count": len(meals),
        "workouts_count": len(workouts),
    })


@dashboard_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    """
    Recent activity: last N meals and last N workouts for dashboard widgets.
    """
    user_id = get_jwt_identity()
    limit = min(request.args.get("limit", 10, type=int), 50)
    meals = (
        Meal.query.filter_by(user_id=user_id)
        .order_by(Meal.logged_at.desc())
        .limit(limit)
        .all()
    )
    workouts = (
        Workout.query.filter_by(user_id=user_id)
        .order_by(Workout.logged_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify({
        "meals": [m.to_dict() for m in meals],
        "workouts": [w.to_dict() for w in workouts],
    })
