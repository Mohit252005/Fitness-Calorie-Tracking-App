from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import FoodLog
from ..services.nutrition_analyzer import analyze_food_image

food_bp = Blueprint("food", __name__, url_prefix="/api/food")


def _analyze_and_store(app, user_id, image_bytes):
    with app.app_context():
        prediction = analyze_food_image(image_bytes)
        food_log = FoodLog(
            user_id=user_id,
            label=prediction["label"],
            confidence=prediction["confidence"],
            calories=prediction["calories"],
            protein=prediction["protein"],
            carbs=prediction["carbs"],
            fat=prediction["fat"],
        )
        db.session.add(food_log)
        db.session.commit()

        payload = food_log.to_dict()
        payload["user_id"] = user_id
        return payload


@food_bp.post("/analyze")
@jwt_required()
def analyze_food():
    user_id = int(get_jwt_identity())
    if "image" not in request.files:
        return jsonify({"error": "Image is required under field name 'image'."}), 400

    image = request.files["image"]
    image_bytes = image.read()
    if not image_bytes:
        return jsonify({"error": "Uploaded image is empty."}), 400

    app = current_app._get_current_object()
    task_id = current_app.task_queue.enqueue(
        _analyze_and_store, app, user_id, image_bytes, metadata={"user_id": user_id}
    )
    return jsonify({"task_id": task_id, "status": "queued"}), 202


@food_bp.get("/tasks/<task_id>")
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())
    task = current_app.task_queue.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404

    owner_id = task.get("metadata", {}).get("user_id")
    if owner_id != user_id:
        return jsonify({"error": "Task does not belong to current user."}), 403

    response = {
        "task_id": task_id,
        "status": task["status"],
        "result": task["result"],
        "error": task["error"],
    }
    return jsonify(response), 200


@food_bp.get("/logs")
@jwt_required()
def food_logs():
    user_id = int(get_jwt_identity())
    logs = FoodLog.query.filter_by(user_id=user_id).order_by(FoodLog.created_at.desc()).limit(50).all()
    return jsonify([log.to_dict() for log in logs]), 200
