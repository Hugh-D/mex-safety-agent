import React, { useState } from "react"
import { StatusBar } from "expo-status-bar"
import type { AssessmentProject, HazardEntry } from "../../../../shared/types/assessment"
import type { PhotoAnalysisResult } from "./services/api"
import { getProject } from "./services/api"

import HomeScreen from "./screens/HomeScreen"
import NewProjectScreen from "./screens/NewProjectScreen"
import CaptureScreen from "./screens/CaptureScreen"
import HazardFormScreen from "./screens/HazardFormScreen"
import ReviewScreen from "./screens/ReviewScreen"

// ---------------------------------------------------------------------------
// Screen state machine
// ---------------------------------------------------------------------------
type Screen =
  | { name: "home" }
  | { name: "new-project" }
  | { name: "capture" }
  | { name: "hazard-form"; photoUri: string; siteLabel: string; aiResult: PhotoAnalysisResult }
  | { name: "review" }

export default function App() {
  const [screen, setScreen] = useState<Screen>({ name: "home" })
  const [project, setProject] = useState<AssessmentProject | null>(null)

  // -------------------------------------------------------------------------
  // Navigation
  // -------------------------------------------------------------------------
  function goHome() {
    setScreen({ name: "home" })
    setProject(null)
  }

  async function goOpenProject(projectNumber: string) {
    try {
      const loaded = await getProject(projectNumber)
      setProject(loaded)
    } catch {
      setProject({
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: "draft",
        projectBrief: {
          projectNumber,
          client: "", site: "", machineOrLine: "",
          assessmentDate: new Date().toISOString().split("T")[0],
          team: [], scopeDescription: "", standardsApplicable: [], lifecycleExclusions: [],
        },
        hazards: [],
      })
    }
    setScreen({ name: "review" })
  }

  function goStartProject(newProject: AssessmentProject) {
    setProject(newProject)
    setScreen({ name: "capture" })
  }

  function goCapture() {
    setScreen({ name: "capture" })
  }

  function goHazardForm(photoUri: string, siteLabel: string, aiResult: PhotoAnalysisResult) {
    setScreen({ name: "hazard-form", photoUri, siteLabel, aiResult })
  }

  function addHazardToProject(entry: HazardEntry): AssessmentProject | null {
    let updated: AssessmentProject | null = null
    setProject((prev) => {
      if (!prev) return prev
      updated = { ...prev, hazards: [...prev.hazards, entry], updatedAt: new Date().toISOString() }
      return updated
    })
    return updated
  }

  function handleSaveHazard(entry: HazardEntry) {
    addHazardToProject(entry)
    setScreen({ name: "review" })
  }

  function handleSaveAndAddAnother(entry: HazardEntry) {
    addHazardToProject(entry)
    setScreen({ name: "capture" })
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <>
      <StatusBar style="light" />

      {screen.name === "home" && (
        <HomeScreen
          onNewAssessment={() => setScreen({ name: "new-project" })}
          onOpenProject={goOpenProject}
        />
      )}

      {screen.name === "new-project" && (
        <NewProjectScreen onBack={goHome} onStart={goStartProject} />
      )}

      {screen.name === "capture" && project && (
        <CaptureScreen
          project={project}
          onBack={() => setScreen({ name: "review" })}
          onAnalysed={goHazardForm}
        />
      )}

      {screen.name === "hazard-form" && project && (
        <HazardFormScreen
          photoUri={screen.photoUri}
          siteLabel={screen.siteLabel}
          aiResult={screen.aiResult}
          hazardCount={project.hazards.length}
          onBack={goCapture}
          onSave={handleSaveHazard}
          onSaveAndAddAnother={handleSaveAndAddAnother}
        />
      )}

      {screen.name === "review" && project && (
        <ReviewScreen
          project={project}
          onAddHazard={goCapture}
          onHome={goHome}
        />
      )}
    </>
  )
}
