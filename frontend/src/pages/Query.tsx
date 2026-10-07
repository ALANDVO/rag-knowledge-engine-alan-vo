import { useState } from "react";

export default function Query() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<any[] | null>(null);

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

  return (
    <div>
      <h1>Query</h1>
      <div style={{ marginTop: "1rem", maxWidth: 700 }}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your knowledge base..."
          rows={3}
          style={{ width: "100%", padding: "0.5rem", marginBottom: 8, border: "1px solid #cbd5e1", borderRadius: 6 }}
        />
        <button onClick={submit} style={{ padding: "0.5rem 1.5rem", background: "#3b82f6", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" }}>
          Search
        </button>
        {answer && (
          <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }}>
            <h3>Answer</h3>
            <p>{answer}</p>
            {sources && (
              <div>
                <h4>Sources</h4>
                {sources.map((s, i) => (
                  <div key={i} style={{ padding: 8, background: "#e2e8f0", borderRadius: 6, marginBottom: 6 }}>
                    <strong>{s.doc_id}</strong> (score: {s.score})
                    <p style={{ fontSize: "0.85rem", color: "#64748b" }}>{s.text_preview}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
