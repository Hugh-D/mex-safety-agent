import React, { useState } from "react"
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native"
import * as FileSystem from "expo-file-system/legacy"
import * as Sharing from "expo-sharing"
import type { AssessmentProject, HazardEntry, HRNParameters } from "../../../../../shared/types/assessment"
import { saveProject, generateProjectReport, API_BASE } from "../services/api"
import { LIGHT_GREY, LIME, MID_GREY, NAVY, getRiskBand, HRN_PARAMS, getParamLabel } from "../constants"

function HrnBreakdown({ params, score, label }: { params: HRNParameters; score: number; label: string }) {
  const band = getRiskBand(score)
  const rows: (keyof typeof HRN_PARAMS)[] = ["LO", "FE", "DPH", "NP"]
  return (
    <View style={detailStyles.breakdownBox}>
      <Text style={detailStyles.breakdownTitle}>{label}</Text>
      {rows.map((key) => (
        <View key={key} style={detailStyles.paramRow}>
          <Text style={detailStyles.paramKey}>{key}</Text>
          <Text style={detailStyles.paramValue}>{params[key]}</Text>
          <Text style={detailStyles.paramLabel}>{getParamLabel(key, params[key])}</Text>
        </View>
      ))}
      {params.justification && Object.keys(params.justification).length > 0 && (
        <>{Object.entries(params.justification).map(([k, v]) => (
          <Text key={k} style={detailStyles.justification}>{k}: {v as string}</Text>
        ))}</>
      )}
      <View style={[detailStyles.scoreBadge, { backgroundColor: band.color }]}>
        <Text style={detailStyles.scoreFormula}>
          {params.LO} × {params.FE} × {params.DPH} × {params.NP} = {score}
        </Text>
        <Text style={detailStyles.scoreBand}>{band.label}</Text>
      </View>
    </View>
  )
}

interface Props {
  project: AssessmentProject
  onAddHazard: () => void
  onEditHazard: (hazardId: string) => void
  onHome: () => void
}

export default function ReviewScreen({ project, onAddHazard, onEditHazard, onHome }: Props) {
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

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
      const projectNumber = project.projectBrief.projectNumber
      if (Platform.OS === "web") {
        const blob = await generateProjectReport(projectNumber)
        const url = (window as any).URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `MEX-RA-${projectNumber}.pdf`
        a.click()
        ;(window as any).URL.revokeObjectURL(url)
      } else {
        const safeName = projectNumber.replace(/[^a-zA-Z0-9\-_. ]/g, "_")
        const fileUri = `${FileSystem.cacheDirectory}MEX-RA-${safeName}.pdf`
        const result = await FileSystem.downloadAsync(
          `${API_BASE}/report/project/${encodeURIComponent(projectNumber)}`,
          fileUri,
        )
        if (result.status !== 200) throw new Error(`Server returned ${result.status}`)
        await new Promise<void>((resolve) =>
          Alert.alert(
            "Report Ready",
            "Select a PDF viewer (e.g. Adobe Reader, Files) from the share sheet to open the report.",
            [{ text: "Open Share Sheet", onPress: () => resolve() }],
          )
        )
        await Sharing.shareAsync(result.uri, {
          mimeType: "application/pdf",
          dialogTitle: `MEX-RA-${projectNumber}`,
          UTI: "com.adobe.pdf",
        })
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
    const expanded = expandedId === h.id

    return (
      <View style={styles.hazardRow}>
        <Pressable
          style={({ pressed }) => [styles.hazardSummary, pressed && { opacity: 0.85 }]}
          onPress={() => setExpandedId(expanded ? null : h.id)}
        >
          <View style={styles.hazardLeft}>
            <Text style={styles.hazardId}>{h.id}</Text>
            <View style={[styles.bandDot, { backgroundColor: band.color }]} />
          </View>
          <View style={styles.hazardBody}>
            <View style={styles.hazardBodyHeader}>
              <Text style={styles.hazardLocation}>{h.location}</Text>
              <Text style={styles.chevron}>{expanded ? "▾" : "▸"}</Text>
            </View>
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
            {!expanded && h.riskReductionMeasures.length > 0 && (
              <Text style={styles.measures} numberOfLines={2}>
                {h.riskReductionMeasures.slice(0, 2).join("; ")}
                {h.riskReductionMeasures.length > 2 ? ` +${h.riskReductionMeasures.length - 2} more` : ""}
              </Text>
            )}
          </View>
        </Pressable>

        {expanded && (
          <View style={styles.detailPanel}>
            <HrnBreakdown params={h.hrnBefore} score={h.hrnScoreBefore} label="Before Mitigation" />

            {h.hrnAfter && h.hrnScoreAfter != null && (
              <HrnBreakdown params={h.hrnAfter} score={h.hrnScoreAfter} label="After Mitigation" />
            )}

            {h.riskReductionMeasures.length > 0 && (
              <View style={detailStyles.section}>
                <Text style={detailStyles.sectionTitle}>Risk Reduction Measures</Text>
                {h.riskReductionMeasures.map((m, i) => (
                  <Text key={i} style={detailStyles.bullet}>• {m}</Text>
                ))}
              </View>
            )}

            {h.aiValidationFlags && h.aiValidationFlags.length > 0 && (
              <View style={detailStyles.section}>
                <Text style={detailStyles.sectionTitle}>AI Validation Flags</Text>
                {h.aiValidationFlags.map((f, i) => (
                  <Text key={i} style={detailStyles.flagBullet}>⚑ {f}</Text>
                ))}
              </View>
            )}

            {h.aiRecommendations && h.aiRecommendations.length > 0 && (
              <View style={detailStyles.section}>
                <Text style={detailStyles.sectionTitle}>AI Recommendations</Text>
                {h.aiRecommendations.map((r, i) => (
                  <Text key={i} style={detailStyles.bullet}>• {r}</Text>
                ))}
              </View>
            )}

            {h.hazardTypes.length > 0 && (
              <View style={detailStyles.section}>
                <Text style={detailStyles.sectionTitle}>Hazard Types</Text>
                <Text style={detailStyles.bullet}>{h.hazardTypes.join(", ")}</Text>
              </View>
            )}

            <Pressable
              style={({ pressed }) => [detailStyles.editBtn, pressed && { opacity: 0.75 }]}
              onPress={() => onEditHazard(h.id)}
            >
              <Text style={detailStyles.editBtnText}>Edit Hazard</Text>
            </Pressable>
          </View>
        )}
      </View>
    )
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={onHome}>
          <Text style={styles.back}>‹ Home</Text>
        </Pressable>
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

        <Pressable style={({ pressed }) => [styles.addBtn, pressed && { opacity: 0.75 }]} onPress={onAddHazard}>
          <Text style={styles.addBtnText}>+ Add Hazard</Text>
        </Pressable>

        <View style={styles.bottomRow}>
          <Pressable
            style={({ pressed }) => [styles.saveBtn, (saving || pressed) && styles.btnDisabled]}
            onPress={handleSave}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator color={NAVY} size="small" />
            ) : (
              <Text style={styles.saveBtnText}>{saved ? "✓ Saved" : "Save Project"}</Text>
            )}
          </Pressable>

          <Pressable
            style={({ pressed }) => [styles.reportBtn, (generatingReport || pressed) && styles.btnDisabled]}
            onPress={handleGenerateReport}
            disabled={generatingReport}
          >
            {generatingReport ? (
              <ActivityIndicator color={NAVY} size="small" />
            ) : (
              <Text style={styles.reportBtnText}>Generate Report</Text>
            )}
          </Pressable>
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

