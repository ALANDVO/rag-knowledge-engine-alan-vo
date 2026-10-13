import { useState, useEffect } from "react";
import { useAuth } from "../App";

interface LLMSettings {
  provider: string;
  model: string;
  embeddingModel: string;
  baseUrl: string;
  apiKeySet: boolean;
}

interface AppSettings {
  chunkSize: number;
  chunkOverlap: number;
  topK: number;
  requireSso: boolean;
  llm: LLMSettings;
}

export default function Settings() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<AppSettings>({
    chunkSize: 1024,
    chunkOverlap: 128,
    topK: 5,
    requireSso: true,
    llm: {
      provider: "openai",
      model: "gpt-4",
      embeddingModel: "text-embedding-3-small",
      baseUrl: "https://api.openai.com/v1",
      apiKeySet: false,
    },
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [csrfToken, setCsrfToken] = useState("");

  useEffect(() => {
    loadSettings();
    checkApiKey();
    loadCsrfToken();
  }, []);

  const apiFetch = async (url: string, options: RequestInit = {}) => {
    return fetch(url, {
      ...options,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
        ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}),
      },
    });
  };

  const loadSettings = async () => {
    try {
      const r = await apiFetch("/api/settings");
      if (r.ok) {
        const data = await r.json();
        setSettings((prev) => ({
          ...prev,
          chunkSize: data.chunk_size ?? prev.chunkSize,
          chunkOverlap: data.chunk_overlap ?? prev.chunkOverlap,
          topK: data.top_k ?? prev.topK,
          requireSso: data.require_sso ?? prev.requireSso,
          llm: {
            ...prev.llm,
            model: data.llm_model ?? prev.llm.model,
            embeddingModel: data.embedding_model ?? prev.llm.embeddingModel,
          },
        }));
      }
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  };

  const checkApiKey = async () => {
    try {
      const r = await apiFetch("/api/settings/api-key-status");
      if (r.ok) {
        const data = await r.json();
        setSettings((prev) => ({ ...prev, llm: { ...prev.llm, apiKeySet: data.set } }));
      }
    } catch (e) {
      console.error("Failed to check API key", e);
    }
  };
  const loadCsrfToken = async () => {
    try {
      const r = await fetch("/api/auth/csrf", { credentials: "include" });
      if (r.ok) {
        const data = await r.json();
        setCsrfToken(data.csrf_token);
      }
    } catch (e) {
      console.error("Failed to load CSRF token", e);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const payload = {
        chunk_size: settings.chunkSize,
        chunk_overlap: settings.chunkOverlap,
        top_k: settings.topK,
        require_sso: settings.requireSso,
        llm_model: settings.llm.model,
        embedding_model: settings.llm.embeddingModel,
        llm_base_url: settings.llm.baseUrl,
      };
      if (apiKey) {
        (payload as any).llm_api_key = apiKey;
      }
      const r = await apiFetch("/api/settings", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error("Failed to save");
      if (apiKey) await checkApiKey();
      setMessage("Settings saved successfully");
      setApiKey("");
    } catch (e) {
      setMessage(String(e));
    } finally {
      setSaving(false);
    }
  };

  const providers = [
    { id: "openai", name: "OpenAI / OpenRouter", defaultUrl: "https://api.openai.com/v1" },
    { id: "anthropic", name: "Anthropic", defaultUrl: "https://api.anthropic.com/v1" },
    { id: "gemini", name: "Google Gemini", defaultUrl: "https://generativelanguage.googleapis.com/v1beta" },
    { id: "ollama", name: "Ollama (Local)", defaultUrl: "http://localhost:11434" },
  ];

  return (
    <div>
      <h1>Settings</h1>
      {user && (
        <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "#f0f9ff", borderRadius: 8, border: "1px solid #bae6fd" }}>
          <h3 style={{ marginTop: 0 }}>Current User</h3>
          <p><strong>Name:</strong> {user.name || user.email || user.sub}</p>
          <p><strong>Roles:</strong> {user.roles.join(", ")}</p>
        </div>
      )}
      <div style={{ marginTop: "1rem", maxWidth: 800 }}>
        <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }}>
          <h3>LLM Provider</h3>
          <div style={{ marginBottom: 8 }}>
            <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Provider</label>
            <select
              value={settings.llm.provider}
              onChange={(e) => {
                const provider = providers.find((p) => p.id === e.target.value);
                setSettings((prev) => ({
                  ...prev,
                  llm: {
                    ...prev.llm,
                    provider: e.target.value,
                    baseUrl: provider?.defaultUrl || prev.llm.baseUrl,
                  },
                }));
              }}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: 8 }}>
            <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Base URL</label>
            <input
              value={settings.llm.baseUrl}
              onChange={(e) => setSettings((prev) => ({ ...prev, llm: { ...prev.llm, baseUrl: e.target.value } }))}
              placeholder={providers.find((p) => p.id === settings.llm.provider)?.defaultUrl}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
            />
          </div>
          <div style={{ marginBottom: 8 }}>
            <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Chat Model</label>
            <input
              value={settings.llm.model}
              onChange={(e) => setSettings((prev) => ({ ...prev, llm: { ...prev.llm, model: e.target.value } }))}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
            />
          </div>
          <div style={{ marginBottom: 8 }}>
            <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Embedding Model</label>
            <input
              value={settings.llm.embeddingModel}
              onChange={(e) => setSettings((prev) => ({ ...prev, llm: { ...prev.llm, embeddingModel: e.target.value } }))}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
            />
          </div>
          <div style={{ marginBottom: 8 }}>
            <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>API Key</label>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={settings.llm.apiKeySet ? "•••••••• (leave blank to keep current)" : "Enter API key"}
                style={{ flex: 1, padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
              />
              {settings.llm.apiKeySet && (
                <span style={{ color: "#22c55e", fontSize: "0.85rem" }}>✓ API key configured</span>
              )}
            </div>
          </div>
        </div>

        <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }}>
          <h3>RAG Pipeline</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem" }}>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Chunk Size</label>
              <input
                type="number"
                value={settings.chunkSize}
                onChange={(e) => setSettings((prev) => ({ ...prev, chunkSize: parseInt(e.target.value) || 1024 }))}
                min="100"
                max="8192"
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Chunk Overlap</label>
              <input
                type="number"
                value={settings.chunkOverlap}
                onChange={(e) => setSettings((prev) => ({ ...prev, chunkOverlap: parseInt(e.target.value) || 128 }))}
                min="0"
                max="1024"
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontWeight: 500 }}>Top K Results</label>
              <input
                type="number"
                value={settings.topK}
                onChange={(e) => setSettings((prev) => ({ ...prev, topK: parseInt(e.target.value) || 5 }))}
                min="1"
                max="50"
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
              />
            </div>
            <div>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 500 }}>
                <input
                  type="checkbox"
                  checked={settings.requireSso}
                  onChange={(e) => setSettings((prev) => ({ ...prev, requireSso: e.target.checked }))}
                />
                Require SSO Authentication
              </label>
            </div>
          </div>
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <button
            onClick={handleSave}
            disabled={saving}
            style={{
              padding: "0.75rem 2rem",
              background: "#3b82f6",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: saving ? "not-allowed" : "pointer",
              opacity: saving ? 0.7 : 1,
            }}
          >
            {saving ? "Saving..." : "Save Settings"}
          </button>
          {message && (
            <p style={{ marginTop: 8, color: message.includes("Failed") || message.includes("Error") ? "#ef4444" : "#22c55e" }}>
              {message}
            </p>
          )}
        </div>

        <div style={{ padding: "1rem", background: "#fef3c7", borderRadius: 8, border: "1px solid #fcd34d" }}>
          <h4 style={{ color: "#92400e", marginBottom: 4 }}>Note</h4>
          <p style={{ color: "#92400e", fontSize: "0.85rem" }}>
            Settings are stored in environment variables on the server. Changes require a backend restart to take effect.
            API keys are stored securely and never returned in API responses.
          </p>
        </div>
      </div>
    </div>
  );
}