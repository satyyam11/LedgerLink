import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { saveToken } from "../auth";
import { api } from "../api";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!agreeTerms) {
      setError("Please agree to the Terms of Service and Privacy Policy");
      return;
    }

    setLoading(true);

    try {
      const data = await api.register(email, password);
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
      alert("Google OAuth coming soon! For now, please use email/password registration.");
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
          
          <div className="auth-form">
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
                  placeholder="Enter your password"
                  disabled
                />
              </div>
            </div>
            
            <div className="auth-options">
              <label className="auth-remember">
                <input type="checkbox" disabled />
                Remember me
              </label>
              <a href="#" className="auth-forgot">Forgot Password?</a>
            </div>
            
            <button type="button" className="auth-btn" disabled style={{ opacity: 0.5 }}>
              Login
            </button>
            
            <div className="auth-divider">
              <div className="auth-divider-line"></div>
              <span className="auth-divider-text">or</span>
              <div className="auth-divider-line"></div>
            </div>
            
            <button 
              type="button" 
              className="auth-oauth-btn"
              disabled
            >
              <span className="auth-oauth-icon">🌐</span>
              Continue with Google
            </button>
          </div>
          
          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register" className="auth-switch-link">Sign up</Link>
          </p>
        </div>
        
        <div className="auth-right">
          <h2>Create Account</h2>
          <p className="auth-right-subtitle">Register to get started</p>
          
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-input-group">
              <label>Full Name</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">👤</span>
                <input
                  type="text"
                  required
                  className="auth-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your name"
                />
              </div>
            </div>
            
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
                  placeholder="Create a password"
                />
                <span 
                  className="auth-input-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? "👁️" : "👁️‍🗨️"}
                </span>
              </div>
            </div>
            
            <div className="auth-input-group">
              <label>Confirm Password</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">🔒</span>
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  required
                  className="auth-input"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                />
                <span 
                  className="auth-input-password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? "👁️" : "👁️‍🗨️"}
                </span>
              </div>
            </div>
            
            <label className="auth-terms">
              <input 
                type="checkbox"
                checked={agreeTerms}
                onChange={(e) => setAgreeTerms(e.target.checked)}
              />
              <span>I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a></span>
            </label>
            
            {error && <div className="auth-error">{error}</div>}
            
            <button type="submit" className="auth-btn" disabled={loading}>
              {loading ? "Creating account..." : "Register"}
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
            Already have an account?{" "}
            <Link to="/login" className="auth-switch-link">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
