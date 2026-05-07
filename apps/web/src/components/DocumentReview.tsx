import { useRef, useState } from "react"
import type { DesignReviewResponse } from "../services/api"
import { reviewDesignDocument, extractDocumentText } from "../services/api"

const PL_OPTIONS = ["PLa", "PLb", "PLc", "PLd", "PLe"]
const CAT_OPTIONS = ["Cat B", "Cat 1", "Cat 2", "Cat 3", "Cat 4"]

const VERDICT_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  adequate:           { bg: "#e8f5e1", color: "#2e7d32", label: "Adequate" },
  partially_adequate: { bg: "#fff8e1", color: "#f57f17", label: "Partially Adequate" },
  inadequate:         { bg: "#fdecea", color: "#c62828", label: "Inadequate" },
}

const SEVERITY_COLOUR: Record<string, string> = {
  critical: "#c62828",
  major:    "#e65100",
  minor:    "#f57f17",
}

export default function DocumentReview() {
  const fileRef = useRef<HTMLInputElement>(null)
  const [documentText, setDocumentText] = useState("")
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null)
  const [extracting, setExtracting] = useState(false)
  const [targetPl, setTargetPl] = useState("PLd")
  const [targetCategory, setTargetCategory] = useState("Cat 3")
  const [hazardIds, setHazardIds] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DesignReviewResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleFileUpload(file: File) {
    setExtracting(true)
    setError(null)
    setUploadedFileName(file.name)
    try {
      const text = await extractDocumentText(file)
      setDocumentText(text)
    } catch (e) {
      setError((e as Error).message)
      setUploadedFileName(null)
    } finally {
      setExtracting(false)
    }
  }

  async function handleReview() {
    if (!documentText.trim()) { setError("Please paste or type a document first."); return }
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const ids = hazardIds.split(",").map((s) => s.trim()).filter(Boolean)
      const res = await reviewDesignDocument(documentText.trim(), targetPl, targetCategory, ids.length ? ids : undefined)
      setResult(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const verdict = result ? (VERDICT_STYLE[result.overallVerdict] ?? VERDICT_STYLE.inadequate) : null

  return (
    <div className="design-review">
      <section>
        <h2>Document Review — Design & Quote Analysis</h2>
        <p className="subtitle">
          Paste a design specification, quote, or proposal. Claude will check it for safety function
          completeness against your target Performance Level and Category.
        </p>

        <div
          className="drop-zone"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleFileUpload(f) }}
          onClick={() => fileRef.current?.click()}
        >
          {extracting ? (
            <span className="drop-zone-hint">Extracting text…</span>
          ) : uploadedFileName ? (
            <span className="drop-zone-file">📄 {uploadedFileName} — text extracted</span>
          ) : (
            <span className="drop-zone-hint">
              Drag & drop a document, or click to select<br />
              <small>PDF, DOCX, or TXT</small>
            </span>
          )}
          <input ref={fileRef} type="file" accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
            style={{ display: "none" }}
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileUpload(f) }} />
        </div>

        <label>
          <span>Document Text <small style={{ color: "#8a9ab0" }}>(auto-filled from upload, or paste manually)</small></span>
          <textarea
            value={documentText}
            onChange={(e) => setDocumentText(e.target.value)}
            rows={8}
            placeholder="Text will appear here after upload, or paste directly…"
            style={{ fontFamily: "monospace", fontSize: "0.85rem" }}
          />
        </label>

        <div className="form-row form-row-3">
          <label>
            <span>Target PL</span>
            <select value={targetPl} onChange={(e) => setTargetPl(e.target.value)}>
              {PL_OPTIONS.map((pl) => <option key={pl}>{pl}</option>)}
            </select>
          </label>
          <label>
            <span>Target Category</span>
            <select value={targetCategory} onChange={(e) => setTargetCategory(e.target.value)}>
              {CAT_OPTIONS.map((c) => <option key={c}>{c}</option>)}
            </select>
          </label>
        </div>

        <div className="form-row">
          <label>
            <span>RA Hazard IDs to verify <small>(optional — comma separated, e.g. H01, H02)</small></span>
            <input
              type="text"
              value={hazardIds}
              onChange={(e) => setHazardIds(e.target.value)}
              placeholder="H01, H02, H03"
            />
          </label>
        </div>

        {error && <p className="error-msg">{error}</p>}

        <button onClick={handleReview} disabled={loading} className="primary-btn">
          {loading ? "Reviewing…" : "Review Document"}
        </button>
      </section>

      {result && verdict && (
        <>
          {/* Verdict banner */}
          <div className="verdict-banner" style={{ background: verdict.bg, borderColor: verdict.color }}>
            <span className="verdict-label" style={{ color: verdict.color }}>{verdict.label}</span>
          </div>
          <p className="gap-summary">{result.coverageAssessment}</p>

          {/* Safety functions */}
          {result.safetyFunctionsIdentified.length > 0 && (
            <section className="result-section">
              <h3>Safety Functions Identified ({result.safetyFunctionsIdentified.length})</h3>
              <table className="components-table">
                <thead>
                  <tr><th>Function</th><th>Implementation</th><th>PL Claimed</th><th>Category</th></tr>
                </thead>
                <tbody>
                  {result.safetyFunctionsIdentified.map((sf, i) => (
                    <tr key={i}>
                      <td>
                        <strong>{sf.name}</strong>
                        <br /><small style={{ color: "#6b8299" }}>{sf.description}</small>
                      </td>
                      <td>{sf.implementation || "—"}</td>
                      <td>{sf.plClaimed || "—"}</td>
                      <td>{sf.categoryClaimed || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {/* Gaps */}
          {result.gaps.length > 0 && (
            <section className="result-section">
              <h3>Gaps Identified ({result.gaps.length})</h3>
              {result.gaps.map((g, i) => (
                <div key={i} className="finding-card" style={{ borderLeftColor: SEVERITY_COLOUR[g.severity] ?? "#999" }}>
                  <div className="finding-header">
                    <span className="severity-badge" style={{ background: SEVERITY_COLOUR[g.severity] ?? "#999" }}>
                      {g.severity.toUpperCase()}
                    </span>
                    <span className="clause-ref">{g.clauseReference}</span>
                  </div>
                  <p className="finding-desc">{g.description}</p>
                  <p className="finding-remedy">→ {g.recommendation}</p>
                </div>
              ))}
            </section>
          )}

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <section className="result-section">
              <h3>Recommendations</h3>
              <ol style={{ paddingLeft: "1.2rem", margin: 0 }}>
                {result.recommendations.map((r, i) => (
                  <li key={i} style={{ marginBottom: 8, fontSize: "0.9rem", color: "#102a43" }}>{r}</li>
                ))}
              </ol>
            </section>
          )}
        </>
      )}
    </div>
  )
}
