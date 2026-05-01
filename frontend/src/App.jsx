import {
  NavLink,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Expenses from "./pages/Expenses.jsx";
import Invoices from "./pages/Invoices.jsx";
import Customers from "./pages/Customers.jsx";
import Products from "./pages/Products.jsx";
import Analytics from "./pages/Analytics.jsx";
import Chatbot from "./components/Chatbot.jsx";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/expenses", label: "Expenses" },
  { to: "/invoices", label: "Invoices" },
  { to: "/customers", label: "Customers" },
  { to: "/products", label: "Products" },
  { to: "/analytics", label: "Live Insights" },
];

export default function App() {
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
      </aside>

      <main className="main">
        <header className="topbar">
          <h2>LedgerLink Console</h2>
        </header>

        <section className="page">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/invoices" element={<Invoices />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/products" element={<Products />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </section>
      </main>

      <Chatbot />
    </div>
  );
}