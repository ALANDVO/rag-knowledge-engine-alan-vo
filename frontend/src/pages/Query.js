import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
export default function Query() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState(null);
    const [sources, setSources] = useState(null);
    const submit = async () => {
        setAnswer(null);
        setSources(null);
        const r = await fetch("http://localhost:8000/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        }).then((r) => r.json());
        setAnswer(r.answer);
        setSources(r.sources);
    };
    return (_jsxs("div", { children: [_jsx("h1", { children: "Query" }), _jsxs("div", { style: { marginTop: "1rem", maxWidth: 700 }, children: [_jsx("textarea", { value: question, onChange: (e) => setQuestion(e.target.value), placeholder: "Ask a question about your knowledge base...", rows: 3, style: { width: "100%", padding: "0.5rem", marginBottom: 8, border: "1px solid #cbd5e1", borderRadius: 6 } }), _jsx("button", { onClick: submit, style: { padding: "0.5rem 1.5rem", background: "#3b82f6", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" }, children: "Search" }), answer && (_jsxs("div", { style: { marginTop: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }, children: [_jsx("h3", { children: "Answer" }), _jsx("p", { children: answer }), sources && (_jsxs("div", { children: [_jsx("h4", { children: "Sources" }), sources.map((s, i) => (_jsxs("div", { style: { padding: 8, background: "#e2e8f0", borderRadius: 6, marginBottom: 6 }, children: [_jsx("strong", { children: s.doc_id }), " (score: ", s.score, ")", _jsx("p", { style: { fontSize: "0.85rem", color: "#64748b" }, children: s.text_preview })] }, i)))] }))] }))] })] }));
}
