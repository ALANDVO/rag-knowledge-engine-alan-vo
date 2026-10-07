import { useState } from "react";

export default function Documents() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setError(null);
    try {
      const r = await fetch("http://localhost:8000/api/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      });
      const data = await r.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <div>
      <h1>Documents</h1>
      <div style={{ marginTop: "1rem", maxWidth: 600 }}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Document title"
          style={{ width: "100%", padding: "0.5rem", marginBottom: 8, border: "1px solid #cbd5e1", borderRadius: 6 }}
        />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste document content..."
          rows={8}
          style={{ width: "100%", padding: "0.5rem", marginBottom: 8, border: "1px solid #cbd5e1", borderRadius: 6 }}
        />
        <button onClick={submit} style={{ padding: "0.5rem 1.5rem", background: "#3b82f6", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" }}>
          Ingest Document
        </button>
        {error && <p style={{ color: "#ef4444", marginTop: 8 }}>{error}</p>}
        {result && <pre style={{ marginTop: 8, background: "#f1f5f9", padding: 12, borderRadius: 6 }}>{result}</pre>}
      </div>
    </div>
  );
}
