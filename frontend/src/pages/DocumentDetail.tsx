import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";

export default function DocumentDetail() {
  const { docId } = useParams<{ docId: string }>();
  const navigate = useNavigate();
  const [document, setDocument] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocument = async () => {
      if (!docId) return;
      setLoading(true);
      try {
        const r = await fetch(`http://localhost:8000/api/documents/${docId}`);
        if (!r.ok) throw new Error("Document not found");
        const data = await r.json();
        setDocument(data);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    };
    fetchDocument();
  }, [docId]);

  const handleDelete = async () => {
    if (!docId || !window.confirm(`Delete document "${docId}" and all its chunks? This cannot be undone.`)) {
      return;
    }
    setDeleting(true);
    setDeleteError(null);
    try {
      const r = await fetch(`http://localhost:8000/api/documents/${docId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: "Delete failed" }));
        throw new Error(err.detail || "Delete failed");
      }
      navigate("/documents");
    } catch (e) {
      setDeleteError(String(e));
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <p>Loading document...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "2rem", textAlign: "center", color: "#ef4444" }}>
        <p>{error}</p>
        <Link to="/documents" style={{ marginTop: "1rem", display: "inline-block" }}>
          Back to Documents
        </Link>
      </div>
    );
  }

  if (!document) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <p>Document not found</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1>{document.doc_id}</h1>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <Link to="/documents" style={{ color: "#3b82f6" }}>
            ← Back to Documents
          </Link>
          <button
            onClick={handleDelete}
            disabled={deleting}
            style={{
              padding: "0.5rem 1rem",
              background: "#ef4444",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: deleting ? "not-allowed" : "pointer",
              opacity: deleting ? 0.7 : 1,
            }}
          >
            {deleting ? "Deleting..." : "Delete Document"}
          </button>
        </div>
      </div>

      {deleteError && (
        <div style={{ marginBottom: "1rem", padding: "1rem", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 6, color: "#dc2626" }}>
          {deleteError}
        </div>
      )}

      <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
          <div>
            <div style={{ fontSize: "0.85rem", color: "#64748b" }}>Total Chunks</div>
            <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{document.total_chunks}</div>
          </div>
          <div>
            <div style={{ fontSize: "0.85rem", color: "#64748b" }}>Chunk IDs</div>
            <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{document.chunks.length}</div>
          </div>
        </div>
      </div>

      <div>
        <h3>Chunks</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {document.chunks.map((chunk: any, index: number) => (
            <div
              key={chunk.chunk_id}
              style={{
                padding: "1rem",
                background: "#fff",
                border: "1px solid #e2e8f0",
                borderRadius: 8,
                maxHeight: "300px",
                overflow: "auto",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <strong>Chunk #{chunk.index}</strong>
                <code style={{ fontSize: "0.75rem", background: "#f1f5f9", padding: "0.25rem 0.5rem", borderRadius: 4 }}>
                  {chunk.chunk_id}
                </code>
              </div>
              <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.9rem", color: "#334155" }}>
                {chunk.text}
              </pre>
              {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
                <details style={{ marginTop: "0.5rem" }}>
                  <summary style={{ cursor: "pointer", color: "#64748b", fontSize: "0.85rem" }}>Metadata</summary>
                  <pre style={{ marginTop: "0.5rem", fontSize: "0.75rem", background: "#f8fafc", padding: "0.5rem", borderRadius: 4 }}>
                    {JSON.stringify(chunk.metadata, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}