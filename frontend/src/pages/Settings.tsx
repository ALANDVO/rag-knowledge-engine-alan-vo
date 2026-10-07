export default function Settings() {
  return (
    <div>
      <h1>Settings</h1>
      <div style={{ marginTop: "1rem", maxWidth: 500 }}>
        <div style={{ padding: "1rem", background: "#f1f5f9", borderRadius: 8 }}>
          <h3>Configuration</h3>
          <p>API: http://localhost:8000</p>
          <p>SSO: Enabled</p>
          <p>Chunk size: 1024 tokens</p>
        </div>
      </div>
    </div>
  );
}
