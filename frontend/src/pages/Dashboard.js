import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
export default function Dashboard() {
    const [stats, setStats] = useState(null);
    useEffect(() => {
        fetch("http://localhost:8000/api/stats").then((r) => r.json()).then(setStats).catch(() => { });
    }, []);
    return (_jsxs("div", { children: [_jsx("h1", { children: "Dashboard" }), _jsxs("div", { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginTop: "1.5rem" }, children: [_jsxs("div", { style: { padding: "1.5rem", background: "#f1f5f9", borderRadius: 8 }, children: [_jsx("div", { style: { fontSize: "0.85rem", color: "#64748b" }, children: "Total Vectors" }), _jsx("div", { style: { fontSize: "2rem", fontWeight: 700 }, children: stats?.total_vectors ?? "..." })] }), _jsxs("div", { style: { padding: "1.5rem", background: "#f1f5f9", borderRadius: 8 }, children: [_jsx("div", { style: { fontSize: "0.85rem", color: "#64748b" }, children: "Status" }), _jsx("div", { style: { fontSize: "2rem", fontWeight: 700, color: "#22c55e" }, children: "Online" })] }), _jsxs("div", { style: { padding: "1.5rem", background: "#f1f5f9", borderRadius: 8 }, children: [_jsx("div", { style: { fontSize: "0.85rem", color: "#64748b" }, children: "Version" }), _jsx("div", { style: { fontSize: "2rem", fontWeight: 700 }, children: "1.0.0" })] })] })] }));
}
