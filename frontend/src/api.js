export const API_BASE = "http://localhost:5000/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok || data.success === false) {
    const msg = data.error || res.statusText || "Request failed";
    throw new Error(msg);
  }

  return data;
}

export const api = {
  // -------- HEALTH --------
  async health() {
    return request("/health");
  },

  // -------- AUTH --------
  async register(email, password) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  async login(email, password) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  // -------- EXPENSE --------
  async categorizeExpense(text) {
    return request("/expense/categorize", {
      method: "POST",
      body: JSON.stringify({ text })
    });
  }
};
