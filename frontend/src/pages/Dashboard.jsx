import { useEffect, useState, useMemo } from "react";
import { api } from "../api.js";
import { Skeleton, SkeletonCard } from "../components/Skeleton.jsx";

export default function Dashboard() {
  const [stats, setStats] = useState({
    expenses: 0,
    invoices: 0,
    customers: 0,
    products: 0,
    outstanding: 0,
    paid: 0
  });
  const [expensesData, setExpensesData] = useState([]);
  const [status, setStatus] = useState("Checking backend...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [health, expenses, invoices, customers, products] =
          await Promise.all([
            api.health().catch(() => null),
            api.getExpenses().catch(() => []),
            api.getInvoices().catch(() => []),
            api.getCustomers().catch(() => []),
            api.getProducts().catch(() => [])
          ]);

        if (health) {
          setStatus(" Quick snapshot of your workspace.");
        } else {
          setStatus("Backend reachable (no /health).");
        }

        setExpensesData(expenses || []);
        setStats({
          expenses: expenses?.length || 0,
          invoices: invoices?.length || 0,
          customers: customers?.success ? customers.data.length : (customers?.length || 0),
          products: products?.success ? products.data.length : (products?.length || 0)
        });
      } catch (err) {
        console.error(err);
        setStatus("Error talking to backend: " + err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const chartData = useMemo(() => {
    const cats = {};
    expensesData.forEach(e => {
      const c = e.category || "Uncategorized";
      cats[c] = (cats[c] || 0) + (Number(e.amount) || 0);
    });
    return Object.entries(cats).map(([name, value]) => ({ name, value }));
  }, [expensesData]);

  return (
    <div>
      <h3>Overview</h3>
      {loading ? (
        <Skeleton className="skeleton-text" style={{ width: '30%', height: '1.2rem', marginBottom: '1.5rem' }} />
      ) : (
        <p className="muted">{status}</p>
      )}

      <div className="grid">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <StatCard label="Expenses" value={stats.expenses} />
            <StatCard label="Invoices" value={stats.invoices} />
            <StatCard label="Customers" value={stats.customers} />
            <StatCard label="Products" value={stats.products} />
          </>
        )}
      </div>

      <div className="grid" style={{ marginTop: '2rem', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <h4>Expenses by Category</h4>
          <div style={{ marginTop: '0.75rem' }}>
            {loading ? (
              <div style={{ height: '150px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <Skeleton className="skeleton-row" style={{ width: '90%' }} />
                <Skeleton className="skeleton-row" style={{ width: '70%' }} />
                <Skeleton className="skeleton-row" style={{ width: '80%' }} />
              </div>
            ) : chartData.length > 0 ? (
              <div className="mini-chart">
                {chartData.map((d, i) => {
                  const max = Math.max(...chartData.map(x => x.value));
                  const width = (d.value / max) * 100;
                  return (
                    <div key={i} style={{ marginBottom: '0.75rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.2rem' }}>
                        <span>{d.name}</span>
                        <span className="muted">₹{d.value.toLocaleString()}</span>
                      </div>
                      <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ 
                          height: '100%', 
                          width: `${width}%`, 
                          background: 'linear-gradient(90deg, #6366f1, #a855f7)',
                          borderRadius: '4px'
                        }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="muted">No data to display.</p>
            )}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <h4>Recent Activity</h4>
          <div style={{ marginTop: '0.75rem' }}>
            {loading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <Skeleton className="skeleton-text" />
                <Skeleton className="skeleton-text" />
                <Skeleton className="skeleton-text" />
              </div>
            ) : expensesData.length > 0 ? (
              <div className="activity-list">
                {expensesData.slice(-4).reverse().map((e, i) => (
                  <div key={i} style={{ paddingBottom: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.05)', marginBottom: '0.5rem' }}>
                    <div style={{ fontSize: '0.85rem' }}>{e.vendor}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }} className="muted">
                      <span>{e.category}</span>
                      <span>₹{e.amount}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No recent activity.</p>
            )}
          </div>
        </div>
      </div>

      <p className="muted" style={{ marginTop: "1.5rem" }}>
        Tip: open the Expenses page, submit a few expenses, and then come back
        here to see the counts increase.
      </p>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div className="card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={color ? { background: 'none', WebkitTextFillColor: color, color: color } : {}}>{value}</div>
    </div>
  );
}
