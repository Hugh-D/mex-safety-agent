import { useState, useRef } from "react"
import type { AssessmentProject, HazardEntry, HRNParameters, PhotoEntry } from "@shared/types/assessment"
import { saveProject, analysePhoto, validateHrnAI, generateProjectReport, uploadHazardPhoto, PHOTO_BASE } from "../services/api"
import type { PhotoAnalysisResult, HRNValidationResult } from "../services/api"

const HRN_PARAMS = {
  LO: [
    { value: 0.033, label: "Almost impossible" },
    { value: 1,     label: "Highly unlikely" },
    { value: 1.5,   label: "Unlikely" },
    { value: 2,     label: "Possible" },
    { value: 5,     label: "Even chance" },
    { value: 8,     label: "Probable" },
    { value: 10,    label: "Likely" },
    { value: 15,    label: "Certain" },
  ],
  FE: [
    { value: 0.5, label: "Annually" },
    { value: 1,   label: "Monthly" },
    { value: 1.5, label: "Weekly" },
    { value: 2.5, label: "Daily" },
    { value: 4,   label: "Hourly" },
    { value: 5,   label: "Constantly" },
  ],
  DPH: [
    { value: 0.1,  label: "Scratch / bruise" },
    { value: 0.5,  label: "Laceration / mild ill health" },
    { value: 1,    label: "Minor fracture (fingers/toes)" },
    { value: 2,    label: "Major fracture (hand/arm/leg)" },
    { value: 4,    label: "Loss of 1–2 digits" },
    { value: 8,    label: "Amputation / partial sense loss" },
    { value: 10,   label: "Double amputation / total sense loss" },
    { value: 12,   label: "Critical / permanent illness" },
    { value: 15,   label: "Fatality" },
  ],
  NP: [
    { value: 1,  label: "1–2 persons" },
    { value: 2,  label: "3–7 persons" },
    { value: 4,  label: "8–15 persons" },
    { value: 8,  label: "16–50 persons" },
    { value: 12, label: "More than 50" },
  ],
}

const HAZARD_TYPES = [
  "Crushing", "Impact", "Entanglement", "Drawing-in", "Friction and abrasion",
  "Burn/Scald", "Cutting", "Shearing", "Slipping", "Tripping", "Falling",
  "Being run over", "Ejection of parts", "Loss of stability",
  "Electrical shock", "Electrocution", "Noise", "Vibration", "Radiation",
  "Dust/fume inhalation", "Contact with hazardous substances",
]

const MODES = ["Operation", "Maintenance", "Setup", "Cleaning", "Fault finding"]

function snapHrn(param: "LO" | "FE" | "DPH" | "NP", value: number): number {
  return HRN_PARAMS[param].reduce((best, o) =>
    Math.abs(o.value - value) < Math.abs(best.value - value) ? o : best
  ).value
}

function calcHrn(p: HRNParameters): number {
  return Math.round(p.LO * p.FE * p.DPH * p.NP * 1000) / 1000
}

function getRiskBand(score: number): { label: string; bg: string; fg: string } {
  if (score <= 1)   return { label: "Acceptable",   bg: "#00B050", fg: "white" }
  if (score < 4)    return { label: "Very Low",      bg: "#92D050", fg: "#102a43" }
  if (score <= 6)   return { label: "Needs Review",  bg: "#FFA000", fg: "white" }
  if (score <= 10)  return { label: "Low",           bg: "#FFFF00", fg: "#102a43" }
  if (score <= 50)  return { label: "Significant",   bg: "#FFC000", fg: "#102a43" }
  if (score <= 100) return { label: "High",          bg: "#FF6600", fg: "white" }
  if (score <= 500) return { label: "Very High",     bg: "#FF0000", fg: "white" }
  if (score <= 1000) return { label: "Extreme",      bg: "#CC0000", fg: "white" }
  return { label: "Unacceptable", bg: "#990000", fg: "white" }
}

const DEFAULT_HRN: HRNParameters = { LO: 2, FE: 2.5, DPH: 2, NP: 1 }

interface Props {
  project: AssessmentProject
  onBack: () => void
  onProjectUpdate: (p: AssessmentProject) => void
}

