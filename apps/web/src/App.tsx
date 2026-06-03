import { useMemo, useState, useEffect } from "react"
import { determinePLR, scoreHRN, listProjects, createProject, getProject, generateProjectReport } from "./services/api"
import type { HRNParameters, PLRRequest, HRNScoreResponse, PLRResultResponse, AssessmentProject, ProjectListResponse } from "@shared/types/assessment"
import DesignReview from "./components/DesignReview"
import DocumentReview from "./components/DocumentReview"
import ProjectView from "./components/ProjectView"
import { ApiKeyGate } from "./components/ApiKeyGate"

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
    { value: 0.1, label: "Scratch / bruise" },
    { value: 0.5, label: "Laceration / mild ill health" },
    { value: 1,   label: "Minor fracture (fingers/toes)" },
    { value: 2,   label: "Major fracture (hand/arm/leg)" },
    { value: 4,   label: "Loss of 1–2 digits" },
    { value: 8,   label: "Amputation / partial sense loss" },
    { value: 10,  label: "Double amputation / total sense loss" },
    { value: 12,  label: "Critical / permanent illness" },
    { value: 15,  label: "Fatality" },
  ],
  NP: [
    { value: 1,  label: "1–2 persons" },
    { value: 2,  label: "3–7 persons" },
    { value: 4,  label: "8–15 persons" },
    { value: 8,  label: "16–50 persons" },
    { value: 12, label: "More than 50" },
  ],
}

// ISO 13849-1 risk graph paths: [severity, frequency, avoidance] → PLr
const PLR_GRAPH: { s: string; f: string; p: string; pl: string }[] = [
  { s: "S1", f: "F1", p: "P1", pl: "PLa" },
  { s: "S1", f: "F1", p: "P2", pl: "PLb" },
  { s: "S1", f: "F2", p: "P1", pl: "PLb" },
  { s: "S1", f: "F2", p: "P2", pl: "PLc" },
  { s: "S2", f: "F1", p: "P1", pl: "PLc" },
  { s: "S2", f: "F1", p: "P2", pl: "PLd" },
  { s: "S2", f: "F2", p: "P1", pl: "PLd" },
  { s: "S2", f: "F2", p: "P2", pl: "PLe" },
]

const PLR_COLOUR: Record<string, string> = {
  PLa: "#4caf50", PLb: "#8bc34a", PLc: "#ffc107", PLd: "#ff7043", PLe: "#e53935",
}

