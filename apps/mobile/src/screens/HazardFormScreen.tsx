import React, { useState } from "react"
import {
  ActivityIndicator,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native"
import { useAudioRecorder, AudioModule, RecordingPresets } from "expo-audio"
import type { HazardEntry } from "../../../../../shared/types/assessment"
import type { PhotoAnalysisResult, HRNValidationResult, RiskReductionResult, VoiceTranscriptResult } from "../services/api"
import { validateHrn, recommendRiskReduction, transcribeVoice } from "../services/api"
import {
  HAZARD_TYPES,
  HRN_PARAMS,
  LIGHT_GREY,
  LIME,
  MODES,
  MID_GREY,
  NAVY,
  calcHrn,
  getRiskBand,
} from "../constants"

interface NewCaptureProps {
  existingHazard?: undefined
  photoUri: string
  siteLabel: string
  aiResult: PhotoAnalysisResult
  hazardCount: number
  onBack: () => void
  onSave: (entry: HazardEntry) => void
  onSaveAndAddAnother: (entry: HazardEntry) => void
  onUpdate?: never
}

interface EditProps {
  existingHazard: HazardEntry
  onUpdate: (entry: HazardEntry) => void
  onBack: () => void
  photoUri?: never
  siteLabel?: never
  aiResult?: never
  hazardCount?: never
  onSave?: never
  onSaveAndAddAnother?: never
}

type Props = NewCaptureProps | EditProps

// ---------------------------------------------------------------------------
// Sub-component: value picker row (cycles through allowed values)
// ---------------------------------------------------------------------------
function HrnPicker({
  param,
  value,
  onChange,
  challenged,
}: {
  param: "LO" | "FE" | "DPH" | "NP"
  value: number
  onChange: (v: number) => void
  challenged?: boolean
}) {
  const options = HRN_PARAMS[param]
  const idx = options.findIndex((o) => o.value === value)
  const current = options[idx] ?? options[0]

  function prev() {
    if (idx > 0) onChange(options[idx - 1].value)
  }
  function next() {
    if (idx < options.length - 1) onChange(options[idx + 1].value)
  }

  return (
    <View style={[pickerStyles.row, challenged && pickerStyles.rowChallenged]}>
      <Text style={pickerStyles.paramLabel}>{param}</Text>
      <Pressable onPress={prev} style={pickerStyles.arrow} disabled={idx === 0}>
        <Text style={[pickerStyles.arrowText, idx === 0 && pickerStyles.arrowDisabled]}>◀</Text>
      </Pressable>
      <View style={pickerStyles.valueBox}>
        <Text style={pickerStyles.value}>{current.value}</Text>
        <Text style={pickerStyles.valueLabel} numberOfLines={1}>{current.label}</Text>
      </View>
      <Pressable onPress={next} style={pickerStyles.arrow} disabled={idx === options.length - 1}>
        <Text style={[pickerStyles.arrowText, idx === options.length - 1 && pickerStyles.arrowDisabled]}>▶</Text>
      </Pressable>
    </View>
  )
}

const pickerStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#dde3ef",
    marginBottom: 8,
    paddingVertical: 10,
    paddingHorizontal: 12,
  },
  rowChallenged: { borderColor: "#FFC000", backgroundColor: "#fffbf0" },
  paramLabel: { width: 36, fontWeight: "700", color: NAVY, fontSize: 14 },
  arrow: { padding: 8 },
  arrowText: { fontSize: 16, color: NAVY },
  arrowDisabled: { color: "#ccc" },
  valueBox: { flex: 1, alignItems: "center" },
  value: { fontSize: 20, fontWeight: "700", color: NAVY },
  valueLabel: { fontSize: 11, color: MID_GREY, marginTop: 2 },
})

