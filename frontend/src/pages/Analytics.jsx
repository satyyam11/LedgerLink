import { useEffect, useState, useMemo } from "react";
import { api } from "../api.js";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar, Cell
} from 'recharts';
import { Skeleton } from "../components/Skeleton.jsx";

export default function Analytics() {
  const [data, setData] = useState({ expenses: [], invoices: [] });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const loadData = async () => {
    try {
      const [expenses, invoices] = await Promise.all([
        api.getExpenses().catch(() => []),
        api.getInvoices().catch(() => [])
      ]);
      
      setData({ 
        expenses: Array.isArray(expenses) ? expenses : [], 
        invoices: Array.isArray(invoices) ? invoices : (invoices?.data || [])
      });
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Failed to fetch analytics data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Live polling every 10 seconds
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const chartData = useMemo(() => {
    const dailyMap = {};

    // Process Expenses
    data.expenses.forEach(e => {
      const date = (e.date || "").slice(0, 10);
      if (!date) return;
      if (!dailyMap[date]) dailyMap[date] = { date, expense: 0, invoice: 0 };
      dailyMap[date].expense += Number(e.amount) || 0;
    });

    // Process Invoices
    data.invoices.forEach(i => {
      const date = (i.due || i.due_date || "").slice(0, 10);
      if (!date) return;
      if (!dailyMap[date]) dailyMap[date] = { date, expense: 0, invoice: 0 };
      dailyMap[date].invoice += Number(i.amount) || 0;
    });

    return Object.values(dailyMap).sort((a, b) => a.date.localeCompare(b.date)).slice(-7);
  }, [data]);

  if (loading && chartData.length === 0) {
    return (
      <div className="page">
        <h3>Live Insights</h3>
        <div className="card" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Skeleton style={{ width: '90%', height: '80%' }} />
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h3>Live Insights</h3>
          <p className="muted">Real-time visualization of your cash flow.</p>
        </div>
        <div className="pill" style={{ fontSize: '0.7rem' }}>
          Live • Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1fr', gap: '2rem' }}>
        {/* Main Trend Chart */}
        <div className="card" style={{ height: '450px', padding: '2rem' }}>
          <h4 style={{ marginBottom: '2rem' }}>Expense vs Revenue Trend</h4>
          <ResponsiveContainer width="100%" height="85%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="#94a3b8" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false} 
                dy={10}
              />
              <YAxis 
                stroke="#94a3b8" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false}
                tickFormatter={(val) => `₹${val}`}
              />
              <Tooltip 
                contentStyle={{ background: '#1e293b', border: '1px solid rgba(148, 163, 184, 0.1)', borderRadius: '12px' }}
                itemStyle={{ fontSize: '0.85rem' }}
              />
              <Legend verticalAlign="top" height={36}/>
              <Line 
                name="Revenue (Invoices)"
                type="monotone" 
                dataKey="invoice" 
                stroke="#10b981" 
                strokeWidth={3} 
                dot={{ r: 4, fill: '#10b981' }}
                activeDot={{ r: 6 }}
                animationDuration={1500}
              />
              <Line 
                name="Expenses"
                type="monotone" 
                dataKey="expense" 
                stroke="#f43f5e" 
                strokeWidth={3} 
                dot={{ r: 4, fill: '#f43f5e' }}
                activeDot={{ r: 6 }}
                animationDuration={1500}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {/* Summary Stat 1 */}
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="stat-label">Total Revenue (Last 7 Days)</div>
            <div className="stat-value" style={{ color: '#10b981', background: 'none', WebkitTextFillColor: '#10b981' }}>
              ₹{chartData.reduce((acc, curr) => acc + curr.invoice, 0).toLocaleString()}
            </div>
          </div>
          {/* Summary Stat 2 */}
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="stat-label">Total Expenses (Last 7 Days)</div>
            <div className="stat-value" style={{ color: '#f43f5e', background: 'none', WebkitTextFillColor: '#f43f5e' }}>
              ₹{chartData.reduce((acc, curr) => acc + curr.expense, 0).toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