function RiskGraph({ activeSeverity, activeFrequency, activeAvoidance }: {
  activeSeverity: string; activeFrequency: string; activeAvoidance: string
}) {
  const activePl = PLR_GRAPH.find(
    (r) => r.s === activeSeverity && r.f === activeFrequency && r.p === activeAvoidance
  )?.pl ?? null

  // Layout constants
  const W = 560; const H = 310
  const col = [40, 160, 280, 400, 510]

  type Node = { id: string; x: number; y: number; label: string; sub?: string; active?: boolean }
  const nodes: Node[] = [
    { id: "start", x: col[0], y: 140, label: "Risk" },
    { id: "S1", x: col[1], y: 80,  label: "S1", sub: "Slight", active: activeSeverity === "S1" },
    { id: "S2", x: col[1], y: 200, label: "S2", sub: "Serious", active: activeSeverity === "S2" },
    { id: "S1F1", x: col[2], y: 50,  label: "F1", sub: "Seldom",  active: activeSeverity === "S1" && activeFrequency === "F1" },
    { id: "S1F2", x: col[2], y: 110, label: "F2", sub: "Frequent", active: activeSeverity === "S1" && activeFrequency === "F2" },
    { id: "S2F1", x: col[2], y: 170, label: "F1", sub: "Seldom",  active: activeSeverity === "S2" && activeFrequency === "F1" },
    { id: "S2F2", x: col[2], y: 270, label: "F2", sub: "Frequent", active: activeSeverity === "S2" && activeFrequency === "F2" },
    { id: "S1F1P1", x: col[3], y: 30,  label: "P1", sub: "Possible", active: activeSeverity === "S1" && activeFrequency === "F1" && activeAvoidance === "P1" },
    { id: "S1F1P2", x: col[3], y: 70,  label: "P2", sub: "Not poss.", active: activeSeverity === "S1" && activeFrequency === "F1" && activeAvoidance === "P2" },
    { id: "S1F2P1", x: col[3], y: 110, label: "P1", sub: "Possible", active: activeSeverity === "S1" && activeFrequency === "F2" && activeAvoidance === "P1" },
    { id: "S1F2P2", x: col[3], y: 150, label: "P2", sub: "Not poss.", active: activeSeverity === "S1" && activeFrequency === "F2" && activeAvoidance === "P2" },
    { id: "S2F1P1", x: col[3], y: 190, label: "P1", sub: "Possible", active: activeSeverity === "S2" && activeFrequency === "F1" && activeAvoidance === "P1" },
    { id: "S2F1P2", x: col[3], y: 225, label: "P2", sub: "Not poss.", active: activeSeverity === "S2" && activeFrequency === "F1" && activeAvoidance === "P2" },
    { id: "S2F2P1", x: col[3], y: 255, label: "P1", sub: "Possible", active: activeSeverity === "S2" && activeFrequency === "F2" && activeAvoidance === "P1" },
    { id: "S2F2P2", x: col[3], y: 285, label: "P2", sub: "Not poss.", active: activeSeverity === "S2" && activeFrequency === "F2" && activeAvoidance === "P2" },
  ]

  const edges: [string, string][] = [
    ["start","S1"],["start","S2"],
    ["S1","S1F1"],["S1","S1F2"],["S2","S2F1"],["S2","S2F2"],
    ["S1F1","S1F1P1"],["S1F1","S1F1P2"],
    ["S1F2","S1F2P1"],["S1F2","S1F2P2"],
    ["S2F1","S2F1P1"],["S2F1","S2F1P2"],
    ["S2F2","S2F2P1"],["S2F2","S2F2P2"],
  ]

  const plNodes = [
    { id: "S1F1P1", pl: "PLa" }, { id: "S1F1P2", pl: "PLb" },
    { id: "S1F2P1", pl: "PLb" }, { id: "S1F2P2", pl: "PLc" },
    { id: "S2F1P1", pl: "PLc" }, { id: "S2F1P2", pl: "PLd" },
    { id: "S2F2P1", pl: "PLd" }, { id: "S2F2P2", pl: "PLe" },
  ]

  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]))

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, display: "block" }}>
      {/* edges */}
      {edges.map(([a, b]) => {
        const na = byId[a]; const nb = byId[b]
        return (
          <line key={`${a}-${b}`} x1={na.x + 18} y1={na.y} x2={nb.x - 18} y2={nb.y}
            stroke="#c8d8ea" strokeWidth={1.5} />
        )
      })}
      {/* pl outcome badges */}
      {plNodes.map(({ id, pl }) => {
        const n = byId[id]
        const isActive = pl === activePl && n.active
        return (
          <g key={`pl-${id}`}>
            <rect x={col[4] - 22} y={n.y - 13} width={44} height={26} rx={6}
              fill={isActive ? PLR_COLOUR[pl] : "#eef2f7"}
              stroke={isActive ? PLR_COLOUR[pl] : "#c8d8ea"} strokeWidth={1.5} />
            <text x={col[4]} y={n.y + 5} textAnchor="middle"
              fontSize={12} fontWeight={isActive ? 700 : 500}
              fill={isActive ? "white" : "#6b8299"}>
              {pl}
            </text>
          </g>
        )
      })}
      {/* nodes */}
      {nodes.map((n) => (
        <g key={n.id}>
          <rect x={n.x - 18} y={n.y - 13} width={36} height={26} rx={6}
            fill={n.active ? "#002559" : "#f0f4ff"}
            stroke={n.active ? "#002559" : "#b0c4de"} strokeWidth={1.5} />
          <text x={n.x} y={n.y + 4} textAnchor="middle"
            fontSize={11} fontWeight={n.active ? 700 : 500}
            fill={n.active ? "white" : "#102a43"}>
            {n.label}
          </text>
          {n.sub && (
            <text x={n.x} y={n.y + 22} textAnchor="middle" fontSize={8.5} fill="#8a9ab0">
              {n.sub}
            </text>
          )}
        </g>
      ))}
    </svg>
  )
}

const defaultParameters: HRNParameters = {
  LO: 2,
  FE: 1,
  DPH: 2,
  NP: 1,
  justification: {
    LO: "Possible occurrence",
    FE: "Daily exposure",
    DPH: "Major fracture",
    NP: "Single operator",
  },
}

