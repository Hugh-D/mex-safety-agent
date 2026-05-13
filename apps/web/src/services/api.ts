import type {
  HRNParameters,
  HRNScoreResponse,
  PLRRequest,
  PLRResultResponse,
  ReportDraftRequest,
  AssessmentProject,
  ProjectListResponse,
} from "../../../../shared/types/assessment"

const API_BASE = "http://localhost:8000/api"

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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!response.ok) await throwWithDetail(response, "API request failed")
  return response.json()
}

async function getJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
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
    headers: { "Content-Type": "application/json" },
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

export async function getProject(projectNumber: string): Promise<AssessmentProject> {
  return getJSON<AssessmentProject>(`/assessment/project/${projectNumber}`)
}

export async function listProjects(): Promise<ProjectListResponse> {
  return getJSON<ProjectListResponse>("/assessment/projects")
}

export async function generateProjectReport(projectNumber: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}/report/project/${projectNumber}`)
  if (!response.ok) {
    throw new Error(`Failed to generate report: ${response.statusText}`)
  }
  return response.blob()
}

// ---------------------------------------------------------------------------
// Compliance / Design Review
// ---------------------------------------------------------------------------
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
): Promise<DesignReviewResponse> {
  return requestJSON<DesignReviewResponse>("/compliance/design-review", {
    documentText,
    targetPl,
    targetCategory,
    raHazardIds,
  })
}

export async function extractDocumentText(file: File): Promise<string> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await fetch(`${API_BASE}/compliance/extract-text`, { method: "POST", body: formData })
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

  const response = await fetch(`${API_BASE}/compliance/drawing`, { method: "POST", body: formData })
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
  const response = await fetch(`${API_BASE}/compliance/dxf`, { method: "POST", body: formData })
  if (!response.ok) await throwWithDetail(response, "DXF parse failed")
  return response.json()
}
