import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Products() {
  const [form, setForm] = useState({
    name: "",
    sku: "",
    unit_price: ""
  });
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadProducts() {
    try {
      const res = await api.getProducts();
      setRows(res.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  function updateField(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Name is required.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await api.createProduct({
        ...form,
        unit_price: form.unit_price ? Number(form.unit_price) : 0
      });
      setForm({ name: "", sku: "", unit_price: "" });
      await loadProducts();
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h3>Products</h3>
      <p className="muted">Items you sell or bill for in invoices.</p>

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
            <label>SKU</label>
            <input
              value={form.sku}
              onChange={(e) => updateField("sku", e.target.value)}
            />
          </div>
          <div>
            <label>Unit Price</label>
            <input
              type="number"
              value={form.unit_price}
              onChange={(e) => updateField("unit_price", e.target.value)}
            />
          </div>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Add Product"}
        </button>
        {error && <div className="error">{error}</div>}
      </form>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h4>Product List</h4>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>SKU</th>
                <th>Unit Price</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.sku}</td>
                  <td>{r.unit_price}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan="4" className="muted">
                    No products yet.
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