// ---------------------------------------------------------------------------
// Main screen
// ---------------------------------------------------------------------------
export default function HazardFormScreen(props: Props) {
  const isEditMode = props.existingHazard !== undefined
  const { onBack } = props

  const initMode = isEditMode ? props.existingHazard.mode : props.aiResult.suggestedMode
  const initTask = isEditMode ? props.existingHazard.task : props.aiResult.suggestedTask
  const initHazardTypes = isEditMode ? props.existingHazard.hazardTypes : props.aiResult.hazardTypes
  const initLO = isEditMode ? props.existingHazard.hrnBefore.LO : props.aiResult.hrnSuggestions.LO.value
  const initFE = isEditMode ? props.existingHazard.hrnBefore.FE : props.aiResult.hrnSuggestions.FE.value
  const initDPH = isEditMode ? props.existingHazard.hrnBefore.DPH : props.aiResult.hrnSuggestions.DPH.value
  const initNP = isEditMode ? props.existingHazard.hrnBefore.NP : props.aiResult.hrnSuggestions.NP.value
  const siteLabel = isEditMode ? props.existingHazard.location : props.siteLabel
  const photoUri = isEditMode ? (props.existingHazard.photos[0]?.filepath ?? "") : props.photoUri

  const [mode, setMode] = useState(initMode)
  const [task, setTask] = useState(initTask)
  const [selectedHazardTypes, setSelectedHazardTypes] = useState<string[]>(initHazardTypes)
  const [notes, setNotes] = useState(isEditMode ? (props.existingHazard.typedNotes ?? "") : "")

  const [LO, setLO] = useState(initLO)
  const [FE, setFE] = useState(initFE)
  const [DPH, setDPH] = useState(initDPH)
  const [NP, setNP] = useState(initNP)

  const hrnScore = calcHrn(LO, FE, DPH, NP)
  const band = getRiskBand(hrnScore)

  const [validating, setValidating] = useState(false)
  const [validation, setValidation] = useState<HRNValidationResult | null>(null)
  const [loadingRR, setLoadingRR] = useState(false)
  const [rrResult, setRrResult] = useState<RiskReductionResult | null>(null)
  const [selectedMeasures, setSelectedMeasures] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  const [postLO, setPostLO] = useState(isEditMode ? (props.existingHazard.hrnAfter?.LO ?? initLO) : initLO)
  const [postFE, setPostFE] = useState(isEditMode ? (props.existingHazard.hrnAfter?.FE ?? initFE) : initFE)
  const [postDPH, setPostDPH] = useState(isEditMode ? (props.existingHazard.hrnAfter?.DPH ?? initDPH) : initDPH)
  const [postNP, setPostNP] = useState(isEditMode ? (props.existingHazard.hrnAfter?.NP ?? initNP) : initNP)
  const postHrnScore = calcHrn(postLO, postFE, postDPH, postNP)
  const postBand = getRiskBand(postHrnScore)

  const [voiceState, setVoiceState] = useState<"idle" | "recording" | "processing" | "done">("idle")
  const [voiceResult, setVoiceResult] = useState<VoiceTranscriptResult | null>(null)
  const [voiceError, setVoiceError] = useState<string | null>(null)
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY)

  const challengedParams = new Set(validation?.challengedParameters.map((c) => c.parameter) ?? [])

  function toggleHazardType(ht: string) {
    setSelectedHazardTypes((prev) =>
      prev.includes(ht) ? prev.filter((x) => x !== ht) : [...prev, ht],
    )
  }

  function toggleMeasure(desc: string) {
    setSelectedMeasures((prev) =>
      prev.includes(desc) ? prev.filter((x) => x !== desc) : [...prev, desc],
    )
  }

  async function handleValidate() {
    setError(null)
    setValidating(true)
    setValidation(null)
    setRrResult(null)
    setSelectedMeasures([])
    try {
      const justification = isEditMode
        ? (props.existingHazard.hrnBefore.justification ?? {})
        : { LO: props.aiResult.hrnSuggestions.LO.justification, FE: props.aiResult.hrnSuggestions.FE.justification, DPH: props.aiResult.hrnSuggestions.DPH.justification, NP: props.aiResult.hrnSuggestions.NP.justification }
      const observations = isEditMode ? (props.existingHazard.typedNotes ?? "") : props.aiResult.observations
      const result = await validateHrn(
        { LO, FE, DPH, NP, justification },
        selectedHazardTypes,
        observations,
      )
      setValidation(result)

      // Auto-fetch risk reduction for Needs Review and above
      if (hrnScore >= 4) {
        setLoadingRR(true)
        try {
          const rr = await recommendRiskReduction(
            siteLabel, mode, task, selectedHazardTypes, hrnScore, band.label,
          )
          setRrResult(rr)
        } finally {
          setLoadingRR(false)
        }
      }
    } catch (e) {
      setError(`Validation failed: ${(e as Error).message}`)
    } finally {
      setValidating(false)
    }
  }

  async function startRecording() {
    if (Platform.OS === "web") {
      setVoiceError("Voice recording is not supported in the web preview — use the Expo Go app on your device")
      return
    }
    setVoiceError(null)
    try {
      const permission = await AudioModule.requestRecordingPermissionsAsync()
      if (!permission.granted) {
        setVoiceError("Microphone permission denied — enable it in device Settings")
        return
      }
      await audioRecorder.prepareToRecordAsync()
      audioRecorder.record()
      setVoiceState("recording")
    } catch (e) {
      setVoiceError(`Could not start recording: ${(e as Error).message}`)
    }
  }

  async function stopRecording() {
    try {
      await audioRecorder.stop()
      const uri = audioRecorder.uri
      if (!uri) { setVoiceState("idle"); return }
      setVoiceState("processing")
      const result = await transcribeVoice(uri, siteLabel)
      setVoiceResult(result)
      setVoiceState("done")
    } catch (e) {
      setVoiceError(`Transcription failed: ${(e as Error).message}`)
      setVoiceState("idle")
    }
  }

  function applyVoiceNote() {
    if (!voiceResult) return
    if (voiceResult.suggestedMode && MODES.includes(voiceResult.suggestedMode)) {
      setMode(voiceResult.suggestedMode)
    }
    if (voiceResult.suggestedTask) setTask(voiceResult.suggestedTask)
    if (voiceResult.hazardTypes.length > 0) {
      setSelectedHazardTypes((prev) => [
        ...new Set([...prev, ...voiceResult.hazardTypes.filter((ht) => HAZARD_TYPES.includes(ht))]),
      ])
    }
    if (voiceResult.typedNotes) {
      setNotes((n) => (n ? `${n}\n${voiceResult.typedNotes}` : voiceResult.typedNotes!))
    }
    setVoiceResult(null)
    setVoiceState("idle")
  }

  function buildEntry(): HazardEntry {
    const existing = isEditMode ? props.existingHazard : null
    const id = existing ? existing.id : `H${String(props.hazardCount + 1).padStart(2, "0")}`

    const hrnAfterFields = rrResult
      ? { hrnAfter: { LO: postLO, FE: postFE, DPH: postDPH, NP: postNP }, hrnScoreAfter: postHrnScore, riskBandAfter: postBand.label }
      : existing?.hrnAfter
        ? { hrnAfter: existing.hrnAfter, hrnScoreAfter: existing.hrnScoreAfter, riskBandAfter: existing.riskBandAfter }
        : {}

    return {
      id,
      location: siteLabel,
      mode,
      task,
      hazardTypes: selectedHazardTypes,
      photos: existing
        ? existing.photos
        : photoUri ? [{ filepath: photoUri, timestamp: new Date().toISOString(), siteLabel, annotations: [] as any[] }] : [],
      voiceNotes: existing ? existing.voiceNotes : [],
      typedNotes: notes || undefined,
      hrnBefore: { LO, FE, DPH, NP },
      hrnScoreBefore: hrnScore,
      riskBandBefore: band.label,
      riskReductionMeasures: selectedMeasures.length > 0 ? selectedMeasures : (existing?.riskReductionMeasures ?? []),
      standardsReferences: rrResult
        ? rrResult.measures.filter((m) => selectedMeasures.includes(m.description)).flatMap((m) => m.standardsReferences).filter((v, i, a) => a.indexOf(v) === i)
        : (existing?.standardsReferences ?? []),
      ...hrnAfterFields,
      aiValidationFlags: validation?.flags ?? existing?.aiValidationFlags ?? [],
      aiRecommendations: rrResult?.measures.map((m) => m.description) ?? existing?.aiRecommendations ?? [],
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={styles.header}>
        <Pressable onPress={onBack}>
          <Text style={styles.back}>‹ Back</Text>
        </Pressable>
        <Text style={styles.title}>Hazard Details</Text>
        <Text style={styles.subtitle}>{siteLabel}</Text>
      </View>

      <ScrollView style={styles.body} contentContainerStyle={styles.bodyContent}>
        {/* Photo + observations — new capture only */}
        {!isEditMode && (
          <>
            <Image source={{ uri: photoUri }} style={styles.photo} resizeMode="cover" />
            <View style={styles.card}>
              <Text style={styles.cardTitle}>AI Observations</Text>
              <Text style={styles.observations}>{props.aiResult.observations}</Text>
              {props.aiResult.flags.map((flag, i) => (
                <View key={i} style={styles.flagRow}>
                  <Text style={styles.flagText}>⚠ {flag}</Text>
                </View>
              ))}
            </View>
          </>
        )}

        {/* Voice note */}
        <Text style={styles.sectionLabel}>Voice Note</Text>
        {voiceState === "idle" && (
          <Pressable style={({ pressed }) => [styles.micBtn, pressed && { opacity: 0.75 }]} onPress={startRecording}>
            <Text style={styles.micIcon}>🎙</Text>
            <Text style={styles.micBtnText}>Record voice note</Text>
          </Pressable>
        )}
        {voiceState === "recording" && (
          <Pressable style={({ pressed }) => [styles.micBtn, styles.micBtnRecording, pressed && { opacity: 0.75 }]} onPress={stopRecording}>
            <Text style={styles.micIcon}>⏹</Text>
            <Text style={styles.micBtnText}>Recording… tap to stop</Text>
          </Pressable>
        )}
        {voiceState === "processing" && (
          <View style={styles.loadingRow}>
            <ActivityIndicator color={NAVY} />
            <Text style={styles.loadingText}>Transcribing…</Text>
          </View>
        )}
        {voiceState === "done" && voiceResult && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Transcript</Text>
            <Text style={styles.voiceTranscript}>{voiceResult.transcript}</Text>
            {(voiceResult.suggestedMode || voiceResult.suggestedTask || voiceResult.hazardTypes.length > 0) && (
              <Text style={styles.voiceExtracted}>
                {[
                  voiceResult.suggestedMode && `Mode: ${voiceResult.suggestedMode}`,
                  voiceResult.suggestedTask && `Task: ${voiceResult.suggestedTask}`,
                  voiceResult.hazardTypes.length > 0 && `Hazards: ${voiceResult.hazardTypes.join(", ")}`,
                ].filter(Boolean).join("  ·  ")}
              </Text>
            )}
            <View style={styles.voiceActions}>
              <Pressable style={({ pressed }) => [styles.applyBtn, pressed && { opacity: 0.75 }]} onPress={applyVoiceNote}>
                <Text style={styles.applyBtnText}>Apply to form</Text>
              </Pressable>
              <Pressable onPress={() => { setVoiceResult(null); setVoiceState("idle") }}>
                <Text style={styles.discardText}>Discard</Text>
              </Pressable>
            </View>
          </View>
        )}
        {voiceError && <Text style={styles.error}>{voiceError}</Text>}

        {/* Mode */}
        <Text style={styles.sectionLabel}>Mode</Text>
        <View style={styles.chipRow}>
          {MODES.map((m) => (
            <Pressable
              key={m}
              style={({ pressed }) => [styles.chip, mode === m && styles.chipActive, pressed && { opacity: 0.75 }]}
              onPress={() => setMode(m)}
            >
              <Text style={[styles.chipText, mode === m && styles.chipTextActive]}>{m}</Text>
            </Pressable>
          ))}
        </View>

        {/* Task */}
        <Text style={styles.sectionLabel}>Task</Text>
        <TextInput
          style={styles.input}
          value={task}
          onChangeText={setTask}
          placeholder="Describe the task"
          placeholderTextColor={MID_GREY}
        />

        {/* Hazard types */}
        <Text style={styles.sectionLabel}>Hazard Types</Text>
        <View style={styles.chipRow}>
          {HAZARD_TYPES.map((ht) => (
            <Pressable
              key={ht}
              style={({ pressed }) => [styles.chip, selectedHazardTypes.includes(ht) && styles.chipActive, pressed && { opacity: 0.75 }]}
              onPress={() => toggleHazardType(ht)}
            >
              <Text style={[styles.chipText, selectedHazardTypes.includes(ht) && styles.chipTextActive]}>
                {ht}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* HRN pickers */}
        <Text style={styles.sectionLabel}>HRN Parameters</Text>
        <HrnPicker param="LO" value={LO} onChange={setLO} challenged={challengedParams.has("LO")} />
        <HrnPicker param="FE" value={FE} onChange={setFE} challenged={challengedParams.has("FE")} />
        <HrnPicker param="DPH" value={DPH} onChange={setDPH} challenged={challengedParams.has("DPH")} />
        <HrnPicker param="NP" value={NP} onChange={setNP} challenged={challengedParams.has("NP")} />

        {/* HRN score badge */}
        <View style={[styles.hrnBadge, { backgroundColor: band.color }]}>
          <Text style={styles.hrnScore}>{hrnScore}</Text>
          <Text style={styles.hrnBand}>{band.label}</Text>
          {band.label === "Needs Review" && <Text style={styles.hrnAction}>Engineer review required</Text>}
          {band.label !== "Needs Review" && !band.acceptable && <Text style={styles.hrnAction}>Action required</Text>}
        </View>

        {/* Validate button */}
        <Pressable
          style={({ pressed }) => [styles.validateBtn, validating && styles.btnDisabled, pressed && !validating && { opacity: 0.75 }]}
          onPress={handleValidate}
          disabled={validating}
        >
          {validating ? (
            <ActivityIndicator color={NAVY} />
          ) : (
            <Text style={styles.validateBtnText}>Validate HRN with AI</Text>
          )}
        </Pressable>

        {/* Validation result */}
        {validation && (
          <View style={[styles.card, validation.valid ? styles.cardGood : styles.cardWarn]}>
            <Text style={styles.cardTitle}>
              {validation.valid ? "✓ HRN Parameters Validated" : "⚠ Parameters Challenged"}
            </Text>
            <Text style={styles.validationComment}>{validation.overallComment}</Text>
            {validation.challengedParameters.map((cp, i) => (
              <View key={i} style={styles.challengeRow}>
                <Text style={styles.challengeParam}>{cp.parameter}</Text>
                <Text style={styles.challengeText}>
                  Entered {cp.enteredValue} → Recommended {cp.recommendedValue}
                </Text>
                <Text style={styles.challengeReason}>{cp.reason}</Text>
              </View>
            ))}
            {validation.challengedParameters.length > 0 && (
              <Pressable
                style={({ pressed }) => [styles.applyAiBtn, pressed && { opacity: 0.75 }]}
                onPress={() => {
                  for (const cp of validation.challengedParameters) {
                    if (cp.parameter === "LO") setLO(cp.recommendedValue)
                    else if (cp.parameter === "FE") setFE(cp.recommendedValue)
                    else if (cp.parameter === "DPH") setDPH(cp.recommendedValue)
                    else if (cp.parameter === "NP") setNP(cp.recommendedValue)
                  }
                }}
              >
                <Text style={styles.applyAiBtnText}>Apply AI Suggestions</Text>
              </Pressable>
            )}
          </View>
        )}

        {/* Risk reduction */}
        {loadingRR && (
          <View style={styles.loadingRow}>
            <ActivityIndicator color={NAVY} />
            <Text style={styles.loadingText}>Getting risk reduction recommendations…</Text>
          </View>
        )}
        {rrResult && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Risk Reduction Recommendations</Text>
            <Text style={styles.rrNotes}>{rrResult.notes}</Text>
            {rrResult.measures.map((m, i) => (
              <Pressable
                key={i}
                style={({ pressed }) => [styles.measureRow, selectedMeasures.includes(m.description) && styles.measureSelected, pressed && { opacity: 0.75 }]}
                onPress={() => toggleMeasure(m.description)}
              >
                <Text style={styles.measureCheck}>{selectedMeasures.includes(m.description) ? "☑" : "☐"}</Text>
                <View style={styles.measureBody}>
                  <Text style={styles.measureDesc}>{m.description}</Text>
                  <Text style={styles.measureMeta}>
                    {m.hierarchyLevel}  ·  {m.estimatedHrnFactorReduction}
                  </Text>
                  {m.standardsReferences.length > 0 && (
                    <Text style={styles.measureRefs}>{m.standardsReferences.join("  |  ")}</Text>
                  )}
                </View>
              </Pressable>
            ))}
          </View>
        )}

        {/* Post-mitigation HRN */}
        {rrResult && (
          <>
            <Text style={styles.sectionLabel}>Post-Mitigation HRN Parameters</Text>
            <HrnPicker param="LO" value={postLO} onChange={setPostLO} />
            <HrnPicker param="FE" value={postFE} onChange={setPostFE} />
            <HrnPicker param="DPH" value={postDPH} onChange={setPostDPH} />
            <HrnPicker param="NP" value={postNP} onChange={setPostNP} />
            <View style={[styles.hrnBadge, { backgroundColor: postBand.color }]}>
              <Text style={styles.hrnScore}>{postHrnScore}</Text>
              <Text style={styles.hrnBand}>{postBand.label} (after measures)</Text>
              {postBand.label === "Needs Review" && <Text style={styles.hrnAction}>Engineer review required</Text>}
              {postBand.label !== "Needs Review" && !postBand.acceptable && <Text style={styles.hrnAction}>Action required</Text>}
              {postBand.acceptable && <Text style={styles.hrnAction}>Residual risk acceptable</Text>}
            </View>
          </>
        )}

        {/* Notes */}
        <Text style={styles.sectionLabel}>Notes (optional)</Text>
        <TextInput
          style={[styles.input, styles.notesInput]}
          value={notes}
          onChangeText={setNotes}
          placeholder="Add any additional observations…"
          placeholderTextColor={MID_GREY}
          multiline
          numberOfLines={3}
        />

        {error && <Text style={styles.error}>{error}</Text>}

        {/* Save buttons */}
        {isEditMode ? (
          <Pressable style={({ pressed }) => [styles.finishBtn, pressed && { opacity: 0.75 }]} onPress={() => props.onUpdate(buildEntry())}>
            <Text style={styles.finishBtnText}>Save Changes</Text>
          </Pressable>
        ) : (
          <>
            <Pressable style={({ pressed }) => [styles.saveBtn, pressed && { opacity: 0.75 }]} onPress={() => props.onSaveAndAddAnother(buildEntry())}>
              <Text style={styles.saveBtnText}>Save & Add Another →</Text>
            </Pressable>
            <Pressable style={({ pressed }) => [styles.finishBtn, pressed && { opacity: 0.75 }]} onPress={() => props.onSave(buildEntry())}>
              <Text style={styles.finishBtnText}>Save & Review Project</Text>
            </Pressable>
          </>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  header: {
    backgroundColor: NAVY,
    paddingTop: 56,
    paddingBottom: 20,
    paddingHorizontal: 24,
  },
  back: { color: LIME, fontSize: 16, marginBottom: 8 },
  title: { color: "#fff", fontSize: 20, fontWeight: "700" },
  subtitle: { color: MID_GREY, fontSize: 13, marginTop: 2 },
  body: { flex: 1, backgroundColor: "#f5f7fb" },
  bodyContent: { padding: 16 },
  photo: { width: "100%", height: 180, borderRadius: 12, marginBottom: 12 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#dde3ef",
  },
  cardGood: { borderColor: "#00B050", backgroundColor: "#f0fff4" },
  cardWarn: { borderColor: "#FFC000", backgroundColor: "#fffbf0" },
  cardTitle: { fontWeight: "700", color: NAVY, fontSize: 13, marginBottom: 6 },
  observations: { color: "#334e68", fontSize: 13, lineHeight: 19 },
  flagRow: {
    marginTop: 6,
    backgroundColor: "#fff8e1",
    borderRadius: 6,
    padding: 8,
  },
  flagText: { color: "#7a5c00", fontSize: 12 },
  sectionLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: NAVY,
    textTransform: "uppercase",
    letterSpacing: 0.6,
    marginBottom: 8,
    marginTop: 4,
  },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 14 },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 20,
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#dde3ef",
  },
  chipActive: { backgroundColor: NAVY, borderColor: NAVY },
  chipText: { fontSize: 12, color: NAVY },
  chipTextActive: { color: "#fff" },
  input: {
    backgroundColor: "#fff",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#dde3ef",
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 14,
    color: "#1a2a3a",
    marginBottom: 14,
  },
  notesInput: { minHeight: 80, textAlignVertical: "top" },
  hrnBadge: {
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
    marginBottom: 14,
  },
  hrnScore: { fontSize: 36, fontWeight: "800", color: NAVY },
  hrnBand: { fontSize: 16, fontWeight: "600", color: NAVY, marginTop: 2 },
  hrnAction: { fontSize: 12, color: NAVY, marginTop: 4, fontWeight: "600" },
  validateBtn: {
    backgroundColor: NAVY,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginBottom: 14,
  },
  btnDisabled: { opacity: 0.5 },
  validateBtnText: { color: "#fff", fontSize: 15, fontWeight: "700" },
  validationComment: { color: "#334e68", fontSize: 13, lineHeight: 18, marginBottom: 8 },
  challengeRow: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "#f0e4b0",
  },
  challengeParam: { fontWeight: "700", color: NAVY, fontSize: 12 },
  challengeText: { color: "#7a5c00", fontSize: 12, marginTop: 2 },
  challengeReason: { color: "#555", fontSize: 11, marginTop: 3 },
  applyAiBtn: { marginTop: 14, backgroundColor: LIME, borderRadius: 8, paddingVertical: 10, alignItems: "center" as const },
  applyAiBtnText: { color: NAVY, fontWeight: "700" as const, fontSize: 14 },
  loadingRow: { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 14 },
  loadingText: { color: MID_GREY, fontSize: 13 },
  rrNotes: { color: MID_GREY, fontSize: 12, marginBottom: 10 },
  measureRow: {
    flexDirection: "row",
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: "#f0f0f0",
    alignItems: "flex-start",
  },
  measureSelected: { backgroundColor: "#f0fff4" },
  measureCheck: { fontSize: 20, marginRight: 10, color: NAVY },
  measureBody: { flex: 1 },
  measureDesc: { fontSize: 13, color: "#1a2a3a", fontWeight: "500" },
  measureMeta: { fontSize: 11, color: MID_GREY, marginTop: 2 },
  measureRefs: { fontSize: 10, color: LIME, marginTop: 2, fontWeight: "600" },
  error: { color: "#d32f2f", fontSize: 13, marginBottom: 12 },
  micBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: "#fff",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#dde3ef",
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 14,
  },
  micBtnRecording: { borderColor: "#d32f2f", backgroundColor: "#fff5f5" },
  micIcon: { fontSize: 20 },
  micBtnText: { fontSize: 14, color: NAVY, fontWeight: "600" },
  voiceTranscript: { color: "#334e68", fontSize: 13, lineHeight: 19, marginBottom: 10 },
  voiceExtracted: { fontSize: 11, color: MID_GREY, marginBottom: 10, lineHeight: 16 },
  voiceActions: { flexDirection: "row", alignItems: "center", gap: 16 },
  applyBtn: {
    backgroundColor: LIME,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 9,
  },
  applyBtnText: { color: NAVY, fontWeight: "700", fontSize: 13 },
  discardText: { color: MID_GREY, fontSize: 13 },
  saveBtn: {
    backgroundColor: LIME,
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center",
    marginBottom: 10,
  },
  saveBtnText: { color: NAVY, fontSize: 16, fontWeight: "700" },
  finishBtn: {
    backgroundColor: NAVY,
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center",
    marginBottom: 20,
  },
  finishBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
})
