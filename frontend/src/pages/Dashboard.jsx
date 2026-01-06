import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Dashboard() {
  const [stats, setStats] = useState({
    expenses: 0,
    invoices: 0,
    customers: 0,
    products: 0
  });
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    async function load() {
      try {
        const [health, expenses, invoices, customers, products] =
          await Promise.all([
            api.health().catch(() => null),
            api.getExpenses(),
            api.getInvoices(),
            api.getCustomers(),
            api.getProducts()
          ]);

        if (health) {
          setStatus(" Quick snapshot of your workspace.");
        } else {
          setStatus("Backend reachable (no /health).");
        }

        setStats({
          expenses: expenses.data?.length || 0,
          invoices: invoices.data?.length || 0,
          customers: customers.data?.length || 0,
          products: products.data?.length || 0
        });
      } catch (err) {
        console.error(err);
        setStatus("Error talking to backend: " + err.message);
      }
    }
    load();
  }, []);

  return (
    <div>
      <h3>Overview</h3>
      <p className="muted">{status}</p>

      <div className="grid">
        <StatCard label="Expenses" value={stats.expenses} />
        <StatCard label="Invoices" value={stats.invoices} />
        <StatCard label="Customers" value={stats.customers} />
        <StatCard label="Products" value={stats.products} />
      </div>

      <p className="muted" style={{ marginTop: "1.5rem" }}>
        Tip: open the Expenses page, submit a few expenses, and then come back
        here to see the counts increase.
      </p>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