export default function ProjectView({ project, onBack, onProjectUpdate }: Props) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())
  const [showForm, setShowForm] = useState(false)
  const [editingHazardIdx, setEditingHazardIdx] = useState<number | null>(null)
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  const [photoPreview, setPhotoPreview] = useState<string | null>(null)
  const [location, setLocation] = useState("")
  const [mode, setMode] = useState(MODES[0])
  const [task, setTask] = useState("")
  const [hazardTypes, setHazardTypes] = useState<string[]>([])
  const [hrn, setHrn] = useState<HRNParameters>(DEFAULT_HRN)
  const [analysing, setAnalysing] = useState(false)
  const [aiResult, setAiResult] = useState<PhotoAnalysisResult | null>(null)
  const [validating, setValidating] = useState(false)
  const [validation, setValidation] = useState<HRNValidationResult | null>(null)
  const [saving, setSaving] = useState(false)
  const [downloading, setDownloading] = useState<"pdf" | "docx" | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const photoCacheRef = useRef<Map<string, string>>(new Map())

  const hrnScore = calcHrn(hrn)
  const band = getRiskBand(hrnScore)

  function resetForm() {
    setPhotoFile(null); setPhotoPreview(null); setLocation(""); setMode(MODES[0])
    setTask(""); setHazardTypes([]); setHrn(DEFAULT_HRN); setAiResult(null)
    setValidation(null); setError(null); setShowForm(false); setEditingHazardIdx(null)
  }

  function startEditHazard(idx: number) {
    const h = project.hazards[idx]
    setLocation(h.location)
    setMode(h.mode)
    setTask(h.task)
    setHazardTypes([...h.hazardTypes])
    setHrn({ LO: h.hrnBefore.LO, FE: h.hrnBefore.FE, DPH: h.hrnBefore.DPH, NP: h.hrnBefore.NP })
    const cachedPreview = photoCacheRef.current.get(h.id) ?? null
    const serverPreview = h.photos.length > 0 ? `${PHOTO_BASE}/photos/${h.photos[0].filepath}` : null
    setPhotoFile(null); setPhotoPreview(cachedPreview ?? serverPreview); setAiResult(null); setValidation(null); setError(null)
    setEditingHazardIdx(idx)
    setShowForm(true)
  }

  function toggleHazardType(t: string) {
    setHazardTypes((prev) => prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t])
  }

  async function handleAnalyse() {
    if (!photoFile) return
    setAnalysing(true); setError(null)
    try {
      const result = await analysePhoto(photoFile, location || "Unspecified location")
      setAiResult(result)
      if (result.suggestedMode && MODES.includes(result.suggestedMode)) setMode(result.suggestedMode)
      if (result.suggestedTask) setTask(result.suggestedTask)
      if (result.hazardTypes?.length) setHazardTypes(result.hazardTypes)
      const s = result.hrnSuggestions
      if (s?.LO && s.FE && s.DPH && s.NP) {
        setHrn({ LO: s.LO.value, FE: s.FE.value, DPH: s.DPH.value, NP: s.NP.value })
      }
    } catch (e: any) {
      setError(e.message)
    } finally {
      setAnalysing(false)
    }
  }

  async function handleValidate() {
    setValidating(true); setError(null)
    try {
      const result = await validateHrnAI(hrn, hazardTypes, aiResult?.observations ?? task)
      setValidation(result)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setValidating(false)
    }
  }

  async function handleSaveHazard() {
    if (!location.trim()) { setError("Location is required"); return }
    setSaving(true); setError(null)
    try {
      const aiFlags: string[] = [
        ...(validation?.flags ?? []),
        ...(validation?.challengedParameters.map(
          (cp) => `${cp.parameter}: entered ${cp.enteredValue} → recommended ${cp.recommendedValue}. ${cp.reason}`
        ) ?? []),
      ]

      const projectNumber = project.projectBrief.projectNumber
      let updatedHazards: HazardEntry[]

      if (editingHazardIdx !== null) {
        const existing = project.hazards[editingHazardIdx]
        let photos: PhotoEntry[] = existing.photos
        if (photoFile) {
          const { filepath } = await uploadHazardPhoto(projectNumber, existing.id, photoFile)
          photos = [{ filepath, timestamp: new Date().toISOString(), siteLabel: location.trim(), annotations: [] }]
          photoCacheRef.current.set(existing.id, `${PHOTO_BASE}/photos/${filepath}`)
        }
        const edited: HazardEntry = {
          ...existing,
          location: location.trim(),
          mode,
          task: task.trim(),
          hazardTypes,
          photos,
          hrnBefore: hrn,
          hrnScoreBefore: hrnScore,
          riskBandBefore: band.label,
          aiValidationFlags: aiFlags.length > 0 ? aiFlags : existing.aiValidationFlags,
        }
        updatedHazards = project.hazards.map((h, i) => i === editingHazardIdx ? edited : h)
      } else {
        const hazardId = `H${String(project.hazards.length + 1).padStart(2, "0")}`
        let photos: PhotoEntry[] = []
        if (photoFile) {
          const { filepath } = await uploadHazardPhoto(projectNumber, hazardId, photoFile)
          photos = [{ filepath, timestamp: new Date().toISOString(), siteLabel: location.trim(), annotations: [] }]
          photoCacheRef.current.set(hazardId, `${PHOTO_BASE}/photos/${filepath}`)
        }
        const newHazard: HazardEntry = {
          id: hazardId,
          location: location.trim(),
          mode,
          task: task.trim(),
          hazardTypes,
          photos,
          voiceNotes: [],
          hrnBefore: hrn,
          hrnScoreBefore: hrnScore,
          riskBandBefore: band.label,
          riskReductionMeasures: [],
          standardsReferences: [],
          aiValidationFlags: aiFlags,
          aiRecommendations: [],
        }
        updatedHazards = [...project.hazards, newHazard]
      }

      const updated: AssessmentProject = {
        ...project,
        hazards: updatedHazards,
        updatedAt: new Date().toISOString(),
      }
      await saveProject(updated)
      onProjectUpdate(updated)
      resetForm()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDownload(format: "pdf" | "docx") {
    setDownloading(format); setError(null)
    try {
      const blob = await generateProjectReport(project.projectBrief.projectNumber, format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      const safeName = project.projectBrief.projectNumber.replace(/[^a-zA-Z0-9_\- ]/g, "").trim().replace(/ /g, "_")
      a.href = url
      a.download = `${safeName}_RA.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 100)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setDownloading(null)
    }
  }

  return (
    <div className="project-view">
      <div className="pv-header">
        <button className="pv-back-btn" onClick={onBack}>← Projects</button>
        <h2 className="pv-title">{project.projectBrief.projectNumber}</h2>
        <div className="download-btn-group">
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

      <div className="pv-brief-card">
        <div className="pv-brief-row"><span>Client</span><strong>{project.projectBrief.client}</strong></div>
        <div className="pv-brief-row"><span>Site</span><strong>{project.projectBrief.site}</strong></div>
        <div className="pv-brief-row"><span>Machine / Line</span><strong>{project.projectBrief.machineOrLine}</strong></div>
        <div className="pv-brief-row"><span>Date</span><strong>{project.projectBrief.assessmentDate}</strong></div>
      </div>

      <section className="pv-hazards-section">
        <div className="pv-section-header">
          <h3>Hazards ({project.hazards.length})</h3>
          {!showForm && (
            <button className="primary-btn" onClick={() => setShowForm(true)}>+ Add Hazard</button>
          )}
        </div>

        {project.hazards.length === 0 && !showForm && (
          <p className="empty-state">No hazards recorded yet. Add the first hazard above.</p>
        )}

        {project.hazards.map((h, idx) => {
          const b = getRiskBand(h.hrnScoreBefore)
          const toggle = (section: string) => setExpandedSections((prev) => {
            const next = new Set(prev)
            const key = `${h.id}:${section}`
            next.has(key) ? next.delete(key) : next.add(key)
            return next
          })
          const isOpen = (section: string) => expandedSections.has(`${h.id}:${section}`)

          return (
            <div key={h.id} className="pv-hazard-card">
              <div className="pv-hazard-card-header">
                <span className="pv-hazard-id">{h.id}</span>
                <span className="pv-risk-badge" style={{ background: b.bg, color: b.fg }}>
                  {h.riskBandBefore} — {h.hrnScoreBefore}
                </span>
                <button
                  className="pv-edit-btn"
                  onClick={() => { if (!showForm) startEditHazard(idx) }}
                  disabled={showForm}
                  title="Edit hazard"
                >
                  Edit
                </button>
              </div>
              {h.photos.length > 0 && (
                <img
                  src={`${PHOTO_BASE}/photos/${h.photos[0].filepath}`}
                  alt={`${h.id} site photo`}
                  className="pv-hazard-photo-thumb"
                />
              )}
              <div className="pv-hazard-detail"><strong>Location:</strong> {h.location}</div>
              {h.mode && <div className="pv-hazard-detail"><strong>Mode:</strong> {h.mode}</div>}
              {h.task && <div className="pv-hazard-detail"><strong>Task:</strong> {h.task}</div>}
              {h.typedNotes && <div className="pv-hazard-detail"><strong>Notes:</strong> {h.typedNotes}</div>}

              {h.hazardTypes.length > 0 && (
                <div className="pv-hazard-section">
                  <button className="pv-section-toggle" onClick={() => toggle("types")}>
                    <span className="pv-section-chevron">{isOpen("types") ? "▾" : "▸"}</span>
                    Hazard Types <span className="pv-section-count">({h.hazardTypes.length})</span>
                  </button>
                  {isOpen("types") && (
                    <div className="pv-hazard-chips pv-section-body">
                      {h.hazardTypes.map((t) => <span key={t} className="pv-chip">{t}</span>)}
                    </div>
                  )}
                </div>
              )}

              {h.riskReductionMeasures && h.riskReductionMeasures.length > 0 && (
                <div className="pv-hazard-section">
                  <button className="pv-section-toggle" onClick={() => toggle("rrm")}>
                    <span className="pv-section-chevron">{isOpen("rrm") ? "▾" : "▸"}</span>
                    Risk Reduction Measures <span className="pv-section-count">({h.riskReductionMeasures.length})</span>
                  </button>
                  {isOpen("rrm") && (
                    <ul className="pv-hazard-list pv-section-body">
                      {h.riskReductionMeasures.map((m, i) => <li key={i}>{m}</li>)}
                    </ul>
                  )}
                </div>
              )}

              {h.aiValidationFlags && h.aiValidationFlags.length > 0 && (
                <div className="pv-hazard-section pv-hazard-section--flags">
                  <button className="pv-section-toggle pv-section-toggle--flags" onClick={() => toggle("flags")}>
                    <span className="pv-section-chevron">{isOpen("flags") ? "▾" : "▸"}</span>
                    AI Validation Flags <span className="pv-section-count">({h.aiValidationFlags.length})</span>
                  </button>
                  {isOpen("flags") && (
                    <ul className="pv-hazard-list pv-section-body">
                      {h.aiValidationFlags.map((f, i) => <li key={i}>⚑ {f}</li>)}
                    </ul>
                  )}
                </div>
              )}

              {h.aiRecommendations && h.aiRecommendations.length > 0 && (
                <div className="pv-hazard-section pv-hazard-section--recommendations">
                  <button className="pv-section-toggle pv-section-toggle--recs" onClick={() => toggle("recs")}>
                    <span className="pv-section-chevron">{isOpen("recs") ? "▾" : "▸"}</span>
                    AI Recommendations <span className="pv-section-count">({h.aiRecommendations.length})</span>
                  </button>
                  {isOpen("recs") && (
                    <ul className="pv-hazard-list pv-section-body">
                      {h.aiRecommendations.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  )}
                </div>
              )}
            </div>
          )
        })}

        {showForm && (
          <div className="pv-add-form">
            <h4>{editingHazardIdx !== null ? `Edit Hazard ${project.hazards[editingHazardIdx]?.id}` : "New Hazard"}</h4>

            <div className="pv-form-group">
              <span className="pv-label">Photo</span>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (!f) return
                  setPhotoFile(f)
                  setPhotoPreview(URL.createObjectURL(f))
                  setAiResult(null); setValidation(null)
                }}
              />
              <div className="pv-photo-row">
                <button type="button" className="pv-outline-btn" onClick={() => fileInputRef.current?.click()}>
                  {photoFile ? "Change Photo" : "Upload Photo"}
                </button>
                {photoFile && (
                  <button type="button" className="primary-btn" onClick={handleAnalyse} disabled={analysing}>
                    {analysing ? <><span className="btn-spinner" />Analysing…</> : "Analyse with AI"}
                  </button>
                )}
              </div>
              {photoPreview && <img src={photoPreview} alt="hazard" className="pv-photo-preview" />}
            </div>

            {aiResult && (
              <div className="pv-ai-box">
                <strong>AI Observations:</strong> {aiResult.observations}
              </div>
            )}

            <div className="pv-form-group">
              <label className="pv-label">
                Location *
                <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. East exit conveyor" />
              </label>
            </div>

            <div className="pv-form-group">
              <label className="pv-label">
                Mode
                <select value={mode} onChange={(e) => setMode(e.target.value)}>
                  {MODES.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </label>
            </div>

            <div className="pv-form-group">
              <label className="pv-label">
                Task
                <input value={task} onChange={(e) => setTask(e.target.value)} placeholder="Describe the task being performed" />
              </label>
            </div>

            <div className="pv-form-group">
              <span className="pv-label">Hazard Types</span>
              <div className="pv-hazard-type-grid">
                {HAZARD_TYPES.map((t) => (
                  <label key={t} className="pv-checkbox-label">
                    <input type="checkbox" checked={hazardTypes.includes(t)} onChange={() => toggleHazardType(t)} />
                    {t}
                  </label>
                ))}
              </div>
            </div>

            <div className="pv-form-group">
              <span className="pv-label">HRN Parameters</span>
              <div className="pv-hrn-grid">
                {(["LO", "FE", "DPH", "NP"] as const).map((param) => (
                  <div key={param} className="pv-hrn-select">
                    <span className="pv-hrn-param-label">{param}</span>
                    <select value={hrn[param]} onChange={(e) => setHrn({ ...hrn, [param]: parseFloat(e.target.value) })}>
                      {HRN_PARAMS[param].map((o) => (
                        <option key={o.value} value={o.value}>{o.label} ({o.value})</option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
              <div className="pv-hrn-score" style={{ background: band.bg, color: band.fg }}>
                HRN: {hrnScore.toFixed(1)} — {band.label}
              </div>
            </div>

            <button
              type="button"
              className="pv-outline-btn"
              onClick={handleValidate}
              disabled={validating || (hazardTypes.length === 0 && !aiResult)}
            >
              {validating ? <><span className="btn-spinner" />Validating with AI…</> : "Validate HRN with AI"}
            </button>

            {validation && (
              <div className="pv-validation-box">
                {validation.challengedParameters.length > 0 && (
                  <>
                    <p className="pv-validation-title">Challenged parameters:</p>
                    {validation.challengedParameters.map((cp) => (
                      <div key={cp.parameter} className="pv-challenged-row">
                        <strong>{cp.parameter}:</strong> entered {cp.enteredValue} → recommended {cp.recommendedValue}<br />
                        <span>{cp.reason}</span>
                      </div>
                    ))}
                    <button
                      type="button"
                      className="pv-apply-ai-btn"
                      onClick={() => {
                        const next = { ...hrn }
                        for (const cp of validation.challengedParameters) {
                          if (cp.parameter === "LO") next.LO = snapHrn("LO", cp.recommendedValue)
                          else if (cp.parameter === "FE") next.FE = snapHrn("FE", cp.recommendedValue)
                          else if (cp.parameter === "DPH") next.DPH = snapHrn("DPH", cp.recommendedValue)
                          else if (cp.parameter === "NP") next.NP = snapHrn("NP", cp.recommendedValue)
                        }
                        setHrn(next)
                      }}
                    >
                      Apply AI Suggestions
                    </button>
                  </>
                )}
                {validation.overallComment && (
                  <p style={{ margin: "10px 0 0" }}><strong>AI comment:</strong> {validation.overallComment}</p>
                )}
              </div>
            )}

            {error && <p className="error-msg">{error}</p>}

            <div className="pv-form-actions">
              <button type="button" className="pv-outline-btn" onClick={resetForm}>Cancel</button>
              <button type="button" className="primary-btn" onClick={handleSaveHazard} disabled={saving}>
                {saving ? <><span className="btn-spinner" />Saving…</> : editingHazardIdx !== null ? "Save Changes" : "Save Hazard"}
              </button>
            </div>
          </div>
        )}
      </section>

      {error && !showForm && <p className="error-msg" style={{ marginTop: 16 }}>{error}</p>}
    </div>
  )
}
