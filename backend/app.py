"""
Legacy entry point. Prefer: python run.py  or  flask run (with FLASK_APP=run:app).
"""
from run import app

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True), host="0.0.0.0", port=5000)
