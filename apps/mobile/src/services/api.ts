import type {
  HRNParameters,
  HRNScoreResponse,
  PLRRequest,
  PLRResultResponse,
  ReportDraftRequest,
  AssessmentProject,
  ProjectListResponse,
} from "../../../../shared/types/assessment"

export const API_BASE =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api"

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------
const TIMEOUT_MS = 8000
const AI_TIMEOUT_MS = 120_000

function fetchWithTimeout(url: string, options?: RequestInit, timeoutMs = TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  return fetch(url, { ...options, signal: controller.signal }).finally(() =>
    clearTimeout(timer),
  )
}

async function requestJSON<T>(path: string, body: unknown, timeoutMs = TIMEOUT_MS): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }, timeoutMs)
  if (!response.ok) {
    const text = await response.text().catch(() => "")
    throw new Error(`API error ${response.status}: ${text || response.statusText}`)
  }
  return response.json()
}

async function getJSON<T>(path: string): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE}${path}`)
  if (!response.ok) throw new Error(`API error: ${response.statusText}`)
  return response.json()
}

// ---------------------------------------------------------------------------
// Deterministic endpoints
// ---------------------------------------------------------------------------
export async function scoreHRN(parameters: HRNParameters): Promise<HRNScoreResponse> {
  return requestJSON<HRNScoreResponse>("/assessment/hrn", parameters)
}

export async function determinePLR(request: PLRRequest): Promise<PLRResultResponse> {
  return requestJSON<PLRResultResponse>("/assessment/plr", request)
}

export async function listProjects(): Promise<ProjectListResponse> {
  return getJSON<ProjectListResponse>("/assessment/projects")
}

export async function getProject(projectNumber: string): Promise<AssessmentProject> {
  return getJSON<AssessmentProject>(`/assessment/project/${encodeURIComponent(projectNumber)}`)
}

export async function saveProject(project: AssessmentProject): Promise<AssessmentProject> {
  return requestJSON<AssessmentProject>("/assessment/project", project)
}

export async function generateProjectReport(projectNumber: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}/report/project/${encodeURIComponent(projectNumber)}`)
  if (!response.ok) throw new Error(`Failed to generate report: ${response.statusText}`)
  return response.blob()
}

// ---------------------------------------------------------------------------
// AI types
// ---------------------------------------------------------------------------
export interface HrnSuggestion {
  value: number
  justification: string
}

export interface PhotoAnalysisResult {
  observations: string
  hazardTypes: string[]
  suggestedMode: string
  suggestedTask: string
  hrnSuggestions: {
    LO: HrnSuggestion
    FE: HrnSuggestion
    DPH: HrnSuggestion
    NP: HrnSuggestion
  }
  flags: string[]
}

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

export interface RiskReductionMeasure {
  description: string
  hierarchyLevel: string
  standardsReferences: string[]
  estimatedHrnFactorReduction: string
}

export interface RiskReductionResult {
  measures: RiskReductionMeasure[]
  targetHrnAchievable: boolean
  notes: string
}

// ---------------------------------------------------------------------------
// AI endpoints
// ---------------------------------------------------------------------------
export async function analysePhoto(
  imageUri: string,
  siteLabel: string,
  equipmentRef?: string,
): Promise<PhotoAnalysisResult> {
  const formData = new FormData()

  if (imageUri.startsWith("blob:") || imageUri.startsWith("data:")) {
    const blob = await fetch(imageUri).then((r) => r.blob())
    formData.append("file", new File([blob], "photo.jpg", { type: blob.type || "image/jpeg" }))
  } else {
    formData.append("file", { uri: imageUri, type: "image/jpeg", name: "photo.jpg" } as any)
  }

  formData.append("site_label", siteLabel)
  if (equipmentRef) formData.append("equipment_ref", equipmentRef)

  // POST to /ai/photo/start — returns immediately with a job_id (no timeout: upload may take a few seconds)
  const startResp = await fetch(`${API_BASE}/ai/photo/start`, { method: "POST", body: formData })
  if (!startResp.ok) throw new Error(`Photo upload failed: ${startResp.statusText}`)
  const { job_id } = await startResp.json()

  // Poll /ai/photo/{job_id} every 3s for up to 120s
  const deadline = Date.now() + 120_000
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 3000))
    const pollResp = await fetchWithTimeout(`${API_BASE}/ai/photo/${job_id}`)
    if (!pollResp.ok) throw new Error(`Poll failed: ${pollResp.statusText}`)
    const job = await pollResp.json()
    if (job.status === "complete") { const raw = job.result; return {
      observations: raw.observations,
      hazardTypes: raw.hazard_types,
      suggestedMode: raw.suggested_mode,
      suggestedTask: raw.suggested_task,
      hrnSuggestions: { LO: raw.hrn_suggestions.LO, FE: raw.hrn_suggestions.FE, DPH: raw.hrn_suggestions.DPH, NP: raw.hrn_suggestions.NP },
      flags: raw.flags,
    }}
    if (job.status === "error") throw new Error(job.detail ?? "AI analysis failed")
  }
  throw new Error("Analysis timed out — please try again")
}

