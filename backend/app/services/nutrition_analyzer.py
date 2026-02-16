from typing import Dict

import cv2
import numpy as np
import tensorflow as tf


FOOD_PROFILES = [
    {
        "label": "grilled chicken breast",
        "rgb_signature": [184.0, 146.0, 108.0],
        "macros": {"calories": 220.0, "protein": 40.0, "carbs": 0.0, "fat": 5.0},
    },
    {
        "label": "mixed salad",
        "rgb_signature": [92.0, 138.0, 71.0],
        "macros": {"calories": 120.0, "protein": 3.0, "carbs": 12.0, "fat": 7.0},
    },
    {
        "label": "white rice bowl",
        "rgb_signature": [216.0, 208.0, 196.0],
        "macros": {"calories": 205.0, "protein": 4.0, "carbs": 45.0, "fat": 0.4},
    },
    {
        "label": "oatmeal with berries",
        "rgb_signature": [186.0, 140.0, 124.0],
        "macros": {"calories": 260.0, "protein": 9.0, "carbs": 46.0, "fat": 6.0},
    },
    {
        "label": "salmon fillet",
        "rgb_signature": [208.0, 132.0, 108.0],
        "macros": {"calories": 233.0, "protein": 25.0, "carbs": 0.0, "fat": 14.0},
    },
]

EMBEDDINGS = tf.constant([profile["rgb_signature"] for profile in FOOD_PROFILES], dtype=tf.float32)


def _extract_visual_embedding(image_bytes: bytes) -> tf.Tensor:
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    decoded = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if decoded is None:
        raise ValueError("Invalid image content.")

    resized = cv2.resize(decoded, (224, 224), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    tensor = tf.convert_to_tensor(rgb, dtype=tf.float32)
    return tf.reduce_mean(tensor, axis=[0, 1])


def analyze_food_image(image_bytes: bytes) -> Dict[str, float]:
    image_embedding = _extract_visual_embedding(image_bytes)

    normalized_profiles = tf.linalg.l2_normalize(EMBEDDINGS, axis=1)
    normalized_image = tf.linalg.l2_normalize(tf.expand_dims(image_embedding, axis=0), axis=1)
    similarities = tf.squeeze(
        tf.matmul(normalized_profiles, normalized_image, transpose_b=True), axis=1
    )

    index = int(tf.argmax(similarities).numpy())
    confidence = float(tf.reduce_max(tf.nn.softmax(similarities * 8.0)).numpy())
    prediction = FOOD_PROFILES[index]

    return {
        "label": prediction["label"],
        "confidence": round(confidence, 4),
        "calories": prediction["macros"]["calories"],
        "protein": prediction["macros"]["protein"],
        "carbs": prediction["macros"]["carbs"],
        "fat": prediction["macros"]["fat"],
    }
