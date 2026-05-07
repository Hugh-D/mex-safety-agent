import React, { useState } from "react"
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Platform,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native"
import type { AssessmentProject, HazardEntry } from "../../../../../shared/types/assessment"
import { saveProject, generateProjectReport } from "../services/api"
import { LIGHT_GREY, LIME, MID_GREY, NAVY, getRiskBand } from "../constants"

interface Props {
  project: AssessmentProject
  onAddHazard: () => void
  onHome: () => void
}

export default function ReviewScreen({ project, onAddHazard, onHome }: Props) {
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const b = project.projectBrief
  const hazards = project.hazards
  const unresolved = hazards.filter((h) => !h.hrnScoreAfter || h.hrnScoreAfter > 5)

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      await saveProject(project)
      setSaved(true)
    } catch (e) {
      setError(`Save failed: ${(e as Error).message}`)
    } finally {
      setSaving(false)
    }
  }

  async function handleGenerateReport() {
    if (!saved) {
      Alert.alert("Save First", "Please save the project before generating a report.", [
        { text: "Save Now", onPress: handleSave },
        { text: "Cancel", style: "cancel" },
      ])
      return
    }
    setGeneratingReport(true)
    setError(null)
    try {
      const blob = await generateProjectReport(project.projectBrief.projectNumber)
      if (Platform.OS === "web") {
        const url = (window as any).URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `MEX-RA-${project.projectBrief.projectNumber}.pdf`
        a.click()
        ;(window as any).URL.revokeObjectURL(url)
      } else {
        Alert.alert(
          "Report Ready",
          "PDF report generated. Install the app on your device to save and share the file.",
          [{ text: "OK" }],
        )
      }
    } catch (e) {
      setError(`Report failed: ${(e as Error).message}`)
    } finally {
      setGeneratingReport(false)
    }
  }

  function renderHazard({ item: h }: { item: HazardEntry }) {
    const band = getRiskBand(h.hrnScoreBefore)
    const bandAfter = h.hrnScoreAfter != null ? getRiskBand(h.hrnScoreAfter) : null

    return (
      <View style={styles.hazardRow}>
        <View style={styles.hazardLeft}>
          <Text style={styles.hazardId}>{h.id}</Text>
          <View style={[styles.bandDot, { backgroundColor: band.color }]} />
        </View>
        <View style={styles.hazardBody}>
          <Text style={styles.hazardLocation}>{h.location}</Text>
          <Text style={styles.hazardTask} numberOfLines={1}>{h.mode} — {h.task}</Text>
          <View style={styles.hrnRow}>
            <View style={[styles.hrnChip, { backgroundColor: band.color }]}>
              <Text style={styles.hrnChipText}>HRN {h.hrnScoreBefore}</Text>
            </View>
            {bandAfter && h.hrnScoreAfter != null && (
              <>
                <Text style={styles.arrow}>→</Text>
                <View style={[styles.hrnChip, { backgroundColor: bandAfter.color }]}>
                  <Text style={styles.hrnChipText}>{h.hrnScoreAfter}</Text>
                </View>
              </>
            )}
          </View>
          {h.riskReductionMeasures.length > 0 && (
            <Text style={styles.measures} numberOfLines={2}>
              {h.riskReductionMeasures.slice(0, 2).join("; ")}
              {h.riskReductionMeasures.length > 2 ? ` +${h.riskReductionMeasures.length - 2} more` : ""}
            </Text>
          )}
        </View>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onHome}>
          <Text style={styles.back}>‹ Home</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Project Review</Text>
        <Text style={styles.subtitle}>{b.projectNumber}</Text>
      </View>

      {/* Summary strip */}
      <View style={styles.summaryStrip}>
        <SummaryTile label="Client" value={b.client} />
        <SummaryTile label="Site" value={b.site} />
        <SummaryTile label="Hazards" value={String(hazards.length)} />
        <SummaryTile label="Unresolved" value={String(unresolved.length)} highlight={unresolved.length > 0} />
      </View>

      {/* Hazard list */}
      {hazards.length === 0 ? (
        <View style={styles.emptyWrap}>
          <Text style={styles.emptyText}>No hazards recorded yet.</Text>
        </View>
      ) : (
        <FlatList
          data={hazards}
          keyExtractor={(h) => h.id}
          renderItem={renderHazard}
          contentContainerStyle={styles.listContent}
        />
      )}

      {/* Action bar */}
      <View style={styles.actionBar}>
        {error && <Text style={styles.error}>{error}</Text>}

        <TouchableOpacity style={styles.addBtn} onPress={onAddHazard}>
          <Text style={styles.addBtnText}>+ Add Hazard</Text>
        </TouchableOpacity>

        <View style={styles.bottomRow}>
          <TouchableOpacity
            style={[styles.saveBtn, saving && styles.btnDisabled]}
            onPress={handleSave}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator color={NAVY} size="small" />
            ) : (
              <Text style={styles.saveBtnText}>{saved ? "✓ Saved" : "Save Project"}</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.reportBtn, generatingReport && styles.btnDisabled]}
            onPress={handleGenerateReport}
            disabled={generatingReport}
          >
            {generatingReport ? (
              <ActivityIndicator color={NAVY} size="small" />
            ) : (
              <Text style={styles.reportBtnText}>Generate Report</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </View>
  )
}

