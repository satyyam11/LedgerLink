import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Expenses() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [rows, setRows] = useState([]);

  async function loadExpenses() {
    try {
      const res = await api.getExpenses();
      setRows(res.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadExpenses();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError("");
    try {
      const res = await api.categorizeExpense(text.trim());
      setResult(res.data);
      setText("");
      await loadExpenses();
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h3>Expenses</h3>
      <p className="muted">
        Describe an expense in natural language. The AI will categorize and
        store it.
      </p>

      <form onSubmit={handleSubmit} className="card form">
        <label>Expense text</label>
        <textarea
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Bought uniform for 2500 rupees from Myntra"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Categorizing..." : "Categorize & Save"}
        </button>
        {error && <div className="error">{error}</div>}
      </form>

      {result && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <h4>Last Prediction</h4>
          <div className="prediction">
            <div>
              <div className="pill">Category</div>
              <div className="prediction-main">{result.category || "—"}</div>
              <div className="muted">
                Confidence: {result.confidence ?? "—"}
              </div>
            </div>
            <div>
              <div>Amount: {result.amount ?? "—"}</div>
              <div>Currency: {result.currency || "—"}</div>
              <div>Vendor: {result.vendor || "—"}</div>
              <div>Date: {result.date || "—"}</div>
            </div>
          </div>
          <div className="muted" style={{ marginTop: "0.5rem" }}>
            “{result.original_text}”
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h4>Stored Expenses</h4>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Text</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Vendor</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{(r.original_text || "").slice(0, 60)}</td>
                  <td>{r.category}</td>
                  <td>{r.amount}</td>
                  <td>{r.vendor}</td>
                  <td>{(r.date || "").slice(0, 10)}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan="6" className="muted">
                    No expenses yet. Try adding one above.
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
