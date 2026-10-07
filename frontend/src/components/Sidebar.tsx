import { Link, useLocation } from "react-router-dom";

const items = [
  { path: "/dashboard", label: "Dashboard" },
  { path: "/documents", label: "Documents" },
  { path: "/query", label: "Query" },
  { path: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const location = useLocation();
  return (
    <aside style={{ width: 220, background: "#1e293b", color: "#fff", padding: "1rem" }}>
      <h2 style={{ fontSize: "1.1rem", marginBottom: "1.5rem" }}>RAG Engine</h2>
      <nav>
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
    </aside>
  );
}
