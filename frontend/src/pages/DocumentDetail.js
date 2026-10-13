import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
export default function DocumentDetail() {
    const { docId } = useParams();
    const [document, setDocument] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    useEffect(() => {
        const fetchDocument = async () => {
            if (!docId)
                return;
            setLoading(true);
            try {
                const r = await fetch(`http://localhost:8000/api/documents/${docId}`);
                if (!r.ok)
                    throw new Error("Document not found");
                const data = await r.json();
                setDocument(data);
            }
            catch (e) {
                setError(String(e));
            }
            finally {
                setLoading(false);
            }
        };
        fetchDocument();
    }, [docId]);
    if (loading) {
        return (_jsx("div", { style: { padding: "2rem", textAlign: "center" }, children: _jsx("p", { children: "Loading document..." }) }));
    }
    if (error) {
        return (_jsxs("div", { style: { padding: "2rem", textAlign: "center", color: "#ef4444" }, children: [_jsx("p", { children: error }), _jsx(Link, { to: "/documents", style: { marginTop: "1rem", display: "inline-block" }, children: "Back to Documents" })] }));
    }
    if (!document) {
        return (_jsx("div", { style: { padding: "2rem", textAlign: "center" }, children: _jsx("p", { children: "Document not found" }) }));
    }
    return (_jsxs("div", { style: { maxWidth: 900, margin: "0 auto" }, children: [_jsxs("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }, children: [_jsx("h1", { children: document.doc_id }), _jsx(Link, { to: "/documents", style: { color: "#3b82f6" }, children: "\u2190 Back to Documents" })] }), _jsx("div", { style: { marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }, children: _jsxs("div", { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }, children: [_jsxs("div", { children: [_jsx("div", { style: { fontSize: "0.85rem", color: "#64748b" }, children: "Total Chunks" }), _jsx("div", { style: { fontSize: "1.5rem", fontWeight: 700 }, children: document.total_chunks })] }), _jsxs("div", { children: [_jsx("div", { style: { fontSize: "0.85rem", color: "#64748b" }, children: "Chunk IDs" }), _jsx("div", { style: { fontSize: "1.5rem", fontWeight: 700 }, children: document.chunks.length })] })] }) }), _jsxs("div", { children: [_jsx("h3", { children: "Chunks" }), _jsx("div", { style: { display: "flex", flexDirection: "column", gap: "0.75rem" }, children: document.chunks.map((chunk, index) => (_jsxs("div", { style: {
                                padding: "1rem",
                                background: "#fff",
                                border: "1px solid #e2e8f0",
                                borderRadius: 8,
                                maxHeight: "300px",
                                overflow: "auto",
                            }, children: [_jsxs("div", { style: { display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }, children: [_jsxs("strong", { children: ["Chunk #", chunk.index] }), _jsx("code", { style: { fontSize: "0.75rem", background: "#f1f5f9", padding: "0.25rem 0.5rem", borderRadius: 4 }, children: chunk.chunk_id })] }), _jsx("pre", { style: { whiteSpace: "pre-wrap", fontSize: "0.9rem", color: "#334155" }, children: chunk.text }), chunk.metadata && Object.keys(chunk.metadata).length > 0 && (_jsxs("details", { style: { marginTop: "0.5rem" }, children: [_jsx("summary", { style: { cursor: "pointer", color: "#64748b", fontSize: "0.85rem" }, children: "Metadata" }), _jsx("pre", { style: { marginTop: "0.5rem", fontSize: "0.75rem", background: "#f8fafc", padding: "0.5rem", borderRadius: 4 }, children: JSON.stringify(chunk.metadata, null, 2) })] }))] }, chunk.chunk_id))) })] })] }));
}
