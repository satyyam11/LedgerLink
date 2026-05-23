import { getToken } from "./auth.jsx";
export const API_BASE = "https://ledgerlink-2.onrender.com/api";
export const GOOGLE_CLIENT_ID = "493852389490-dqb47jnspck82edltghg617995kd9fvn.apps.googleusercontent.com";

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const res = await fetch(`${API_BASE}${path}`, {
    headers,
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

  // ---------- HEALTH ----------
  async health() {
    return request("/health");
  },

  // ---------- AUTH ----------
  async register(email, password, name) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name })
    });
  },

  async login(email, password) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  // ---------- CHATBOT ----------
  async chatbotQuery(query) {
    return request("/chatbot/query", {
      method: "POST",
      body: JSON.stringify({ query })
    });
  },

  // ---------- EXPENSE ----------
  async categorizeExpense(text) {
    return request("/expense/categorize", {
      method: "POST",
      body: JSON.stringify({ text })
    });
  },

  async getExpenses() {
    return request("/expenses");
  },

  // ---------- INVOICE ----------
  async generateInvoice(text) {
    return request("/invoice/generate", {
      method: "POST",
      body: JSON.stringify({ text })
    });
  },

  async getInvoices() {
    return request("/invoices");
  },

  async updateInvoiceStatus(id, status) {
    return request(`/invoices/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    });
  },

  // ---------- CUSTOMERS ----------
  async getCustomers() {
    return request("/customers");
  },
  async createCustomer(payload) {
    return request("/customers", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  // ---------- PRODUCTS ----------
  async getProducts() {
    return request("/products");
  },
  async createProduct(payload) {
    return request("/products", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  // ---------- STATS ----------
  async getStats() {
    return request("/stats");
  }

};

export async function loginWithGoogle(credential) {
  return request("/auth/google", {
    method: "POST",
    body: JSON.stringify({ credential })
  });
}

