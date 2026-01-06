import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Invoices() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadInvoices() {
    try {
      const res = await api.getInvoices();
      setRows(res.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadInvoices();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError("");
    try {
      const res = await api.generateInvoice(text.trim());
      setResult(res.data);
      setText("");
      await loadInvoices();
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h3>Invoices</h3>
      <p className="muted">
        Describe the work and amount, e.g. “Create invoice for web development
        for Acme Corp 50000”.
      </p>

      <form onSubmit={handleSubmit} className="card form">
        <label>Invoice request</label>
        <textarea
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate & Save"}
        </button>
        {error && <div className="error">{error}</div>}
      </form>

      {result && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <h4>Last Invoice</h4>
          <div className="prediction">
            <div>
              <div className="pill">Invoice #</div>
              <div className="prediction-main">{result.invoice_number}</div>
              <div className="muted">
                Client: {result.client_name || "—"}
              </div>
            </div>
            <div>
              <div>Service: {result.service_description || "—"}</div>
              <div>Amount: {result.amount ?? "—"}</div>
              <div>Currency: {result.currency || "—"}</div>
              <div>Due date: {result.due_date || "—"}</div>
            </div>
          </div>
          <div className="muted" style={{ marginTop: "0.5rem" }}>
            “{result.original_text}”
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h4>Stored Invoices</h4>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Invoice #</th>
                <th>Client</th>
                <th>Amount</th>
                <th>Currency</th>
                <th>Due</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.invoice_number}</td>
                  <td>{r.client_name}</td>
                  <td>{r.amount}</td>
                  <td>{r.currency}</td>
                  <td>{(r.due_date || "").slice(0, 10)}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan="6" className="muted">
                    No invoices yet.
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