function App() {
  const [activeTab, setActiveTab] = useState<"calculator" | "projects" | "design-review" | "document-review">("calculator")
  const [showReviewTabs, setShowReviewTabs] = useState(false) // mobile only — desktop always shows review tabs via CSS
  const [parameters, setParameters] = useState<HRNParameters>(defaultParameters)
  const [severity, setSeverity] = useState("S2")
  const [frequency, setFrequency] = useState("F2")
  const [avoidance, setAvoidance] = useState("P2")
  const [showRiskGraph, setShowRiskGraph] = useState(false)
  const [hrnResult, setHrnResult] = useState<HRNScoreResponse | null>(null)
  const [plrResult, setPlrResult] = useState<PLRResultResponse | null>(null)
  const [projects, setProjects] = useState<string[]>([])
  const [newProject, setNewProject] = useState({
    projectNumber: "",
    client: "",
    site: "",
    machineOrLine: "",
  })
  const [error, setError] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<AssessmentProject | null>(null)

  useEffect(() => {
    if (activeTab === "projects") {
      loadProjects()
    }
  }, [activeTab])

  useEffect(() => {
    // If user unchecks review tools while on a review tab, bounce back to Projects
    if (!showReviewTabs && (activeTab === "design-review" || activeTab === "document-review")) {
      setActiveTab("projects")
    }
  }, [showReviewTabs])

  const loadProjects = async () => {
    try {
      const result = await listProjects()
      setProjects(result.projectNumbers)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const openProject = async (projectNumber: string) => {
    try {
      const loaded = await getProject(projectNumber)
      setSelectedProject(loaded)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const createNewProject = async () => {
    try {
      const project: AssessmentProject = {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: "draft",
        projectBrief: {
          projectNumber: newProject.projectNumber,
          client: newProject.client,
          site: newProject.site,
          machineOrLine: newProject.machineOrLine,
          assessmentDate: new Date().toISOString().split('T')[0],
          team: [],
          scopeDescription: "",
          standardsApplicable: [],
          lifecycleExclusions: [],
        },
        hazards: [],
      }
      const created = await createProject(project)
      setNewProject({ projectNumber: "", client: "", site: "", machineOrLine: "" })
      loadProjects()
      setSelectedProject(created)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const downloadReport = async (projectNumber: string) => {
    try {
      const blob = await generateProjectReport(projectNumber)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report-${projectNumber}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 100)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const parameterRows = useMemo(
    () => [
      { key: "LO" as const, label: "Likelihood of Occurrence (LO)", options: HRN_PARAMS.LO, value: parameters.LO },
      { key: "FE" as const, label: "Frequency of Exposure (FE)", options: HRN_PARAMS.FE, value: parameters.FE },
      { key: "DPH" as const, label: "Degree of Possible Harm (DPH)", options: HRN_PARAMS.DPH, value: parameters.DPH },
      { key: "NP" as const, label: "Number of Persons at Risk (NP)", options: HRN_PARAMS.NP, value: parameters.NP },
    ],
    [parameters],
  )

  const updateParameter = (key: keyof HRNParameters, value: string) => {
    setParameters((current) => ({
      ...current,
      [key]: Number(value),
    }))
  }

  const handleScoreHRN = async () => {
    setError(null)
    try {
      const result = await scoreHRN(parameters)
      setHrnResult(result)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const handleDeterminePLR = async () => {
    setError(null)
    try {
      const payload: PLRRequest = { severity, frequency, avoidance }
      const result = await determinePLR(payload)
      setPlrResult(result)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <ApiKeyGate>
    <div className="app-shell">
      <header>
        <h1>MEX Safety Platform</h1>
        <nav>
          <button
            onClick={() => setActiveTab("calculator")}
            className={activeTab === "calculator" ? "active" : ""}
          >
            Calculator
          </button>
          <button
            onClick={() => setActiveTab("projects")}
            className={activeTab === "projects" ? "active" : ""}
          >
            Projects
          </button>
          <button
            onClick={() => setActiveTab("design-review")}
            className={[
              activeTab === "design-review" ? "active" : "",
              "nav-review-tab",
              showReviewTabs ? "nav-review-tab--visible" : "",
            ].filter(Boolean).join(" ")}
          >
            Drawing Review
          </button>
          <button
            onClick={() => setActiveTab("document-review")}
            className={[
              activeTab === "document-review" ? "active" : "",
              "nav-review-tab",
              showReviewTabs ? "nav-review-tab--visible" : "",
            ].filter(Boolean).join(" ")}
          >
            Document Review
          </button>
          <label className="review-tabs-toggle">
            <input
              type="checkbox"
              checked={showReviewTabs}
              onChange={(e) => setShowReviewTabs(e.target.checked)}
            />
            Review tools
          </label>
        </nav>
      </header>

      {activeTab === "calculator" && (
        <>
          <section>
            <h2>HRN Input</h2>
            <div className="grid">
              {parameterRows.map((row) => (
                <label key={row.key}>
                  <span>{row.label}</span>
                  <select value={row.value} onChange={(e) => updateParameter(row.key, e.target.value)}>
                    {row.options.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.value} — {opt.label}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
            <button onClick={handleScoreHRN}>Score HRN</button>
          </section>

          {hrnResult && (
            <section>
              <h2>HRN Result</h2>
              <div className="result-card">
                <p>
                  Score: <strong>{hrnResult.hrnScore}</strong>
                </p>
                <p>
                  Band: <strong>{hrnResult.riskBand.label}</strong>
                </p>
                <p>
                  Acceptable: <strong>{hrnResult.acceptable ? "Yes" : "No"}</strong>
                </p>
              </div>
            </section>
          )}

          <section>
            <h2>PLr Input</h2>
            <div className="grid-3">
              <label>
                <span>Severity</span>
                <select value={severity} onChange={(event) => setSeverity(event.target.value)}>
                  <option value="S1">S1 — Slight (reversible)</option>
                  <option value="S2">S2 — Serious (irreversible / fatal)</option>
                </select>
              </label>
              <label>
                <span>Frequency / Exposure</span>
                <select value={frequency} onChange={(event) => setFrequency(event.target.value)}>
                  <option value="F1">F1 — Seldom to infrequent</option>
                  <option value="F2">F2 — Frequent to continuous</option>
                </select>
              </label>
              <label>
                <span>Possibility of Avoidance</span>
                <select value={avoidance} onChange={(event) => setAvoidance(event.target.value)}>
                  <option value="P1">P1 — Possible under specific conditions</option>
                  <option value="P2">P2 — Scarcely possible</option>
                </select>
              </label>
            </div>
            <div className="risk-graph-toggle">
              <label className="toggle-label">
                <input type="checkbox" checked={showRiskGraph} onChange={(e) => setShowRiskGraph(e.target.checked)} />
                Show ISO 13849-1 risk graph
              </label>
            </div>
            {showRiskGraph && (
              <div className="risk-graph-wrap">
                <RiskGraph activeSeverity={severity} activeFrequency={frequency} activeAvoidance={avoidance} />
                <p className="risk-graph-caption">ISO 13849-1:2015 — Risk graph. Highlighted path reflects current selection.</p>
              </div>
            )}
            <button onClick={handleDeterminePLR}>Determine PLr</button>
          </section>

          {plrResult && (
            <section>
              <h2>PLr Result</h2>
              <div className="result-card">
                <p>
                  PLr: <strong>{plrResult.plrRequired}</strong>
                </p>
                <p>Standard: {plrResult.sourceStandard}</p>
              </div>
            </section>
          )}
        </>
      )}

      {activeTab === "projects" && selectedProject && (
        <ProjectView
          project={selectedProject}
          onBack={() => { setSelectedProject(null); loadProjects() }}
          onProjectUpdate={(p) => setSelectedProject(p)}
        />
      )}

      {activeTab === "projects" && !selectedProject && (
        <>
          <section>
            <h2>Create New Project</h2>
            <div className="grid">
              <label>
                <span>Project Number</span>
                <input
                  type="text"
                  value={newProject.projectNumber}
                  onChange={(event) => setNewProject(prev => ({ ...prev, projectNumber: event.target.value }))}
                />
              </label>
              <label>
                <span>Client</span>
                <input
                  type="text"
                  value={newProject.client}
                  onChange={(event) => setNewProject(prev => ({ ...prev, client: event.target.value }))}
                />
              </label>
              <label>
                <span>Site</span>
                <input
                  type="text"
                  value={newProject.site}
                  onChange={(event) => setNewProject(prev => ({ ...prev, site: event.target.value }))}
                />
              </label>
              <label>
                <span>Machine / Line</span>
                <input
                  type="text"
                  value={newProject.machineOrLine}
                  onChange={(event) => setNewProject(prev => ({ ...prev, machineOrLine: event.target.value }))}
                />
              </label>
            </div>
            <button onClick={createNewProject}>Create Project</button>
          </section>

          <section>
            <h2>Existing Projects</h2>
            {projects.length === 0 ? (
              <p>No projects yet. Create your first project above.</p>
            ) : (
              <div className="project-list">
                {projects.map((projectNumber) => (
                  <div key={projectNumber} className="project-item">
                    <button className="project-number-btn" onClick={() => openProject(projectNumber)}>
                      {projectNumber}
                    </button>
                    <button onClick={() => downloadReport(projectNumber)}>Download Report</button>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}

      {activeTab === "design-review" && <DesignReview />}
      {activeTab === "document-review" && <DocumentReview />}

      {error && (
        <section className="error-box">
          <p>{error}</p>
        </section>
      )}
    </div>
    </ApiKeyGate>
  )
}

export default App
