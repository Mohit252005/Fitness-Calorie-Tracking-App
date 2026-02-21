const getApiUrl = () => process.env.REACT_APP_API_URL || "http://localhost:5000";

const authHeaders = (token) =>
  token ? { Authorization: `Bearer ${token}` } : {};

export async function guestLogin() {
  const res = await fetch(`${getApiUrl()}/api/auth/guest`, { method: "POST" });
  if (!res.ok) throw new Error("Guest login failed");
  const data = await res.json();
  return data;
}

export async function getEstimate(token, description) {
  const res = await fetch(`${getApiUrl()}/api/analyze/text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ description: description.trim() }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Estimate failed");
  }
  return res.json();
}

export async function logMeal(token, description) {
  const res = await fetch(`${getApiUrl()}/api/analyze/text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ description: description.trim(), save_meal: true }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Failed to log meal");
  }
  return res.json();
}

export async function getTodaySummary(token) {
  const today = new Date().toISOString().slice(0, 10);
  const res = await fetch(
    `${getApiUrl()}/api/dashboard/summary?date=${today}`,
    { headers: authHeaders(token) }
  );
  if (!res.ok) throw new Error("Failed to load summary");
  return res.json();
}