export async function validateHrn(
  hrnParams: HRNParameters,
  hazardTypes: string[],
  observations: string,
  riskReductionMeasures?: string[],
): Promise<HRNValidationResult> {
  const raw = await requestJSON<any>("/ai/hrn/validate", {
    hrn_params: hrnParams,
    hazard_types: hazardTypes,
    observations,
    risk_reduction_measures: riskReductionMeasures,
  }, AI_TIMEOUT_MS)
  return {
    valid: raw.valid,
    challengedParameters: raw.challenged_parameters?.map((p: any) => ({
      parameter: p.parameter,
      enteredValue: p.entered_value,
      recommendedValue: p.recommended_value,
      reason: p.reason,
    })) ?? [],
    flags: raw.flags,
    overallComment: raw.overall_comment,
  }
}

export interface VoiceTranscriptResult {
  transcript: string
  suggestedMode: string | null
  suggestedTask: string | null
  hazardTypes: string[]
  typedNotes: string | null
}

export async function transcribeVoice(
  audioUri: string,
  siteLabel: string,
): Promise<VoiceTranscriptResult> {
  const formData = new FormData()

  if (audioUri.startsWith("blob:") || audioUri.startsWith("data:")) {
    const blob = await fetch(audioUri).then((r) => r.blob())
    const ext = blob.type.includes("mp4") ? "m4a" : "webm"
    formData.append("file", new File([blob], `voice.${ext}`, { type: blob.type }))
  } else {
    formData.append("file", { uri: audioUri, type: "audio/mp4", name: "voice.m4a" } as any)
  }

  formData.append("site_label", siteLabel)

  const startResp = await fetchWithTimeout(`${API_BASE}/ai/voice/start`, { method: "POST", body: formData })
  if (!startResp.ok) throw new Error(`Voice upload failed: ${startResp.statusText}`)
  const { job_id } = await startResp.json()

  const deadline = Date.now() + 120_000
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 3000))
    const pollResp = await fetchWithTimeout(`${API_BASE}/ai/voice/${job_id}`)
    if (!pollResp.ok) throw new Error(`Poll failed: ${pollResp.statusText}`)
    const job = await pollResp.json()
    if (job.status === "complete") {
      const raw = job.result
      return { transcript: raw.transcript, suggestedMode: raw.suggested_mode, suggestedTask: raw.suggested_task, hazardTypes: raw.hazard_types ?? [], typedNotes: raw.typed_notes }
    }
    if (job.status === "error") throw new Error(job.detail ?? "Transcription failed")
  }
  throw new Error("Transcription timed out — please try again")
}

export async function recommendRiskReduction(
  location: string,
  mode: string,
  task: string,
  hazardTypes: string[],
  hrnScore: number,
  riskBand: string,
  existingMeasures?: string[],
): Promise<RiskReductionResult> {
  const raw = await requestJSON<any>("/ai/risk-reduction", {
    location,
    mode,
    task,
    hazard_types: hazardTypes,
    hrn_score: hrnScore,
    risk_band: riskBand,
    existing_measures: existingMeasures,
  }, AI_TIMEOUT_MS)
  return {
    measures: raw.measures?.map((m: any) => ({
      description: m.description,
      hierarchyLevel: m.hierarchy_level,
      standardsReferences: m.standards_references,
      estimatedHrnFactorReduction: m.estimated_hrn_factor_reduction,
    })) ?? [],
    targetHrnAchievable: raw.target_hrn_achievable,
    notes: raw.notes,
  }
}
