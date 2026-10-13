import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { useAuth } from "../App";
export default function Settings() {
    const { user } = useAuth();
    const [settings, setSettings] = useState({
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
    const [message, setMessage] = useState(null);
    const [apiKey, setApiKey] = useState("");
    const [csrfToken, setCsrfToken] = useState("");
    useEffect(() => {
        loadSettings();
        checkApiKey();
        loadCsrfToken();
    }, []);
    const apiFetch = async (url, options = {}) => {
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
        }
        catch (e) {
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
        }
        catch (e) {
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
        }
        catch (e) {
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
                payload.llm_api_key = apiKey;
            }
            const r = await apiFetch("/api/settings", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            if (!r.ok)
                throw new Error("Failed to save");
            if (apiKey)
                await checkApiKey();
            setMessage("Settings saved successfully");
            setApiKey("");
        }
        catch (e) {
            setMessage(String(e));
        }
        finally {
            setSaving(false);
        }
    };
    const providers = [
        { id: "openai", name: "OpenAI / OpenRouter", defaultUrl: "https://api.openai.com/v1" },
        { id: "anthropic", name: "Anthropic", defaultUrl: "https://api.anthropic.com/v1" },
        { id: "gemini", name: "Google Gemini", defaultUrl: "https://generativelanguage.googleapis.com/v1beta" },
        { id: "ollama", name: "Ollama (Local)", defaultUrl: "http://localhost:11434" },
    ];
    return (_jsxs("div", { children: [_jsx("h1", { children: "Settings" }), user && (_jsxs("div", { style: { marginBottom: "1.5rem", padding: "1rem", background: "#f0f9ff", borderRadius: 8, border: "1px solid #bae6fd" }, children: [_jsx("h3", { style: { marginTop: 0 }, children: "Current User" }), _jsxs("p", { children: [_jsx("strong", { children: "Name:" }), " ", user.name || user.email || user.sub] }), _jsxs("p", { children: [_jsx("strong", { children: "Roles:" }), " ", user.roles.join(", ")] })] })), _jsxs("div", { style: { marginTop: "1rem", maxWidth: 800 }, children: [_jsxs("div", { style: { marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }, children: [_jsx("h3", { children: "LLM Provider" }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Provider" }), _jsx("select", { value: settings.llm.provider, onChange: (e) => {
                                            const provider = providers.find((p) => p.id === e.target.value);
                                            setSettings((prev) => ({
                                                ...prev,
                                                llm: {
                                                    ...prev.llm,
                                                    provider: e.target.value,
                                                    baseUrl: provider?.defaultUrl || prev.llm.baseUrl,
                                                },
                                            }));
                                        }, style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 }, children: providers.map((p) => (_jsx("option", { value: p.id, children: p.name }, p.id))) })] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Base URL" }), _jsx("input", { value: settings.llm.baseUrl, onChange: (e) => setSettings((prev) => ({ ...prev, llm: { ...prev.llm, baseUrl: e.target.value } })), placeholder: providers.find((p) => p.id === settings.llm.provider)?.defaultUrl, style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } })] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Chat Model" }), _jsx("input", { value: settings.llm.model, onChange: (e) => setSettings((prev) => ({ ...prev, llm: { ...prev.llm, model: e.target.value } })), style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } })] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Embedding Model" }), _jsx("input", { value: settings.llm.embeddingModel, onChange: (e) => setSettings((prev) => ({ ...prev, llm: { ...prev.llm, embeddingModel: e.target.value } })), style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } })] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "API Key" }), _jsxs("div", { style: { display: "flex", gap: 8, alignItems: "center" }, children: [_jsx("input", { type: "password", value: apiKey, onChange: (e) => setApiKey(e.target.value), placeholder: settings.llm.apiKeySet ? "•••••••• (leave blank to keep current)" : "Enter API key", style: { flex: 1, padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } }), settings.llm.apiKeySet && (_jsx("span", { style: { color: "#22c55e", fontSize: "0.85rem" }, children: "\u2713 API key configured" }))] })] })] }), _jsxs("div", { style: { marginBottom: "1.5rem", padding: "1rem", background: "#f8fafc", borderRadius: 8 }, children: [_jsx("h3", { children: "RAG Pipeline" }), _jsxs("div", { style: { display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem" }, children: [_jsxs("div", { children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Chunk Size" }), _jsx("input", { type: "number", value: settings.chunkSize, onChange: (e) => setSettings((prev) => ({ ...prev, chunkSize: parseInt(e.target.value) || 1024 })), min: "100", max: "8192", style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } })] }), _jsxs("div", { children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Chunk Overlap" }), _jsx("input", { type: "number", value: settings.chunkOverlap, onChange: (e) => setSettings((prev) => ({ ...prev, chunkOverlap: parseInt(e.target.value) || 128 })), min: "0", max: "1024", style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } })] }), _jsxs("div", { children: [_jsx("label", { style: { display: "block", marginBottom: 4, fontWeight: 500 }, children: "Top K Results" }), _jsx("input", { type: "number", value: settings.topK, onChange: (e) => setSettings((prev) => ({ ...prev, topK: parseInt(e.target.value) || 5 })), min: "1", max: "50", style: { width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: 6 } })] }), _jsx("div", { children: _jsxs("label", { style: { display: "flex", alignItems: "center", gap: 8, fontWeight: 500 }, children: [_jsx("input", { type: "checkbox", checked: settings.requireSso, onChange: (e) => setSettings((prev) => ({ ...prev, requireSso: e.target.checked })) }), "Require SSO Authentication"] }) })] })] }), _jsxs("div", { style: { marginBottom: "1.5rem" }, children: [_jsx("button", { onClick: handleSave, disabled: saving, style: {
                                    padding: "0.75rem 2rem",
                                    background: "#3b82f6",
                                    color: "#fff",
                                    border: "none",
                                    borderRadius: 6,
                                    cursor: saving ? "not-allowed" : "pointer",
                                    opacity: saving ? 0.7 : 1,
                                }, children: saving ? "Saving..." : "Save Settings" }), message && (_jsx("p", { style: { marginTop: 8, color: message.includes("Failed") || message.includes("Error") ? "#ef4444" : "#22c55e" }, children: message }))] }), _jsxs("div", { style: { padding: "1rem", background: "#fef3c7", borderRadius: 8, border: "1px solid #fcd34d" }, children: [_jsx("h4", { style: { color: "#92400e", marginBottom: 4 }, children: "Note" }), _jsx("p", { style: { color: "#92400e", fontSize: "0.85rem" }, children: "Settings are stored in environment variables on the server. Changes require a backend restart to take effect. API keys are stored securely and never returned in API responses." })] })] })] }));
}
