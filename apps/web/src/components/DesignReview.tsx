import { useRef, useState } from "react"
import type { DrawingAnalysisResponse, DxfParseResponse } from "../services/api"
import { analyseDrawing, parseDxf, downloadComplianceReport } from "../services/api"

const PL_OPTIONS = ["PLa", "PLb", "PLc", "PLd", "PLe"]
const CAT_OPTIONS = ["Cat B", "Cat 1", "Cat 2", "Cat 3", "Cat 4"]

const VERDICT_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  compliant:              { bg: "#e8f5e1", color: "#2e7d32", label: "Compliant" },
  conditionally_compliant:{ bg: "#fff8e1", color: "#f57f17", label: "Conditionally Compliant" },
  non_compliant:          { bg: "#fdecea", color: "#c62828", label: "Non-Compliant" },
}

const SEVERITY_COLOUR: Record<string, string> = {
  critical: "#c62828",
  major:    "#e65100",
  minor:    "#f57f17",
}

/** Render text that may contain bullet lines (starting with - or •) as a list, otherwise as paragraphs. */
function RichText({ text, className }: { text: string; className?: string }) {
  const lines = text.split(/\n+/).map((l) => l.trim()).filter(Boolean)
  const isBullet = (l: string) => /^[-•*]/.test(l)
  if (lines.some(isBullet)) {
    return (
      <ul className={`rich-list ${className ?? ""}`}>
        {lines.map((l, i) => (
          <li key={i}>{l.replace(/^[-•*]\s*/, "")}</li>
        ))}
      </ul>
    )
  }
  return (
    <>
      {lines.map((l, i) => (
        <p key={i} className={className} style={{ marginBottom: lines.length > 1 ? 6 : 0 }}>{l}</p>
      ))}
    </>
  )
}

