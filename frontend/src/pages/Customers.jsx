import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Customers() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    address: ""
  });
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadCustomers() {
    try {
      const res = await api.getCustomers();
      setRows(res.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Name is required.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await api.createCustomer(form);
      setForm({ name: "", email: "", phone: "", address: "" });
      await loadCustomers();
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function updateField(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  return (
    <div>
      <h3>Customers</h3>
      <p className="muted">Manage customers linked to your invoices.</p>

      <form onSubmit={handleSubmit} className="card form">
        <div className="form-grid">
          <div>
            <label>Name *</label>
            <input
              value={form.name}
              onChange={(e) => updateField("name", e.target.value)}
            />
          </div>
          <div>
            <label>Email</label>
            <input
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
            />
          </div>
          <div>
            <label>Phone</label>
            <input
              value={form.phone}
              onChange={(e) => updateField("phone", e.target.value)}
            />
          </div>
          <div className="full">
            <label>Address</label>
            <textarea
              rows={2}
              value={form.address}
              onChange={(e) => updateField("address", e.target.value)}
            />
          </div>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Add Customer"}
        </button>
        {error && <div className="error">{error}</div>}
      </form>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h4>Customer List</h4>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.email}</td>
                  <td>{r.phone}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan="4" className="muted">
                    No customers yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
