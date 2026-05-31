import type {
  HRNParameters,
  HRNScoreResponse,
  PLRRequest,
  PLRResultResponse,
  ReportDraftRequest,
  AssessmentProject,
  ProjectListResponse,
} from "../../../../shared/types/assessment"

const API_BASE = "/api"
export const PHOTO_BASE = ""

function authHeader(): Record<string, string> {
  const key =
    localStorage.getItem("mex_api_key") ??
    ((import.meta as any).env?.VITE_API_KEY as string | undefined) ?? ""
  return key ? { "X-API-Key": key } : {}
}

export async function validateApiKey(key: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/assessment/projects`, {
      headers: { "X-API-Key": key },
    })
    return res.ok
  } catch {
    return false
  }
}

async function throwWithDetail(response: Response, prefix: string): Promise<never> {
  let detail = response.statusText
  try {
    const body = await response.json()
    detail = body.detail ?? body.message ?? JSON.stringify(body)
  } catch { /* ignore */ }
  throw new Error(`${prefix}: ${detail}`)
}

async function requestJSON<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(body),
  })
  if (!response.ok) await throwWithDetail(response, "API request failed")
  return response.json()
}

async function getJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: authHeader() })
  if (!response.ok) await throwWithDetail(response, "API request failed")
  return response.json()
}

export async function scoreHRN(parameters: HRNParameters): Promise<HRNScoreResponse> {
  return requestJSON<HRNScoreResponse>("/assessment/hrn", parameters)
}

export async function determinePLR(request: PLRRequest): Promise<PLRResultResponse> {
  return requestJSON<PLRResultResponse>("/assessment/plr", request)
}

export async function generateDraftReport(request: ReportDraftRequest): Promise<Blob> {
  const response = await fetch(`${API_BASE}/report/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    throw new Error(`Failed to generate report: ${response.statusText}`)
  }
  return response.blob()
}

export async function createProject(project: AssessmentProject): Promise<AssessmentProject> {
  return requestJSON<AssessmentProject>("/assessment/project", project)
}

export async function saveProject(project: AssessmentProject): Promise<AssessmentProject> {
  return requestJSON<AssessmentProject>("/assessment/project", project)
}

// ---------------------------------------------------------------------------
// AI — photo analysis
// ---------------------------------------------------------------------------
export interface PhotoAnalysisResult {
  observations: string
  hazardTypes: string[]
  suggestedMode: string
  suggestedTask: string
  hrnSuggestions: {
    LO: { value: number; justification: string }
    FE: { value: number; justification: string }
    DPH: { value: number; justification: string }
    NP: { value: number; justification: string }
  }
  flags: string[]
}

export async function analysePhoto(file: File, siteLabel: string): Promise<PhotoAnalysisResult> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("site_label", siteLabel)

  const startResp = await fetch(`${API_BASE}/ai/photo/start`, { method: "POST", headers: authHeader(), body: formData })
  if (!startResp.ok) throw new Error(`Photo upload failed: ${startResp.statusText}`)
  const { job_id } = await startResp.json()

  const deadline = Date.now() + 120_000
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 3000))
    const pollResp = await fetch(`${API_BASE}/ai/photo/${job_id}`, { headers: authHeader() })
    if (!pollResp.ok) throw new Error(`Poll failed: ${pollResp.statusText}`)
    const job = await pollResp.json()
    if (job.status === "complete") {
      const raw = job.result
      return {
        observations: raw.observations,
        hazardTypes: raw.hazard_types,
        suggestedMode: raw.suggested_mode,
        suggestedTask: raw.suggested_task,
        hrnSuggestions: {
          LO: raw.hrn_suggestions.LO,
          FE: raw.hrn_suggestions.FE,
          DPH: raw.hrn_suggestions.DPH,
          NP: raw.hrn_suggestions.NP,
        },
        flags: raw.flags,
      }
    }
    if (job.status === "error") throw new Error(job.detail ?? "AI analysis failed")
  }
  throw new Error("Analysis timed out — please try again")
}

// ---------------------------------------------------------------------------
// AI — HRN validation
// ---------------------------------------------------------------------------
export interface ChallengedParameter {
  parameter: string
  enteredValue: number
  recommendedValue: number
  reason: string
}

export interface HRNValidationResult {
  valid: boolean
  challengedParameters: ChallengedParameter[]
  flags: string[]
  overallComment: string
}

export async function validateHrnAI(
  hrnParams: HRNParameters,
  hazardTypes: string[],
  observations: string,
): Promise<HRNValidationResult> {
  const raw = await requestJSON<any>("/ai/hrn/validate", {
    hrn_params: hrnParams,
    hazard_types: hazardTypes,
    observations,
  })
  return {
    valid: raw.valid,
    challengedParameters: (raw.challenged_parameters ?? []).map((p: any) => ({
      parameter: p.parameter,
      enteredValue: p.entered_value,
      recommendedValue: p.recommended_value,
      reason: p.reason,
    })),
    flags: raw.flags ?? [],
    overallComment: raw.overall_comment,
  }
}

export async function uploadHazardPhoto(
  projectNumber: string,
  hazardId: string,
  file: File,
): Promise<{ filepath: string }> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("hazard_id", hazardId)
  const response = await fetch(
    `${API_BASE}/assessment/project/${encodeURIComponent(projectNumber)}/photo`,
    { method: "POST", headers: authHeader(), body: formData },
  )
  if (!response.ok) await throwWithDetail(response, "Photo upload failed")
  return response.json()
}

