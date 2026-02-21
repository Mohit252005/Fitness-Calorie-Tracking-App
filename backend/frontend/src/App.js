import { useState, useEffect } from "react";
import { guestLogin, getEstimate, logMeal, getTodaySummary } from "./api";
import "./App.css";

const TOKEN_KEY = "fitness_token";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [description, setDescription] = useState("");
  const [estimate, setEstimate] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (!token) return;
    getTodaySummary(token)
      .then(setSummary)
      .catch(() => setSummary(null));
  }, [token]);

  const handleGuestLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await guestLogin();
      localStorage.setItem(TOKEN_KEY, data.access_token);
      setToken(data.access_token);
      setSummary(null);
    } catch (e) {
      setError(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleGetEstimate = async () => {
    if (!description.trim() || !token) return;
    setError(null);
    setEstimate(null);
    setLoading(true);
    try {
      const data = await getEstimate(token, description);
      setEstimate(data);
    } catch (e) {
      setError(e.message || "Could not get estimate");
    } finally {
      setLoading(false);
    }
  };

  const handleLogMeal = async () => {
    if (!description.trim() || !token) return;
    setError(null);
    setLoading(true);
    try {
      await logMeal(token, description);
      setEstimate(null);
      setDescription("");
      getTodaySummary(token).then(setSummary).catch(() => setSummary(null));
    } catch (e) {
      setError(e.message || "Could not log meal");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="app">
        <header className="header">
          <h1>Fitness & Calorie Tracker</h1>
        </header>
        <main className="main">
          <p className="intro">Enter what you ate and get a quick calorie estimate. No account needed.</p>
          {error && <div className="error">{error}</div>}
          <button
            className="btn btn-primary"
            onClick={handleGuestLogin}
            disabled={loading}
          >
            {loading ? "…" : "Continue as guest"}
          </button>
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Fitness & Calorie Tracker</h1>
        <span className="badge">Guest</span>
      </header>

      <main className="main">
        {summary != null && (
          <section className="summary">
            <h2>Today</h2>
            <p>
              <strong>Calories:</strong> {summary.calories_in} kcal
              {summary.meals_count > 0 && ` (${summary.meals_count} meal${summary.meals_count !== 1 ? "s" : ""})`}
            </p>
          </section>
        )}

        <section className="form-section">
          <h2>What did you eat?</h2>
          <textarea
            className="input"
            placeholder="e.g. two eggs, toast, and coffee"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
          />
          {error && <div className="error">{error}</div>}
          <div className="actions">
            <button
              className="btn btn-primary"
              onClick={handleGetEstimate}
              disabled={loading || !description.trim()}
            >
              {loading ? "…" : "Get estimate"}
            </button>
          </div>
        </section>

        {estimate && (
          <section className="estimate">
            <h3>Estimate</h3>
            <ul className="macros">
              <li><strong>Calories:</strong> {estimate.calories} kcal</li>
              <li><strong>Protein:</strong> {estimate.protein} g</li>
              <li><strong>Carbs:</strong> {estimate.carbs} g</li>
              <li><strong>Fats:</strong> {estimate.fats} g</li>
            </ul>
            {estimate.stub && (
              <p className="stub-note">This is a placeholder estimate. Real values will come from a food database.</p>
            )}
            <button
              className="btn btn-secondary"
              onClick={handleLogMeal}
              disabled={loading}
            >
              {loading ? "…" : "Log this meal"}
            </button>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
