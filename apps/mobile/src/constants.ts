export const NAVY = "#002559"
export const LIME = "#70bf54"
export const LIGHT_GREY = "#f2f4f7"
export const MID_GREY = "#8a9ab0"
export const RED = "#d32f2f"

export const HRN_PARAMS = {
  LO: [
    { value: 0.033, label: "Almost impossible" },
    { value: 1, label: "Highly unlikely" },
    { value: 1.5, label: "Unlikely" },
    { value: 2, label: "Possible" },
    { value: 5, label: "Even chance" },
    { value: 8, label: "Probable" },
    { value: 10, label: "Likely" },
    { value: 15, label: "Certain" },
  ],
  FE: [
    { value: 0.5, label: "Annually" },
    { value: 1, label: "Monthly" },
    { value: 1.5, label: "Weekly" },
    { value: 2.5, label: "Daily" },
    { value: 4, label: "Hourly" },
    { value: 5, label: "Constantly" },
  ],
  DPH: [
    { value: 0.1, label: "Scratch / bruise" },
    { value: 0.5, label: "Laceration / mild ill health" },
    { value: 1, label: "Minor fracture (fingers/toes)" },
    { value: 2, label: "Major fracture (hand/arm/leg)" },
    { value: 4, label: "Loss of 1–2 digits" },
    { value: 8, label: "Amputation / partial sense loss" },
    { value: 10, label: "Double amputation / total sense loss" },
    { value: 12, label: "Critical / permanent illness" },
    { value: 15, label: "Fatality" },
  ],
  NP: [
    { value: 1, label: "1–2 persons" },
    { value: 2, label: "3–7 persons" },
    { value: 4, label: "8–15 persons" },
    { value: 8, label: "16–50 persons" },
    { value: 12, label: "More than 50" },
  ],
}

export const HAZARD_TYPES = [
  "Crushing",
  "Impact",
  "Entanglement",
  "Drawing-in",
  "Friction and abrasion",
  "Burn/Scald",
  "Cutting",
  "Shearing",
  "Slipping",
  "Tripping",
  "Falling",
  "Being run over",
  "Ejection of parts",
  "Loss of stability",
  "Electrical shock",
  "Electrocution",
  "Noise",
  "Vibration",
  "Radiation",
  "Dust/fume inhalation",
  "Contact with hazardous substances",
]

export const MODES = ["Operation", "Maintenance", "Setup", "Cleaning", "Fault finding"]

export function calcHrn(LO: number, FE: number, DPH: number, NP: number): number {
  return Math.round(LO * FE * DPH * NP * 1000) / 1000
}

export function getRiskBand(score: number): { label: string; color: string; acceptable: boolean } {
  if (score <= 1) return { label: "Acceptable", color: "#00B050", acceptable: true }
  if (score < 4) return { label: "Very Low", color: "#92D050", acceptable: true }
  if (score <= 6) return { label: "Needs Review", color: "#FFA000", acceptable: false }
  if (score <= 10) return { label: "Low", color: "#FFFF00", acceptable: false }
  if (score <= 50) return { label: "Significant", color: "#FFC000", acceptable: false }
  if (score <= 100) return { label: "High", color: "#FF6600", acceptable: false }
  if (score <= 500) return { label: "Very High", color: "#FF0000", acceptable: false }
  if (score <= 1000) return { label: "Extreme", color: "#CC0000", acceptable: false }
  return { label: "Unacceptable", color: "#990000", acceptable: false }
}

export function getParamLabel(param: keyof typeof HRN_PARAMS, value: number): string {
  const options = HRN_PARAMS[param]
  return options.reduce((prev, curr) =>
    Math.abs(curr.value - value) < Math.abs(prev.value - value) ? curr : prev
  ).label
}
