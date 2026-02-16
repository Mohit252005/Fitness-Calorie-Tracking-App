import { useCallback, useEffect, useMemo, useState } from "react";

import { apiRequest } from "./api";

const emptyAuthForm = { name: "", email: "", password: "" };
const emptyWorkoutForm = {
  workout_type: "",
  duration_minutes: "",
  calories_burned: "",
  notes: "",
};

function parseStoredUser() {
  const raw = window.localStorage.getItem("fitness_user");
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function StatCard({ label, value, suffix = "" }) {
  return (
    <div className="stat-card">
      <h4>{label}</h4>
      <p>
        {value}
        {suffix}
      </p>
    </div>
  );
}

export default function App() {
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState(emptyAuthForm);
  const [token, setToken] = useState(() => window.localStorage.getItem("fitness_token") || "");
  const [user, setUser] = useState(() => parseStoredUser());
  const [workoutForm, setWorkoutForm] = useState(emptyWorkoutForm);
  const [selectedImage, setSelectedImage] = useState(null);
  const [activeTaskId, setActiveTaskId] = useState("");
  const [analysisMessage, setAnalysisMessage] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [workouts, setWorkouts] = useState([]);
  const [foodLogs, setFoodLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isAuthenticated = Boolean(token);
  const totals = useMemo(
    () =>
      dashboard?.totals || {
        workout_minutes: 0,
        calories_burned: 0,
        calories_consumed: 0,
        protein: 0,
        carbs: 0,
        fat: 0,
      },
    [dashboard],
  );

  const persistAuth = useCallback((nextToken, nextUser) => {
    setToken(nextToken);
    setUser(nextUser);
    window.localStorage.setItem("fitness_token", nextToken);
    window.localStorage.setItem("fitness_user", JSON.stringify(nextUser));
  }, []);

  const clearAuth = useCallback(() => {
    setToken("");
    setUser(null);
    setDashboard(null);
    setWorkouts([]);
    setFoodLogs([]);
    setActiveTaskId("");
    setAnalysisMessage("");
    window.localStorage.removeItem("fitness_token");
    window.localStorage.removeItem("fitness_user");
  }, []);

  const loadAppData = useCallback(async () => {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const [dashboardPayload, workoutsPayload, logsPayload] = await Promise.all([
        apiRequest("/api/dashboard", { token }),
        apiRequest("/api/workouts", { token }),
        apiRequest("/api/food/logs", { token }),
      ]);
      setDashboard(dashboardPayload);
      setWorkouts(workoutsPayload);
      setFoodLogs(logsPayload);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (isAuthenticated) {
      loadAppData();
    }
  }, [isAuthenticated, loadAppData]);

  useEffect(() => {
    if (!activeTaskId || !token) {
      return;
    }

    let cancelled = false;
    const pollTask = async () => {
      try {
        const task = await apiRequest(`/api/food/tasks/${activeTaskId}`, { token });
        if (cancelled) {
          return;
        }

        if (task.status === "completed") {
          setAnalysisMessage(
            `Recognized ${task.result.label} (${Math.round(task.result.confidence * 100)}% confidence).`,
          );
          setActiveTaskId("");
          await loadAppData();
        } else if (task.status === "failed") {
          setAnalysisMessage(`Analysis failed: ${task.error || "Unknown error"}`);
          setActiveTaskId("");
        } else {
          setAnalysisMessage("Analyzing image... this runs asynchronously in the backend queue.");
        }
      } catch (pollError) {
        if (!cancelled) {
          setAnalysisMessage(`Task polling failed: ${pollError.message}`);
          setActiveTaskId("");
        }
      }
    };

    pollTask();
    const intervalId = window.setInterval(pollTask, 1200);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [activeTaskId, token, loadAppData]);

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const endpoint = authMode === "login" ? "/api/auth/login" : "/api/auth/register";
      const payload =
        authMode === "login"
          ? { email: authForm.email, password: authForm.password }
          : { name: authForm.name, email: authForm.email, password: authForm.password };

      const authResponse = await apiRequest(endpoint, { method: "POST", body: payload });
      persistAuth(authResponse.token, authResponse.user);
      setAuthForm(emptyAuthForm);
    } catch (authError) {
      setError(authError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleWorkoutSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await apiRequest("/api/workouts", {
        method: "POST",
        token,
        body: {
          workout_type: workoutForm.workout_type,
          duration_minutes: Number(workoutForm.duration_minutes),
          calories_burned: Number(workoutForm.calories_burned),
          notes: workoutForm.notes,
        },
      });
      setWorkoutForm(emptyWorkoutForm);
      await loadAppData();
    } catch (workoutError) {
      setError(workoutError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleFoodUpload(event) {
    event.preventDefault();
    if (!selectedImage) {
      setError("Please choose an image first.");
      return;
    }

    setError("");
    setLoading(true);
    setAnalysisMessage("Uploading image...");
    try {
      const formData = new FormData();
      formData.append("image", selectedImage);
      const queuedTask = await apiRequest("/api/food/analyze", {
        method: "POST",
        token,
        body: formData,
        isFormData: true,
      });
      setActiveTaskId(queuedTask.task_id);
      setSelectedImage(null);
    } catch (uploadError) {
      setError(uploadError.message);
      setAnalysisMessage("");
    } finally {
      setLoading(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <main className="auth-layout">
        <section className="panel">
          <h1>Fitness & Calorie Tracking App</h1>
          <p>Track workouts, analyze food with TensorFlow + OpenCV, and monitor nutrition goals.</p>
        </section>

        <section className="panel">
          <h2>{authMode === "login" ? "Sign in" : "Create account"}</h2>
          <form onSubmit={handleAuthSubmit} className="form-grid">
            {authMode === "register" && (
              <label>
                Name
                <input
                  required
                  value={authForm.name}
                  onChange={(event) => setAuthForm((prev) => ({ ...prev, name: event.target.value }))}
                  placeholder="Your name"
                />
              </label>
            )}
            <label>
              Email
              <input
                required
                type="email"
                value={authForm.email}
                onChange={(event) => setAuthForm((prev) => ({ ...prev, email: event.target.value }))}
                placeholder="you@example.com"
              />
            </label>
            <label>
              Password
              <input
                required
                type="password"
                minLength={6}
                value={authForm.password}
                onChange={(event) => setAuthForm((prev) => ({ ...prev, password: event.target.value }))}
                placeholder="Minimum 6 characters"
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Submitting..." : authMode === "login" ? "Login" : "Register"}
            </button>
          </form>

          <button
            type="button"
            className="link-button"
            onClick={() => setAuthMode((prev) => (prev === "login" ? "register" : "login"))}
          >
            {authMode === "login" ? "Need an account? Register" : "Already have an account? Login"}
          </button>
          {error && <p className="error">{error}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="dashboard-layout">
      <header className="topbar">
        <div>
          <h1>Welcome, {user?.name || "Athlete"}</h1>
          <p>Personalized health dashboard with workout and nutrition insights.</p>
        </div>
        <button type="button" onClick={clearAuth}>
          Logout
        </button>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="stats-grid">
        <StatCard label="Workout Minutes" value={totals.workout_minutes} />
        <StatCard label="Calories Burned" value={totals.calories_burned} />
        <StatCard label="Calories Consumed" value={totals.calories_consumed} />
        <StatCard label="Protein" value={totals.protein} suffix=" g" />
        <StatCard label="Carbs" value={totals.carbs} suffix=" g" />
        <StatCard label="Fat" value={totals.fat} suffix=" g" />
      </section>

      <section className="grid-two">
        <article className="panel">
          <h2>Log Workout</h2>
          <form onSubmit={handleWorkoutSubmit} className="form-grid">
            <label>
              Workout Type
              <input
                required
                value={workoutForm.workout_type}
                onChange={(event) =>
                  setWorkoutForm((prev) => ({ ...prev, workout_type: event.target.value }))
                }
                placeholder="Running, Cycling..."
              />
            </label>
            <label>
              Duration (minutes)
              <input
                required
                type="number"
                min={1}
                value={workoutForm.duration_minutes}
                onChange={(event) =>
                  setWorkoutForm((prev) => ({ ...prev, duration_minutes: event.target.value }))
                }
              />
            </label>
            <label>
              Calories Burned
              <input
                required
                type="number"
                min={1}
                value={workoutForm.calories_burned}
                onChange={(event) =>
                  setWorkoutForm((prev) => ({ ...prev, calories_burned: event.target.value }))
                }
              />
            </label>
            <label>
              Notes
              <input
                value={workoutForm.notes}
                onChange={(event) => setWorkoutForm((prev) => ({ ...prev, notes: event.target.value }))}
                placeholder="Optional"
              />
            </label>
            <button type="submit" disabled={loading}>
              Save Workout
            </button>
          </form>
        </article>

        <article className="panel">
          <h2>Analyze Meal (TensorFlow + OpenCV)</h2>
          <form onSubmit={handleFoodUpload} className="form-grid">
            <label>
              Food Image
              <input
                required
                type="file"
                accept="image/*"
                onChange={(event) => setSelectedImage(event.target.files?.[0] || null)}
              />
            </label>
            <button type="submit" disabled={loading || Boolean(activeTaskId)}>
              {activeTaskId ? "Analyzing..." : "Analyze Food"}
            </button>
          </form>
          {analysisMessage && <p className="info">{analysisMessage}</p>}
        </article>
      </section>

      <section className="grid-two">
        <article className="panel">
          <h2>Recent Workouts</h2>
          {workouts.length === 0 && !loading ? <p>No workouts logged yet.</p> : null}
          <ul className="list">
            {workouts.slice(0, 8).map((workout) => (
              <li key={workout.id}>
                <strong>{workout.workout_type}</strong> - {workout.duration_minutes} min,{" "}
                {workout.calories_burned} kcal
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Recent Nutrition Logs</h2>
          {foodLogs.length === 0 && !loading ? <p>No nutrition analysis yet.</p> : null}
          <ul className="list">
            {foodLogs.slice(0, 8).map((log) => (
              <li key={log.id}>
                <strong>{log.label}</strong> - {log.calories} kcal | P:{log.protein} C:{log.carbs} F:{log.fat}
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
