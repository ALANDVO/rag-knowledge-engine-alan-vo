import { useEffect, useState } from "react";

export default function Dashboard() {
  const [stats, setStats] = useState<{ total_vectors: number } | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/stats").then((r) => r.json()).then(setStats).catch(() => {});
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginTop: "1.5rem" }}>
        <div style={{ padding: "1.5rem", background: "#f1f5f9", borderRadius: 8 }}>
          <div style={{ fontSize: "0.85rem", color: "#64748b" }}>Total Vectors</div>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>{stats?.total_vectors ?? "..."}</div>
        </div>
        <div style={{ padding: "1.5rem", background: "#f1f5f9", borderRadius: 8 }}>
          <div style={{ fontSize: "0.85rem", color: "#64748b" }}>Status</div>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#22c55e" }}>Online</div>
        </div>
        <div style={{ padding: "1.5rem", background: "#f1f5f9", borderRadius: 8 }}>
          <div style={{ fontSize: "0.85rem", color: "#64748b" }}>Version</div>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>1.0.0</div>
        </div>
      </div>
    </div>
  );
}
