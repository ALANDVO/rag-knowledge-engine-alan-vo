import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useEffect, useState, createContext, useContext } from "react";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import DocumentDetail from "./pages/DocumentDetail";
import Query from "./pages/Query";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Sidebar from "./components/Sidebar";
export const AuthContext = createContext(null);
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
}
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const fetchUser = async () => {
        try {
            const resp = await fetch("/api/auth/me", { credentials: "include" });
            if (resp.ok) {
                const data = await resp.json();
                setUser(data);
            }
            else {
                setUser(null);
            }
        }
        catch {
            setUser(null);
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        fetchUser();
    }, []);
    const login = () => {
        window.location.href = "/api/auth/login";
    };
    const logout = async () => {
        await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
        setUser(null);
    };
    const refreshUser = fetchUser;
    return (_jsx(AuthContext.Provider, { value: { user, loading, login, logout, refreshUser }, children: children }));
}
function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    const location = useLocation();
    if (loading) {
        return (_jsx("div", { style: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }, children: _jsx("div", { children: "Loading..." }) }));
    }
    if (!user) {
        return _jsx(Navigate, { to: "/login", state: { from: location }, replace: true });
    }
    return children;
}
export default function App() {
    return (_jsx(BrowserRouter, { children: _jsx(AuthProvider, { children: _jsxs("div", { style: { display: "flex", minHeight: "100vh" }, children: [_jsx(Sidebar, {}), _jsx("main", { style: { flex: 1, padding: "2rem" }, children: _jsxs(Routes, { children: [_jsx(Route, { path: "/login", element: _jsx(Login, {}) }), _jsx(Route, { path: "/dashboard", element: _jsx(ProtectedRoute, { children: _jsx(Dashboard, {}) }) }), _jsx(Route, { path: "/documents", element: _jsx(ProtectedRoute, { children: _jsx(Documents, {}) }) }), _jsx(Route, { path: "/documents/:docId", element: _jsx(ProtectedRoute, { children: _jsx(DocumentDetail, {}) }) }), _jsx(Route, { path: "/query", element: _jsx(ProtectedRoute, { children: _jsx(Query, {}) }) }), _jsx(Route, { path: "/settings", element: _jsx(ProtectedRoute, { children: _jsx(Settings, {}) }) }), _jsx(Route, { path: "/", element: _jsx(Navigate, { to: "/dashboard" }) })] }) })] }) }) }));
}