function SummaryTile({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <View style={[summaryStyles.tile, highlight && summaryStyles.tileHighlight]}>
      <Text style={summaryStyles.value}>{value}</Text>
      <Text style={summaryStyles.label}>{label}</Text>
    </View>
  )
}

const summaryStyles = StyleSheet.create({
  tile: { flex: 1, alignItems: "center", paddingVertical: 10 },
  tileHighlight: { borderRadius: 8, backgroundColor: "rgba(255,100,0,0.12)" },
  value: { fontSize: 20, fontWeight: "800", color: "#fff" },
  label: { fontSize: 10, color: "rgba(255,255,255,0.7)", marginTop: 2, textTransform: "uppercase" },
})

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fb" },
  header: {
    backgroundColor: NAVY,
    paddingTop: 56,
    paddingBottom: 16,
    paddingHorizontal: 24,
  },
  back: { color: LIME, fontSize: 16, marginBottom: 8 },
  title: { color: "#fff", fontSize: 20, fontWeight: "700" },
  subtitle: { color: MID_GREY, fontSize: 13, marginTop: 2 },
  summaryStrip: {
    flexDirection: "row",
    backgroundColor: NAVY,
    paddingBottom: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 3,
    borderBottomColor: LIME,
  },
  listContent: { padding: 16 },
  hazardRow: {
    backgroundColor: "#fff",
    borderRadius: 10,
    marginBottom: 10,
    flexDirection: "row",
    borderWidth: 1,
    borderColor: "#dde3ef",
    overflow: "hidden",
  },
  hazardLeft: {
    width: 48,
    backgroundColor: LIGHT_GREY,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 14,
    gap: 6,
  },
  hazardId: { fontSize: 11, fontWeight: "700", color: NAVY },
  bandDot: { width: 10, height: 10, borderRadius: 5 },
  hazardBody: { flex: 1, padding: 12 },
  hazardLocation: { fontSize: 14, fontWeight: "600", color: NAVY },
  hazardTask: { fontSize: 12, color: MID_GREY, marginTop: 2 },
  hrnRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: 8 },
  hrnChip: { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  hrnChipText: { fontSize: 11, fontWeight: "700", color: NAVY },
  arrow: { fontSize: 14, color: MID_GREY },
  measures: { fontSize: 11, color: "#334e68", marginTop: 6, lineHeight: 15 },
  emptyWrap: { flex: 1, alignItems: "center", justifyContent: "center" },
  emptyText: { color: MID_GREY, fontSize: 15 },
  actionBar: {
    backgroundColor: "#fff",
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#dde3ef",
  },
  addBtn: {
    backgroundColor: LIGHT_GREY,
    borderRadius: 10,
    paddingVertical: 13,
    alignItems: "center",
    marginBottom: 10,
  },
  addBtnText: { color: NAVY, fontWeight: "600", fontSize: 15 },
  bottomRow: { flexDirection: "row", gap: 10 },
  saveBtn: {
    flex: 1,
    backgroundColor: NAVY,
    borderRadius: 10,
    paddingVertical: 13,
    alignItems: "center",
  },
  btnDisabled: { opacity: 0.5 },
  saveBtnText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  reportBtn: {
    flex: 1,
    backgroundColor: LIME,
    borderRadius: 10,
    paddingVertical: 13,
    alignItems: "center",
  },
  reportBtnText: { color: NAVY, fontWeight: "700", fontSize: 15 },
  error: { color: "#d32f2f", fontSize: 13, marginBottom: 8 },
})
