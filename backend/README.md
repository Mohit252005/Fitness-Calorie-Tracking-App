# Fitness App — Backend

Flask API with PostgreSQL, JWT auth, and stubbed image analysis.

## Setup

1. **Create a virtualenv and install dependencies**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**

   Copy `.env.example` to `.env` and set your PostgreSQL credentials (or `DATABASE_URL`).

3. **Create the database**

   Create a PostgreSQL database named `fitness_app` (or your `PGDATABASE` value).

4. **Run migrations**

   ```bash
   flask db upgrade
   ```

   If this is the first time, generate migrations after editing models:

   ```bash
   flask db migrate -m "Initial"
   flask db upgrade
   ```

5. **Run the server**

   ```bash
   python run.py
   ```

   API base: `http://localhost:5000`

## API Overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | Health check |
| POST | `/api/auth/register` | No | Register (email, password) |
| POST | `/api/auth/login` | No | Login |
| POST | `/api/auth/refresh` | Refresh | New access token |
| GET | `/api/auth/me` | Yes | Current user |
| POST | `/api/analyze` | Yes | Upload image → stub macros (form: `image` or `file`, optional `save_meal`, `name`) |
| GET | `/api/meals` | Yes | List meals (query: `page`, `per_page`, `from`, `to`) |
| POST | `/api/meals` | Yes | Log meal (JSON body) |
| GET/PUT/DELETE | `/api/meals/<id>` | Yes | Get/update/delete meal |
| GET | `/api/workouts` | Yes | List workouts |
| POST | `/api/workouts` | Yes | Log workout |
| GET/PUT/DELETE | `/api/workouts/<id>` | Yes | Get/update/delete workout |
| GET | `/api/dashboard/summary` | Yes | Daily/range summary (query: `date` or `from` & `to`) |
| GET | `/api/dashboard/history` | Yes | Recent meals and workouts (`limit`) |

Protected routes require header: `Authorization: Bearer <access_token>`.
