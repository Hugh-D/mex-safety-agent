import { useState, useEffect } from "react"
import { validateApiKey } from "../services/api"

interface Props {
  children: React.ReactNode
}

export function ApiKeyGate({ children }: Props) {
  const [state, setState] = useState<"checking" | "needs-key" | "ready">("checking")
  const [input, setInput] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setState(localStorage.getItem("mex_api_key") ? "ready" : "needs-key")
  }, [])

  const handleSave = async () => {
    const key = input.trim()
    if (!key) return
    setLoading(true)
    setError(null)
    try {
      const ok = await validateApiKey(key)
      if (ok) {
        localStorage.setItem("mex_api_key", key)
        setState("ready")
      } else {
        setError("Key not recognised — check the key and try again.")
      }
    } catch {
      setError("Could not reach the server. Check your connection.")
    } finally {
      setLoading(false)
    }
  }

  if (state === "checking") return null

  if (state === "needs-key") {
    return (
      <div className="key-gate-overlay">
        <div className="key-gate-card">
          <div className="key-gate-logo">MEX</div>
          <h1 className="key-gate-title">MEX Safety Platform</h1>
          <p className="key-gate-sub">Enter the API key assigned to you by Hugh.</p>
          <input
            className="key-gate-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSave()}
            placeholder="mex-yourname-2026"
            autoFocus
            spellCheck={false}
          />
          {error && <p className="key-gate-error">{error}</p>}
          <button
            className="key-gate-btn"
            onClick={handleSave}
            disabled={loading || !input.trim()}
          >
            {loading ? "Checking…" : "Save & Continue"}
          </button>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
