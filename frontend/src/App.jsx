import {
  NavLink,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { isLoggedIn, clearToken } from "./auth";
import { useState, useEffect } from "react";
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
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AuthRoute({ children }) {
  if (isLoggedIn()) {
    return <Navigate to="/" replace />;
  }
  return children;
}

export default function App() {
  const [authState, setAuthState] = useState(isLoggedIn());

  useEffect(() => {
    setAuthState(isLoggedIn());
  }, []);

  const handleLogout = () => {
    clearToken();
    setAuthState(false);
  };

  if (!authState) {
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


      <aside className="sidebar">
        <NavLink to="/" className="brand">
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
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </aside>

      <main className="main">
        <header className="topbar">
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