export async function getProject(projectNumber: string): Promise<AssessmentProject> {
  return getJSON<AssessmentProject>(`/assessment/project/${encodeURIComponent(projectNumber)}`)
}

export async function listProjects(): Promise<ProjectListResponse> {
  return getJSON<ProjectListResponse>("/assessment/projects")
}

export async function generateProjectReport(projectNumber: string, format: "pdf" | "docx" = "pdf"): Promise<Blob> {
  const response = await fetch(`${API_BASE}/report/project/${encodeURIComponent(projectNumber)}?format=${format}`, { headers: authHeader() })
  if (!response.ok) {
    throw new Error(`Failed to generate report: ${response.statusText}`)
  }
  return response.blob()
}

// ---------------------------------------------------------------------------
// Compliance / Design Review
// ---------------------------------------------------------------------------
export interface TopologyComponent {
  id: string
  channel: string | null
  seriesGroup: string | null
}

export interface TopologyConnection {
  fromId: string
  toId: string
  fromPort: string | null
  toPort: string | null
  wireType: string
  label: string | null
}

export interface TopologyResult {
  components: TopologyComponent[]
  connections: TopologyConnection[]
}

export interface DrawingAnalysisResponse {
  drawingType: string
  componentsIdentified: { component: string; type: string; location: string; safetyRelevant: boolean }[]
  architectureAssessment: {
    detectedCategory: string
    detectedPl: string
    channelCount: string
    hasFeedbackMonitoring: boolean | null
    hasCrossMonitoring: boolean | null
    summary: string
  }
  conformances: { description: string; clauseReference: string }[]
  nonConformances: { severity: string; description: string; clauseReference: string; remediation: string }[]
  gapToTarget: string
  gapSummary: string
  overallVerdict: string
  topology: TopologyResult | null
  svgDiagram: string | null
}

export interface DesignReviewResponse {
  safetyFunctionsIdentified: { name: string; description: string; implementation: string; plClaimed: string; categoryClaimed: string }[]
  gaps: { severity: string; description: string; clauseReference: string; recommendation: string }[]
  coverageAssessment: string
  overallVerdict: string
  recommendations: string[]
}

export async function reviewDesignDocument(
  documentText: string,
  targetPl: string,
  targetCategory: string,
  raHazardIds?: string[],
  file?: File | null,
): Promise<DesignReviewResponse> {
  const formData = new FormData()
  if (file) formData.append("file", file)
  formData.append("document_text", documentText)
  formData.append("target_pl", targetPl)
  formData.append("target_category", targetCategory)
  if (raHazardIds?.length) formData.append("ra_hazard_ids", raHazardIds.join(","))

  const response = await fetch(`${API_BASE}/compliance/design-review`, {
    method: "POST",
    headers: authHeader(),
    body: formData,
  })
  if (!response.ok) await throwWithDetail(response, "Design review failed")
  return response.json()
}

export async function extractDocumentText(file: File): Promise<string> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await fetch(`${API_BASE}/compliance/extract-text`, { method: "POST", headers: authHeader(), body: formData })
  if (!response.ok) throw new Error(`Text extraction failed: ${response.statusText}`)
  const data = await response.json()
  return data.text
}

export async function analyseDrawing(
  file: File,
  drawingTitle: string,
  targetPl: string,
  targetCategory: string,
  context?: string,
  dxfFile?: File,
): Promise<DrawingAnalysisResponse> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("drawing_title", drawingTitle)
  formData.append("target_pl", targetPl)
  formData.append("target_category", targetCategory)
  if (context) formData.append("context", context)
  if (dxfFile) formData.append("dxf_file", dxfFile)

  const response = await fetch(`${API_BASE}/compliance/drawing`, { method: "POST", headers: authHeader(), body: formData })
  if (!response.ok) await throwWithDetail(response, "Drawing analysis failed")
  return response.json()
}

export interface DxfComponent {
  blockName: string
  tag: string
  description: string
  location: string
  componentType: string
  complianceType: string
  safetyRelevant: boolean
  safetyNote: string | null
}

export interface DxfParseResponse {
  sourceFilename: string
  dxfVersion: string
  totalInserts: number
  recognisedCount: number
  safetyCount: number
  unknownBlockCount: number
  components: DxfComponent[]
  unknownBlocks: string[]
  libraryGaps: string[]
  contextText: string
}

export async function parseDxf(file: File): Promise<DxfParseResponse> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await fetch(`${API_BASE}/compliance/dxf`, { method: "POST", headers: authHeader(), body: formData })
  if (!response.ok) await throwWithDetail(response, "DXF parse failed")
  return response.json()
}

export async function downloadComplianceReport(
  drawingTitle: string,
  targetPl: string,
  targetCategory: string,
  analysis: DrawingAnalysisResponse,
  format: "pdf" | "docx",
): Promise<void> {
  const response = await fetch(`${API_BASE}/compliance/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({
      drawingTitle,
      targetPl,
      targetCategory,
      format,
      analysis,
      svgDiagram: analysis.svgDiagram ?? null,
    }),
  })
  if (!response.ok) await throwWithDetail(response, "Report generation failed")

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  const safeName = drawingTitle.replace(/[^a-zA-Z0-9_\- ]/g, "").trim().replace(/ /g, "_").slice(0, 40)
  a.href = url
  a.download = `${safeName}_Compliance_Review.${format}`
  a.click()
  URL.revokeObjectURL(url)
}
