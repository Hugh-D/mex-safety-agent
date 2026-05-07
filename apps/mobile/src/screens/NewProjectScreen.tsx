import React, { useState } from "react"
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native"
import type { AssessmentProject } from "../../../../../shared/types/assessment"
import { LIGHT_GREY, LIME, MID_GREY, NAVY } from "../constants"

interface Props {
  onBack: () => void
  onStart: (project: AssessmentProject) => void
}

export default function NewProjectScreen({ onBack, onStart }: Props) {
  const [projectNumber, setProjectNumber] = useState("")
  const [client, setClient] = useState("")
  const [site, setSite] = useState("")
  const [machineOrLine, setMachineOrLine] = useState("")
  const [error, setError] = useState<string | null>(null)

  function handleStart() {
    if (!projectNumber.trim() || !client.trim() || !site.trim() || !machineOrLine.trim()) {
      setError("All fields are required.")
      return
    }
    const project: AssessmentProject = {
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: "draft",
      projectBrief: {
        projectNumber: projectNumber.trim(),
        client: client.trim(),
        site: site.trim(),
        machineOrLine: machineOrLine.trim(),
        assessmentDate: new Date().toISOString().split("T")[0],
        team: [],
        scopeDescription: "",
        standardsApplicable: ["AS/NZS 4024.1201", "ISO 13849-1:2015"],
        lifecycleExclusions: [],
      },
      hazards: [],
    }
    onStart(project)
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.back}>‹ Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>New Assessment</Text>
      </View>

      <ScrollView style={styles.body} contentContainerStyle={styles.bodyContent}>
        <Field label="Project Number" value={projectNumber} onChange={setProjectNumber} placeholder="e.g. MEX-2024-042" />
        <Field label="Client" value={client} onChange={setClient} placeholder="e.g. Acme Manufacturing Pty Ltd" />
        <Field label="Site" value={site} onChange={setSite} placeholder="e.g. Silverwater Plant — Building 3" />
        <Field label="Machine / Line" value={machineOrLine} onChange={setMachineOrLine} placeholder="e.g. Hydraulic Press Line 4" />

        {error && <Text style={styles.error}>{error}</Text>}

        <TouchableOpacity style={styles.startBtn} onPress={handleStart}>
          <Text style={styles.startBtnText}>Start Assessment →</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder: string
}) {
  return (
    <View style={fieldStyles.wrap}>
      <Text style={fieldStyles.label}>{label}</Text>
      <TextInput
        style={fieldStyles.input}
        value={value}
        onChangeText={onChange}
        placeholder={placeholder}
        placeholderTextColor={MID_GREY}
      />
    </View>
  )
}

const fieldStyles = StyleSheet.create({
  wrap: { marginBottom: 16 },
  label: { fontSize: 13, fontWeight: "600", color: NAVY, marginBottom: 6 },
  input: {
    backgroundColor: "#fff",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#dde3ef",
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: "#1a2a3a",
  },
})

const styles = StyleSheet.create({
  header: {
    backgroundColor: NAVY,
    paddingTop: 56,
    paddingBottom: 20,
    paddingHorizontal: 24,
  },
  back: { color: LIME, fontSize: 16, marginBottom: 8 },
  title: { color: "#fff", fontSize: 20, fontWeight: "700" },
  body: { flex: 1, backgroundColor: "#f5f7fb" },
  bodyContent: { padding: 20 },
  error: { color: "#d32f2f", marginBottom: 12, fontSize: 14 },
  startBtn: {
    marginTop: 8,
    backgroundColor: LIME,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
  },
  startBtnText: { color: NAVY, fontSize: 17, fontWeight: "700" },
})
