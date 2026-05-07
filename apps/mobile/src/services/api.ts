import type {
  HRNParameters,
  HRNScoreResponse,
  PLRRequest,
  PLRResultResponse,
  ReportDraftRequest,
  AssessmentProject,
  ProjectListResponse,
} from "../../../../shared/types/assessment"

export const API_BASE = "http://localhost:8000/api"

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------
async function requestJSON<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(`API error: ${response.statusText}`)
  return response.json()
}

async function getJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
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
  return getJSON<AssessmentProject>(`/assessment/project/${projectNumber}`)
}

export async function saveProject(project: AssessmentProject): Promise<AssessmentProject> {
  return requestJSON<AssessmentProject>("/assessment/project", project)
}

export async function generateProjectReport(projectNumber: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}/report/project/${projectNumber}`)
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

  // On web, expo-image-picker returns a blob: URI — fetch it into a real File.
  // On native, use the { uri, type, name } shorthand that React Native understands.
  if (imageUri.startsWith("blob:") || imageUri.startsWith("data:")) {
    const blob = await fetch(imageUri).then((r) => r.blob())
    formData.append("file", new File([blob], "photo.jpg", { type: blob.type || "image/jpeg" }))
  } else {
    formData.append("file", { uri: imageUri, type: "image/jpeg", name: "photo.jpg" } as any)
  }

  formData.append("site_label", siteLabel)
  if (equipmentRef) formData.append("equipment_ref", equipmentRef)

  const response = await fetch(`${API_BASE}/ai/photo`, { method: "POST", body: formData })
  if (!response.ok) throw new Error(`Photo analysis failed: ${response.statusText}`)
  const raw = await response.json()
  // Snake_case → camelCase mapping from API response
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
  })
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
  })
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
