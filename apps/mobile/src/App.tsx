import React, { useState } from "react"
import HomeScreen from "./screens/HomeScreen"
import NewProjectScreen from "./screens/NewProjectScreen"
import CaptureScreen from "./screens/CaptureScreen"
import HazardFormScreen from "./screens/HazardFormScreen"
import ReviewScreen from "./screens/ReviewScreen"
import type { AssessmentProject, HazardEntry } from "../../../../shared/types/assessment"
import type { PhotoAnalysisResult } from "./services/api"
import { getProject } from "./services/api"

type Screen =
  | { name: "Home" }
  | { name: "NewProject" }
  | { name: "Capture" }
  | { name: "HazardForm"; photoUri: string; siteLabel: string; aiResult: PhotoAnalysisResult }
  | { name: "EditHazard"; hazardId: string }
  | { name: "Review" }

export default function App() {
  const [screen, setScreen] = useState<Screen>({ name: "Home" })
  const [project, setProject] = useState<AssessmentProject | null>(null)

  function addHazard(entry: HazardEntry) {
    setProject((prev) =>
      prev ? { ...prev, hazards: [...prev.hazards, entry], updatedAt: new Date().toISOString() } : prev,
    )
  }

  function updateHazard(entry: HazardEntry) {
    setProject((prev) =>
      prev
        ? { ...prev, hazards: prev.hazards.map((h) => (h.id === entry.id ? entry : h)), updatedAt: new Date().toISOString() }
        : prev,
    )
  }

  async function openProject(projectNumber: string) {
    try {
      const p = await getProject(projectNumber)
      setProject(p)
      setScreen({ name: "Review" })
    } catch {
      setProject(null)
      setScreen({ name: "Home" })
    }
  }

  if (screen.name === "Home") {
    return (
      <HomeScreen
        onNewAssessment={() => setScreen({ name: "NewProject" })}
        onOpenProject={openProject}
      />
    )
  }

  if (screen.name === "NewProject") {
    return (
      <NewProjectScreen
        onBack={() => setScreen({ name: "Home" })}
        onStart={(p) => {
          setProject(p)
          setScreen({ name: "Capture" })
        }}
      />
    )
  }

  if (screen.name === "Capture" && project) {
    return (
      <CaptureScreen
        project={project}
        onBack={() => setScreen({ name: "Home" })}
        onAnalysed={(photoUri, siteLabel, aiResult) =>
          setScreen({ name: "HazardForm", photoUri, siteLabel, aiResult })
        }
      />
    )
  }

  if (screen.name === "HazardForm" && project) {
    return (
      <HazardFormScreen
        photoUri={screen.photoUri}
        siteLabel={screen.siteLabel}
        aiResult={screen.aiResult}
        hazardCount={project.hazards.length}
        onBack={() => setScreen({ name: "Capture" })}
        onSave={(entry) => {
          addHazard(entry)
          setScreen({ name: "Review" })
        }}
        onSaveAndAddAnother={(entry) => {
          addHazard(entry)
          setScreen({ name: "Capture" })
        }}
      />
    )
  }

  if (screen.name === "EditHazard" && project) {
    const hazard = project.hazards.find((h) => h.id === screen.hazardId)
    if (hazard) {
      return (
        <HazardFormScreen
          existingHazard={hazard}
          onBack={() => setScreen({ name: "Review" })}
          onUpdate={(entry) => {
            updateHazard(entry)
            setScreen({ name: "Review" })
          }}
        />
      )
    }
  }

  if (screen.name === "Review" && project) {
    return (
      <ReviewScreen
        project={project}
        onAddHazard={() => setScreen({ name: "Capture" })}
        onEditHazard={(hazardId) => setScreen({ name: "EditHazard", hazardId })}
        onHome={() => {
          setProject(null)
          setScreen({ name: "Home" })
        }}
      />
    )
  }

  // Fallback: screen requires a project but none is loaded — go Home
  return (
    <HomeScreen
      onNewAssessment={() => setScreen({ name: "NewProject" })}
      onOpenProject={openProject}
    />
  )
}
