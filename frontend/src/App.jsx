import {
  NavLink,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { useAuth } from "./auth";
import { useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import Expenses from "./pages/Expenses.jsx";
import Invoices from "./pages/Invoices.jsx";
import Customers from "./pages/Customers.jsx";
import Products from "./pages/Products.jsx";
import Analytics from "./pages/Analytics.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Chatbot from "./components/Chatbot.jsx";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/expenses", label: "Expenses" },
  { to: "/invoices", label: "Invoices" },
  { to: "/customers", label: "Customers" },
  { to: "/products", label: "Products" },
  { to: "/analytics", label: "Live Insights" },
];

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AuthRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return children;
}

export default function App() {
  const { isAuthenticated, logout, loading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Show loading state while checking auth
  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#fff' }}>Loading...</div>;
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={
          <AuthRoute>
            <Login />
          </AuthRoute>
        } />
        <Route path="/register" element={
          <AuthRoute>
            <Register />
          </AuthRoute>
        } />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <div className="app-root">
        {/* Parallax rupee animation */}
  <div className="rupee-layer layer1"></div>
  <div className="rupee-layer layer2"></div>
  <div className="rupee-layer layer3"></div>

  {/* Mobile overlay */}
  {sidebarOpen && (
    <div 
      className="sidebar-overlay" 
      onClick={() => setSidebarOpen(false)}
    />
  )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <NavLink to="/" className="brand" onClick={() => setSidebarOpen(false)}>
          <div className="brand-logo">Ł</div>
          <div className="brand-text">
            <h1>LedgerLink</h1>
            <p>AI-based ERP system</p>
          </div>
        </NavLink>

        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                "nav-link" + (isActive ? " nav-link-active" : "")
              }
              onClick={() => setSidebarOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </aside>

      <main className="main">
        <header className="topbar">
          <button 
            className="mobile-menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h2>LedgerLink Console</h2>
        </header>

        <section className="page">
          <Routes>
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/expenses" element={
              <ProtectedRoute>
                <Expenses />
              </ProtectedRoute>
            } />
            <Route path="/invoices" element={
              <ProtectedRoute>
                <Invoices />
              </ProtectedRoute>
            } />
            <Route path="/customers" element={
              <ProtectedRoute>
                <Customers />
              </ProtectedRoute>
            } />
            <Route path="/products" element={
              <ProtectedRoute>
                <Products />
              </ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            } />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </section>
      </main>

      <Chatbot />
    </div>
  );
}