export default function DesignReview() {
  const fileRef = useRef<HTMLInputElement>(null)
  const dxfRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [dxfFile, setDxfFile] = useState<File | null>(null)
  const [drawingTitle, setDrawingTitle] = useState("")
  const [targetPl, setTargetPl] = useState("PLd")
  const [targetCategory, setTargetCategory] = useState("Cat 3")
  const [context, setContext] = useState("")
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState("")
  const [dxfResult, setDxfResult] = useState<DxfParseResponse | null>(null)
  const [dxfExpanded, setDxfExpanded] = useState(false)
  const [result, setResult] = useState<DrawingAnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [downloading, setDownloading] = useState<"pdf" | "docx" | null>(null)

  function handleFileDrop(e: React.DragEvent) {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (!dropped) return
    if (dropped.name.toLowerCase().endsWith(".dxf")) setDxfFile(dropped)
    else setFile(dropped)
  }

  async function handleAnalyse() {
    if (!file) { setError("Please upload a drawing image first."); return }
    if (!drawingTitle.trim()) { setError("Drawing title is required."); return }
    setError(null)
    setLoading(true)
    setResult(null)
    setDxfResult(null)
    try {
      let parsedDxf: DxfParseResponse | undefined
      if (dxfFile) {
        setLoadingStage("Parsing DXF…")
        parsedDxf = await parseDxf(dxfFile)
        setDxfResult(parsedDxf)
        setDxfExpanded(true)
      }
      setLoadingStage("Analysing drawing…")
      const res = await analyseDrawing(file, drawingTitle.trim(), targetPl, targetCategory, context || undefined, dxfFile || undefined)
      setResult(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
      setLoadingStage("")
    }
  }

  async function handleDownload(format: "pdf" | "docx") {
    if (!result) return
    setDownloading(format)
    try {
      await downloadComplianceReport(drawingTitle.trim(), targetPl, targetCategory, result, format)
    } catch (e) {
      setError(`Export failed: ${(e as Error).message}`)
    } finally {
      setDownloading(null)
    }
  }

  const verdict = result ? (VERDICT_STYLE[result.overallVerdict] ?? VERDICT_STYLE.non_compliant) : null

  return (
    <div className="design-review">
      {/* Upload panel — hidden when printing */}
      <section className="no-print">
        <h2>Design Review — Drawing Analysis</h2>
        <p className="subtitle">
          Upload a safety circuit drawing or mechanical layout. Claude will analyse it against your target
          Performance Level and Category.
        </p>

        <div
          className="drop-zone"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          onClick={() => fileRef.current?.click()}
        >
          {file ? (
            <span className="drop-zone-file">📄 {file.name}</span>
          ) : (
            <span className="drop-zone-hint">Drag & drop a drawing here, or click to select<br /><small>PNG, JPG, PDF</small></span>
          )}
          <input ref={fileRef} type="file" accept="image/*,.pdf" style={{ display: "none" }}
            onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])} />
        </div>

        <div className="dxf-attach-row">
          <button className="dxf-attach-btn" type="button" onClick={() => dxfRef.current?.click()}>
            {dxfFile ? `✓ ${dxfFile.name}` : "+ Attach source DXF (optional)"}
          </button>
          {dxfFile && (
            <button className="dxf-clear-btn" type="button" onClick={() => setDxfFile(null)}>✕</button>
          )}
          <input ref={dxfRef} type="file" accept=".dxf" style={{ display: "none" }}
            onChange={(e) => e.target.files?.[0] && setDxfFile(e.target.files[0])} />
          <span className="dxf-attach-hint">Enriches the AI analysis with a verified component list from your CAD file.</span>
        </div>

        <div className="form-row">
          <label>
            <span>Drawing Title</span>
            <input type="text" value={drawingTitle} onChange={(e) => setDrawingTitle(e.target.value)}
              placeholder="e.g. Press Line 4 — Safety Circuit Rev B" />
          </label>
        </div>

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

        <label>
          <span>Context (optional)</span>
          <textarea value={context} onChange={(e) => setContext(e.target.value)} rows={2}
            placeholder="e.g. This is the safety relay circuit for the press nip point light curtain. Related to hazard H01." />
        </label>

        {error && <p className="error-msg">{error}</p>}

        <button onClick={handleAnalyse} disabled={loading} className="primary-btn">
          {loading ? <><span className="btn-spinner" />{loadingStage || "Analysing…"}</> : "Analyse Drawing"}
        </button>
      </section>

      {/* DXF parse results */}
      {dxfResult && (
        <section className="result-section dxf-section">
          <div className="dxf-header" onClick={() => setDxfExpanded((x) => !x)}>
            <h3>DXF Component Inventory — {dxfResult.sourceFilename}</h3>
            <span className="dxf-toggle">{dxfExpanded ? "▲ Collapse" : "▼ Expand"}</span>
          </div>
          <div className="dxf-stats-row">
            <DxfStat label="Total inserts" value={dxfResult.totalInserts} />
            <DxfStat label="Recognised" value={dxfResult.recognisedCount} />
            <DxfStat label="Safety-relevant" value={dxfResult.safetyCount} highlight />
            <DxfStat label="Unknown blocks" value={dxfResult.unknownBlockCount} warn={dxfResult.unknownBlockCount > 0} />
          </div>
          {dxfExpanded && (
            <>
              {dxfResult.components.filter((c) => c.safetyRelevant).length > 0 && (
                <table className="components-table">
                  <thead>
                    <tr><th>Tag</th><th>Description</th><th>Type</th><th>Compliance</th><th>Note</th></tr>
                  </thead>
                  <tbody>
                    {dxfResult.components.filter((c) => c.safetyRelevant).map((c, i) => (
                      <tr key={i}>
                        <td><strong>{c.tag || c.blockName}</strong></td>
                        <td>{c.description}</td>
                        <td>{c.componentType}</td>
                        <td>{c.complianceType}</td>
                        <td>{c.safetyNote ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              {dxfResult.libraryGaps.length > 0 && (
                <div className="library-gaps">
                  <strong>Library gaps</strong>
                  <ul>
                    {dxfResult.libraryGaps.map((g, i) => <li key={i}>{g}</li>)}
                  </ul>
                </div>
              )}
              {dxfResult.unknownBlocks.length > 0 && (
                <div className="unknown-blocks">
                  <strong>Unrecognised blocks ({dxfResult.unknownBlocks.length}):</strong>{" "}
                  <span className="unknown-list">{dxfResult.unknownBlocks.join(", ")}</span>
                </div>
              )}
            </>
          )}
        </section>
      )}

      {/* Results */}
      {result && verdict && (
        <>
          {/* Verdict + download bar */}
          <div className="verdict-banner" style={{ background: verdict.bg, borderColor: verdict.color }}>
            <span className="verdict-label" style={{ color: verdict.color }}>{verdict.label}</span>
            <span className="verdict-gap">Gap to {targetPl} {targetCategory}: <strong>{result.gapToTarget}</strong></span>
            <div className="download-btn-group no-print">
              <button
                className="print-btn"
                onClick={() => handleDownload("pdf")}
                disabled={downloading !== null}
              >
                {downloading === "pdf" ? <><span className="btn-spinner" />Generating…</> : "⬇ PDF"}
              </button>
              <button
                className="print-btn print-btn-secondary"
                onClick={() => handleDownload("docx")}
                disabled={downloading !== null}
              >
                {downloading === "docx" ? <><span className="btn-spinner" />Generating…</> : "⬇ Word"}
              </button>
            </div>
          </div>
          <div className="gap-summary">
            <RichText text={result.gapSummary} />
          </div>

          {/* Redline SLD — shown when DXF topology produced a diagram */}
          {result.svgDiagram && (
            <section className="result-section sld-section">
              <h3>Redline Safety Circuit Diagram</h3>
              <p className="sld-hint">Red annotations correspond to numbered non-conformances below.</p>
              <div
                className="sld-container"
                dangerouslySetInnerHTML={{ __html: result.svgDiagram }}
              />
            </section>
          )}

          {/* Architecture */}
          <section className="result-section">
            <h3>Architecture Assessment</h3>
            <div className="arch-grid">
              <Tile label="Detected PL" value={result.architectureAssessment.detectedPl} />
              <Tile label="Detected Category" value={result.architectureAssessment.detectedCategory} />
              <Tile label="Channels" value={result.architectureAssessment.channelCount} />
              <Tile label="Feedback Monitoring" value={
                result.architectureAssessment.hasFeedbackMonitoring === null ? "Unknown"
                : result.architectureAssessment.hasFeedbackMonitoring ? "Yes" : "No"
              } />
            </div>
            <div className="arch-summary">
              <RichText text={result.architectureAssessment.summary} />
            </div>
          </section>

          {/* Components */}
          {result.componentsIdentified.length > 0 && (
            <section className="result-section">
              <h3>Components Identified ({result.componentsIdentified.length})</h3>
              <table className="components-table">
                <thead>
                  <tr><th>Component</th><th>Type</th><th>Drawing #</th></tr>
                </thead>
                <tbody>
                  {result.componentsIdentified.map((c, i) => (
                    <tr key={i}>
                      <td>{c.component || "—"}</td>
                      <td>{c.type}</td>
                      <td>{c.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {/* Non-conformances */}
          {result.nonConformances.length > 0 && (
            <section className="result-section">
              <h3>Non-Conformances ({result.nonConformances.length})</h3>
              {result.nonConformances.map((nc, i) => (
                <div key={i} className="finding-card" style={{ borderLeftColor: SEVERITY_COLOUR[nc.severity] ?? "#999" }}>
                  <div className="finding-header">
                    <span className="severity-badge" style={{ background: SEVERITY_COLOUR[nc.severity] ?? "#999" }}>
                      {nc.severity.toUpperCase()}
                    </span>
                    <span className="clause-ref">{nc.clauseReference}</span>
                  </div>
                  <div className="finding-desc">
                    <RichText text={nc.description} />
                  </div>
                  <div className="finding-remedy">
                    <RichText text={`→ ${nc.remediation}`} />
                  </div>
                </div>
              ))}
            </section>
          )}

          {/* Conformances */}
          {result.conformances.length > 0 && (
            <section className="result-section">
              <h3>Conformances ({result.conformances.length})</h3>
              {result.conformances.map((c, i) => (
                <div key={i} className="conformance-row">
                  <span className="check">✓</span>
                  <span>{c.description}</span>
                  <span className="clause-ref">{c.clauseReference}</span>
                </div>
              ))}
            </section>
          )}
        </>
      )}
    </div>
  )
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="arch-tile">
      <span className="arch-tile-value">{value}</span>
      <span className="arch-tile-label">{label}</span>
    </div>
  )
}

function DxfStat({ label, value, highlight, warn }: { label: string; value: number; highlight?: boolean; warn?: boolean }) {
  return (
    <div className={`dxf-stat ${highlight ? "dxf-stat-highlight" : ""} ${warn ? "dxf-stat-warn" : ""}`}>
      <span className="dxf-stat-value">{value}</span>
      <span className="dxf-stat-label">{label}</span>
    </div>
  )
}
