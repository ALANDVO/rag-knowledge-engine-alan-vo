import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

export default function Documents() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<Array<{doc_id: string; title: string; source: string; chunks: number}>>([]);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setError(null);
    setLoading(true);
    try {
      const r = await fetch("http://localhost:8000/api/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Failed to ingest");
      setResult(JSON.stringify(data, null, 2));
      setTitle("");
      setContent("");
      await loadDocuments();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (title) formData.append("title", title);
      const r = await fetch("http://localhost:8000/api/documents/upload", {
        method: "POST",
        body: formData,
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Failed to upload");
      setResult(JSON.stringify(data, null, 2));
      setTitle("");
      setFile(null);
      await loadDocuments();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const r = await fetch("http://localhost:8000/api/documents");
      const data = await r.json();
      setDocuments(data.documents?.map((doc_id: string) => ({ doc_id })) || []);
    } catch (e) {
      console.error("Failed to load documents", e);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div>
      <h1>Documents</h1>
      <div style={{ marginTop: "1rem", maxWidth: 800 }}>
        <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }}>
          <h3>Ingest Text</h3>
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
          <button onClick={submit} disabled={loading || !title || !content} style={{ padding: "0.5rem 1.5rem", background: "#3b82f6", color: "#fff", border: "none", borderRadius: 6, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.7 : 1 }}>
            {loading ? "Ingesting..." : "Ingest Document"}
          </button>
        </div>

        <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }}>
          <h3>Upload File</h3>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            accept=".txt,.md,.html,.pdf,.docx"
            style={{ marginBottom: 8 }}
          />
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Optional title (defaults to filename)"
            style={{ width: "100%", padding: "0.5rem", marginBottom: 8, border: "1px solid #cbd5e1", borderRadius: 6 }}
          />
          <button onClick={uploadFile} disabled={loading || !file} style={{ padding: "0.5rem 1.5rem", background: "#10b981", color: "#fff", border: "none", borderRadius: 6, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.7 : 1 }}>
            {loading ? "Uploading..." : "Upload Document"}
          </button>
          {file && <p style={{ marginTop: 8, fontSize: "0.85rem", color: "#64748b" }}>Selected: {file.name} ({file.size} bytes)</p>}
        </div>

        {error && <p style={{ color: "#ef4444", marginTop: 8 }}>{error}</p>}
        {result && <pre style={{ marginTop: 8, background: "#f1f5f9", padding: 12, borderRadius: 6 }}>{result}</pre>}

        <div style={{ marginTop: "2rem" }}>
          <h3>Documents</h3>
          {documents.length === 0 ? (
            <p style={{ color: "#64748b" }}>No documents yet. Ingest or upload a document to get started.</p>
          ) : (
            <ul style={{ listStyle: "none", padding: 0 }}>
              {documents.map((doc) => (
                <li key={doc.doc_id} style={{ padding: "0.75rem", background: "#f1f5f9", borderRadius: 6, marginBottom: 8 }}>
                  <Link to={`/documents/${doc.doc_id}`} style={{ textDecoration: "none", color: "inherit" }}>
                    <strong>{doc.doc_id}</strong>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}