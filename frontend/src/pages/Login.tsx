import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

interface User {
  sub: string;
  email?: string;
  name?: string;
  roles: string[];
}

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if we're returning from OIDC callback
    const params = new URLSearchParams(location.search);
    const errorParam = params.get("error");
    if (errorParam) {
      setError(`Authentication failed: ${errorParam}`);
      setLoading(false);
      return;
    }

    // Check if already authenticated by calling /api/auth/me
    checkAuth();
  }, [location.search]);

  const checkAuth = async () => {
    try {
      const resp = await fetch("/api/auth/me", { credentials: "include" });
      if (resp.ok) {
        // Already authenticated, redirect to intended page or dashboard
        const from = location.state?.from?.pathname || "/dashboard";
        navigate(from, { replace: true });
      } else {
        setLoading(false);
      }
    } catch {
      setLoading(false);
    }
  };

  const handleLogin = () => {
    // Redirect to backend login endpoint which initiates OIDC flow
    window.location.href = "/api/auth/login";
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "400px", margin: "4rem auto", padding: "2rem", textAlign: "center" }}>
      <h1>RAG Knowledge Engine</h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>
        Sign in with your organizational account to access the knowledge base.
      </p>
      {error && (
        <div style={{ color: "#dc3545", marginBottom: "1rem", padding: "0.75rem", background: "#fff5f5", borderRadius: "4px" }}>
          {error}
        </div>
      )}
      <button
        onClick={handleLogin}
        style={{
          padding: "0.75rem 1.5rem",
          fontSize: "1rem",
          backgroundColor: "#0066cc",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Sign in with Keycloak
      </button>
      <p style={{ marginTop: "1.5rem", fontSize: "0.875rem", color: "#666" }}>
        Demo mode: Set DEMO_MODE=true in backend .env to bypass authentication.
      </p>
    </div>
  );
}