export interface TeamMember {
  name: string
  company: string
  role: string
}

export interface Annotation {
  type: string
  text: string
  x?: number
  y?: number
}

export interface PhotoEntry {
  filepath: string
  timestamp: string
  gpsLat?: number
  gpsLon?: number
  siteLabel: string
  equipmentRef?: string
  annotations: Annotation[]
}

export interface VoiceNote {
  filepath: string
  timestamp: string
  durationSeconds?: number
  transcript?: string
}

export interface HRNParameters {
  LO: number
  FE: number
  DPH: number
  NP: number
  justification?: Record<string, string>
}

export interface RiskBand {
  min: number
  max?: number
  label: string
  acceptable: boolean
  colour: string
}

export interface HazardEntry {
  id: string
  location: string
  assetId?: string
  mode: string
  task: string
  hazardTypes: string[]
  photos: PhotoEntry[]
  voiceNotes: VoiceNote[]
  typedNotes?: string
  measurements?: Record<string, string>
  hrnBefore: HRNParameters
  hrnScoreBefore: number
  riskBandBefore: string
  riskReductionMeasures: string[]
  standardsReferences: string[]
  hrnAfter?: HRNParameters
  hrnScoreAfter?: number
  riskBandAfter?: string
  aiValidationFlags?: string[]
  aiRecommendations?: string[]
}

export interface SafetyFunctionSpec {
  functionName: string
  plrRequired: string
  categoryRequired: string
  severity: string
  frequency: string
  avoidance: string
  sourceHazardIds: string[]
  notes?: string
}

export interface ProjectBrief {
  projectNumber: string
  client: string
  site: string
  machineOrLine: string
  assessmentDate: string
  team: TeamMember[]
  scopeDescription: string
  standardsApplicable: string[]
  lifecycleExclusions: string[]
}

export interface HRNScoreResponse {
  hrnScore: number
  riskBand: RiskBand
  acceptable: boolean
}

export interface PLRRequest {
  severity: string
  frequency: string
  avoidance: string
}

export interface PLRResultResponse {
  plrRequired: string
  sourceStandard: string
  parameterSelection: {
    severity: string
    frequency: string
    avoidance: string
  }
}

export interface AssessmentProject {
  projectId?: string
  createdAt: string
  updatedAt: string
  status: string
  projectBrief: ProjectBrief
  hazards: HazardEntry[]
  safetyFunctions?: SafetyFunctionSpec[]
  notes?: string
}

export interface ProjectListResponse {
  projectNumbers: string[]
}

export interface ReportDraftRequest {
  projectBrief: ProjectBrief
  hazards: HazardEntry[]
  safetyFunctions?: SafetyFunctionSpec[]
  notes?: string
}
