// src/api.js
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
  async health() {
    return request("/health");
  },
  async categorizeExpense(text) {
    return request("/expense/categorize", {
      method: "POST",
      body: JSON.stringify({ text })
    });
  },
  async getExpenses() {
    return request("/expenses");
  },
  async generateInvoice(text) {
    return request("/invoice/generate", {
      method: "POST",
      body: JSON.stringify({ text })
    });
  },
  async getInvoices() {
    return request("/invoices");
  },
  async createCustomer(payload) {
    return request("/customers", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  async getCustomers() {
    return request("/customers");
  },
  async createProduct(payload) {
    return request("/products", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  async getProducts() {
    return request("/products");
  }
};
