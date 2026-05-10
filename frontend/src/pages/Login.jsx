import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { saveToken } from "../auth";
import { api } from "../api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await api.login(email, password);
      saveToken(data.token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleLogin() {
    setGoogleLoading(true);
    setError("");
    
    try {
      alert("Google OAuth coming soon! For now, please use email/password login.");
    } catch (err) {
      setError(err.message);
    } finally {
      setGoogleLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-left">
          <div className="auth-brand">
            <div className="auth-brand-logo">Ł</div>
            <h1 className="auth-brand-name">LedgerLink</h1>
          </div>
          
          <h1 className="auth-welcome">Welcome Back!</h1>
          <p className="auth-subtitle">Login to continue</p>
          
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-input-group">
              <label>Email</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">✉️</span>
                <input
                  type="email"
                  required
                  className="auth-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                />
              </div>
            </div>
            
            <div className="auth-input-group">
              <label>Password</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">🔒</span>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  className="auth-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                />
                <span 
                  className="auth-input-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? "👁️" : "👁️‍🗨️"}
                </span>
              </div>
            </div>
            
            <div className="auth-options">
              <label className="auth-remember">
                <input 
                  type="checkbox" 
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                Remember me
              </label>
              <a href="#" className="auth-forgot">Forgot Password?</a>
            </div>
            
            {error && <div className="auth-error">{error}</div>}
            
            <button type="submit" className="auth-btn" disabled={loading}>
              {loading ? "Logging in..." : "Login"}
            </button>
            
            <div className="auth-divider">
              <div className="auth-divider-line"></div>
              <span className="auth-divider-text">or</span>
              <div className="auth-divider-line"></div>
            </div>
            
            <button 
              type="button" 
              className="auth-oauth-btn"
              onClick={handleGoogleLogin}
              disabled={googleLoading}
            >
              <span className="auth-oauth-icon">🌐</span>
              {googleLoading ? "Connecting..." : "Continue with Google"}
            </button>
          </form>
          
          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register" className="auth-switch-link">Sign up</Link>
          </p>
        </div>
        
        <div className="auth-right">
          <h2>Create Account</h2>
          <p className="auth-right-subtitle">Register to get started</p>
          
          <div className="auth-form">
            <div className="auth-input-group">
              <label>Full Name</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">👤</span>
                <input
                  type="text"
                  className="auth-input"
                  placeholder="Enter your name"
                  disabled
                />
              </div>
            </div>
            
            <div className="auth-input-group">
              <label>Email</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">✉️</span>
                <input
                  type="email"
                  className="auth-input"
                  placeholder="Enter your email"
                  disabled
                />
              </div>
            </div>
            
            <div className="auth-input-group">
              <label>Password</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">🔒</span>
                <input
                  type="password"
                  className="auth-input"
                  placeholder="Create a password"
                  disabled
                />
              </div>
            </div>
            
            <div className="auth-input-group">
              <label>Confirm Password</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">🔒</span>
                <input
                  type="password"
                  className="auth-input"
                  placeholder="Confirm your password"
                  disabled
                />
              </div>
            </div>
            
            <label className="auth-terms">
              <input type="checkbox" disabled />
              <span>I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a></span>
            </label>
            
            <button type="button" className="auth-btn" disabled style={{ opacity: 0.5 }}>
              Register
            </button>
          </div>
          
          <p className="auth-switch">
            Already have an account?{" "}
            <Link to="/login" className="auth-switch-link">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
