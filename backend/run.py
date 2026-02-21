import os
import sys

# Ensure backend directory is on path so "app" and "config" resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app(os.environ.get("FLASK_ENV") or "default")

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True), host="0.0.0.0", port=5000)
