import os
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import Meal
from datetime import datetime, timezone

analyze_bp = Blueprint("analyze", __name__)


def allowed_file(filename):
    if not filename:
        return False
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "webp", "gif"}


@analyze_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():
    """
    Accept an image file, run stub analysis (placeholder for TensorFlow/OpenCV),
    return estimated macros. Optionally save image and create a meal log.
    """
    if "image" not in request.files and "file" not in request.files:
        return jsonify({"error": "No image file provided. Use form field 'image' or 'file'."}), 400
    file = request.files.get("image") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Allowed formats: png, jpg, jpeg, webp, gif"}), 400

    # Stub: in production, run TensorFlow/OpenCV here and return real macros
    # For now return placeholder values (could add simple heuristics later)
    result = {
        "calories": 450,
        "protein": 28,
        "carbs": 42,
        "fats": 18,
        "stub": True,
        "message": "Stub analysis; integrate TensorFlow/OpenCV for real recognition.",
    }

    # Optional: save image and store path for later ML pipeline
    upload_folder = request.app.config.get("UPLOAD_FOLDER")
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(upload_folder, unique)
        file.save(save_path)
        result["image_path"] = unique

    # Optional: if client sends save_meal=true, create a meal from this analysis
    save_meal = request.form.get("save_meal", "").lower() in ("1", "true", "yes")
    if save_meal:
        user_id = get_jwt_identity()
        meal = Meal(
            user_id=user_id,
            calories=result["calories"],
            protein=result["protein"],
            carbs=result["carbs"],
            fats=result["fats"],
            image_path=result.get("image_path"),
            name=request.form.get("name") or "Photo meal",
            logged_at=datetime.now(timezone.utc),
        )
        db.session.add(meal)
        db.session.commit()
        result["meal"] = meal.to_dict()
        result["meal_id"] = meal.id

    return jsonify(result)


@analyze_bp.route("/analyze/text", methods=["POST"])
@jwt_required()
def analyze_text():
    """
    Accept a text description of what was eaten, return stub macros.
    Body: { "description": "two eggs and toast" }, optional "save_meal", "name".
    """
    data = request.get_json() or {}
    description = (data.get("description") or "").strip()
    if not description:
        return jsonify({"error": "description required"}), 400

    # Stub: in production, use NLP or a food DB to estimate from description
    result = {
        "description": description,
        "calories": 420,
        "protein": 22,
        "carbs": 38,
        "fats": 20,
        "stub": True,
        "message": "Stub estimate; integrate food DB/NLP for real values.",
    }

    save_meal = data.get("save_meal") is True or str(data.get("save_meal", "")).lower() in ("1", "true", "yes")
    if save_meal:
        user_id = get_jwt_identity()
        meal = Meal(
            user_id=user_id,
            calories=result["calories"],
            protein=result["protein"],
            carbs=result["carbs"],
            fats=result["fats"],
            name=data.get("name") or description[:255],
            logged_at=datetime.now(timezone.utc),
        )
        db.session.add(meal)
        db.session.commit()
        result["meal"] = meal.to_dict()
        result["meal_id"] = meal.id

    return jsonify(result)
