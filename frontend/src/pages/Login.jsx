import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../auth";
import { api, loginWithGoogle } from "../api";
import { GoogleLogin } from "@react-oauth/google";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await api.login(email, password);
      login(data.token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse) {
    setError("");
    try {
      const credential = credentialResponse.credential;
      const data = await loginWithGoogle(credential);
      login(data.token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  function handleGoogleError() {
    setError("Google login failed. Please try again.");
  }

  return (
    <div className="auth-page">
      <div className="auth-container auth-container-single">
        <div className="auth-single-panel">
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
            
            <div className="auth-google-wrapper">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                useOneTap
                theme="outline"
                size="large"
                text="continue_with"
                shape="pill"
                width="100%"
              />
            </div>
          </form>
          
          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register" className="auth-switch-link">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
