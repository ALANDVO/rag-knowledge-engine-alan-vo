import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../App";

const items = [
  { path: "/dashboard", label: "Dashboard" },
  { path: "/documents", label: "Documents" },
  { path: "/query", label: "Query" },
  { path: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuth();

  return (
    <aside style={{ width: 220, background: "#1e293b", color: "#fff", padding: "1rem", display: "flex", flexDirection: "column" }}>
      <h2 style={{ fontSize: "1.1rem", marginBottom: "1.5rem" }}>RAG Engine</h2>
      <nav style={{ flex: 1 }}>
        {items.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              display: "block",
              padding: "0.5rem 0.75rem",
              borderRadius: 6,
              color: location.pathname === item.path ? "#fff" : "#94a3b8",
              background: location.pathname === item.path ? "#334155" : "transparent",
              textDecoration: "none",
              marginBottom: 4,
            }}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      {user && (
        <div style={{ borderTop: "1px solid #334155", paddingTop: "1rem", marginTop: "auto" }}>
          <div style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "0.25rem" }}>
            {user.name || user.email || user.sub}
          </div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "0.75rem" }}>
            Roles: {user.roles.join(", ")}
          </div>
          <button
            onClick={() => logout()}
            style={{
              width: "100%",
              padding: "0.5rem",
              background: "transparent",
              color: "#94a3b8",
              border: "1px solid #334155",
              borderRadius: 6,
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            Logout
          </button>
        </div>
      )}
    </aside>
  );
}