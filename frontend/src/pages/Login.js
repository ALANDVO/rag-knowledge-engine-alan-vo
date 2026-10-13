import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
export default function Login() {
    const navigate = useNavigate();
    const location = useLocation();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
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
            }
            else {
                setLoading(false);
            }
        }
        catch {
            setLoading(false);
        }
    };
    const handleLogin = () => {
        // Redirect to backend login endpoint which initiates OIDC flow
        window.location.href = "/api/auth/login";
    };
    if (loading) {
        return (_jsx("div", { style: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }, children: _jsx("div", { children: "Loading..." }) }));
    }
    return (_jsxs("div", { style: { maxWidth: "400px", margin: "4rem auto", padding: "2rem", textAlign: "center" }, children: [_jsx("h1", { children: "RAG Knowledge Engine" }), _jsx("p", { style: { color: "#666", marginBottom: "2rem" }, children: "Sign in with your organizational account to access the knowledge base." }), error && (_jsx("div", { style: { color: "#dc3545", marginBottom: "1rem", padding: "0.75rem", background: "#fff5f5", borderRadius: "4px" }, children: error })), _jsx("button", { onClick: handleLogin, style: {
                    padding: "0.75rem 1.5rem",
                    fontSize: "1rem",
                    backgroundColor: "#0066cc",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                }, children: "Sign in with Keycloak" }), _jsx("p", { style: { marginTop: "1.5rem", fontSize: "0.875rem", color: "#666" }, children: "Demo mode: Set DEMO_MODE=true in backend .env to bypass authentication." })] }));
}
