import { useEffect, useState } from "react";
import { api } from "../api.js";
import { SkeletonTable } from "../components/Skeleton.jsx";
import { useToast } from "../components/Toast.jsx";

export default function Products() {
  const { addToast } = useToast();
  const [form, setForm] = useState({
    name: "",
    sku: "",
    unit_price: ""
  });
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);

  async function loadProducts() {
    try {
      setListLoading(true);
      setError("");
      console.log("Fetching products...");
      const res = await api.getProducts();
      console.log("Products API response:", res);
      if (res && res.success && Array.isArray(res.data)) {
        setRows(res.data);
      } else {
        console.warn("Expected success response with data array, got:", res);
        setRows([]);
      }
    } catch (err) {
      console.error("Failed to load products:", err);
      setError(err.message || "An unknown error occurred while loading products.");
    } finally {
      setListLoading(false);
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
      addToast("Product added successfully");
      await loadProducts();
    } catch (err) {
      console.error(err);
      setError(err.message);
      addToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  }

  if (error) {
    return (
      <div className="card" style={{ marginTop: "2rem", borderColor: "red" }}>
        <h3 style={{ color: "red" }}>Error</h3>
        <p>{error}</p>
        <button onClick={() => { setError(""); loadProducts(); }}>Retry</button>
      </div>
    );
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
        {listLoading ? (
          <SkeletonTable rows={5} cols={4} />
        ) : (
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
                {(rows || []).map((r) => (
                  <tr key={r?.id || Math.random()}>
                    <td>{r?.id}</td>
                    <td>{r?.name}</td>
                    <td>{r?.sku}</td>
                    <td>{r?.unit_price}</td>
                  </tr>
                ))}
                {(!rows || rows.length === 0) && (
                  <tr>
                    <td colSpan="4" className="muted">
                      No products yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