const detailStyles = StyleSheet.create({
  breakdownBox: {
    backgroundColor: LIGHT_GREY,
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
  },
  breakdownTitle: { fontSize: 11, fontWeight: "700", color: MID_GREY, textTransform: "uppercase", letterSpacing: 0.6, marginBottom: 8 },
  paramRow: { flexDirection: "row", alignItems: "center", marginBottom: 4 },
  paramKey: { width: 36, fontSize: 12, fontWeight: "700", color: NAVY },
  paramValue: { width: 40, fontSize: 12, color: NAVY },
  paramLabel: { flex: 1, fontSize: 12, color: "#334e68" },
  justification: { fontSize: 11, color: MID_GREY, fontStyle: "italic", marginTop: 2 },
  scoreBadge: { borderRadius: 6, padding: 8, marginTop: 8, alignItems: "center" },
  scoreFormula: { fontSize: 11, color: NAVY, fontWeight: "600" },
  scoreBand: { fontSize: 13, fontWeight: "800", color: NAVY, marginTop: 2 },
  section: { marginBottom: 10 },
  sectionTitle: { fontSize: 11, fontWeight: "700", color: MID_GREY, textTransform: "uppercase", letterSpacing: 0.6, marginBottom: 6 },
  bullet: { fontSize: 12, color: "#334e68", lineHeight: 18, marginBottom: 2 },
  flagBullet: { fontSize: 12, color: "#b45309", lineHeight: 18, marginBottom: 2 },
  editBtn: { backgroundColor: NAVY, borderRadius: 8, paddingVertical: 10, alignItems: "center", marginTop: 4 },
  editBtnText: { color: "#fff", fontSize: 13, fontWeight: "700" },
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
    borderWidth: 1,
    borderColor: "#dde3ef",
    overflow: "hidden",
  },
  hazardSummary: { flexDirection: "row" },
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
  hazardBodyHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  hazardLocation: { flex: 1, fontSize: 14, fontWeight: "600", color: NAVY },
  chevron: { fontSize: 16, color: MID_GREY, marginLeft: 8 },
  hazardTask: { fontSize: 12, color: MID_GREY, marginTop: 2 },
  hrnRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: 8 },
  hrnChip: { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  hrnChipText: { fontSize: 11, fontWeight: "700", color: NAVY },
  arrow: { fontSize: 14, color: MID_GREY },
  measures: { fontSize: 11, color: "#334e68", marginTop: 6, lineHeight: 15 },
  detailPanel: { padding: 12, paddingTop: 4, borderTopWidth: 1, borderTopColor: "#dde3ef" },
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
