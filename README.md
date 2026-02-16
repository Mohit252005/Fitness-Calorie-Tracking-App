## Fitness & Calorie Tracking App

**Tech stack:** Python, React, TensorFlow, OpenCV, Flask, PostgreSQL

- Developed a full-stack application using TensorFlow and OpenCV to automate food macronutrient analysis from images and track workout progress.
- Integrated a React frontend with a Flask/PostgreSQL backend to deliver personalized health dashboards and secure user authentication.
- Optimized image processing latency by implementing asynchronous task queues, ensuring real-time feedback for nutrient recognition.

---

## Project Structure

```text
backend/   Flask API, auth, PostgreSQL models, async food analysis queue
frontend/  React + Vite dashboard and tracking interface
```

## Backend (Flask + PostgreSQL)

### 1) Start PostgreSQL

```bash
docker compose up -d postgres
```

### 2) Configure environment

```bash
cd backend
cp .env.example .env
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run API server

```bash
python run.py
```

Backend runs on `http://localhost:5000`.

### Key API endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/workouts`
- `GET /api/workouts`
- `GET /api/dashboard`
- `POST /api/food/analyze` (async queue)
- `GET /api/food/tasks/<task_id>` (polling)
- `GET /api/food/logs`

## Frontend (React + Vite)

### 1) Configure environment

```bash
cd frontend
cp .env.example .env
```

### 2) Install dependencies

```bash
npm install
```

### 3) Run frontend

```bash
npm run dev
```

Frontend runs on `http://localhost:5173`.

---

## Notes

- Food recognition uses TensorFlow + OpenCV preprocessing and a nutrition profile matcher.
- Food analysis requests are handled in a background thread queue to keep API responses fast.
- SQLAlchemy models are PostgreSQL-ready and can fallback to SQLite if `DATABASE_URL` is not set.
