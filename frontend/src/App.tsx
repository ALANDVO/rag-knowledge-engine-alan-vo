import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useEffect, useState, createContext, useContext } from "react";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import DocumentDetail from "./pages/DocumentDetail";
import Query from "./pages/Query";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Sidebar from "./components/Sidebar";

interface User {
  sub: string;
  email?: string;
  name?: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  csrfToken: string | null;
  refreshCsrfToken: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  const fetchUser = async () => {
    try {
      const resp = await fetch("/api/auth/me", { credentials: "include" });
      if (resp.ok) {
        const data = await resp.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshCsrfToken = async () => {
    try {
      const r = await fetch("/api/auth/csrf", { credentials: "include" });
      if (r.ok) {
        const data = await r.json();
        setCsrfToken(data.csrf_token);
      }
    } catch (e) {
      console.error("Failed to load CSRF token", e);
    }
  };

  useEffect(() => {
    fetchUser();
    refreshCsrfToken();
  }, []);

  const login = () => {
    window.location.href = "/api/auth/login";
  };

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    setUser(null);
    setCsrfToken(null);
  };

  const refreshUser = fetchUser;

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser, csrfToken, refreshCsrfToken }}>
      {children}
    </AuthContext.Provider>
  );
}

function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div style={{ minHeight: "100vh", display: "flex", background: "#f8f9fa" }}>
          <Sidebar />
          <div style={{ flex: 1, marginLeft: 260, minHeight: "100vh" }}>
            <header style={{ padding: "1rem 2rem", borderBottom: "1px solid #dee2e6", background: "white" }}>
              <h1 style={{ margin: 0, fontSize: "1.5rem" }}>RAG Knowledge Engine</h1>
            </header>
            <main style={{ padding: "2rem" }}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/documents"
                  element={
                    <ProtectedRoute>
                      <Documents />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/documents/:docId"
                  element={
                    <ProtectedRoute>
                      <DocumentDetail />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/query"
                  element={
                    <ProtectedRoute>
                      <Query />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <Settings />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
          </div>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
