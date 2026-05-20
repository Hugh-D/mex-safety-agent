import React, { useState } from "react"
import {
  ActivityIndicator,
  Alert,
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
import * as ImagePicker from "expo-image-picker"
import type { AssessmentProject } from "../../../../../shared/types/assessment"
import type { PhotoAnalysisResult } from "../services/api"
import { analysePhoto } from "../services/api"
import { LIGHT_GREY, LIME, MID_GREY, NAVY } from "../constants"

interface Props {
  project: AssessmentProject
  onBack: () => void
  onAnalysed: (photoUri: string, siteLabel: string, result: PhotoAnalysisResult) => void
}

export default function CaptureScreen({ project, onBack, onAnalysed }: Props) {
  const [photoUri, setPhotoUri] = useState<string | null>(null)
  const [siteLabel, setSiteLabel] = useState("")
  const [equipmentRef, setEquipmentRef] = useState("")
  const [analysing, setAnalysing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function pickFromCamera() {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync()
      if (status !== "granted") {
        Alert.alert("Camera Permission", "Camera access is required to capture hazard photos.")
        return
      }
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: "images",
        quality: 0.7,
        allowsEditing: false,
      })
      if (result.canceled) return
      const uri = result.assets?.[0]?.uri
      if (!uri) {
        Alert.alert("Camera Error", "No photo was returned. Please try again or use Choose from Library.")
        return
      }
      setPhotoUri(uri)
    } catch (e) {
      Alert.alert("Camera Error", (e as Error).message ?? "Unknown error launching camera.")
    }
  }

  async function pickFromLibrary() {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
      if (status !== "granted") {
        Alert.alert("Photo Library", "Photo library access is required to select photos.")
        return
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: "images",
        quality: 0.7,
        allowsEditing: false,
      })
      if (result.canceled) return
      const uri = result.assets?.[0]?.uri
      if (!uri) {
        Alert.alert("Library Error", "No photo was returned. Please try again.")
        return
      }
      setPhotoUri(uri)
    } catch (e) {
      Alert.alert("Library Error", (e as Error).message ?? "Unknown error opening library.")
    }
  }

  async function handleAnalyse() {
    if (!photoUri) { setError("Please capture or select a photo first."); return }
    if (!siteLabel.trim()) { setError("Site label is required."); return }
    setError(null)
    setAnalysing(true)
    try {
      const result = await analysePhoto(photoUri, siteLabel.trim(), equipmentRef.trim() || undefined)
      onAnalysed(photoUri, siteLabel.trim(), result)
    } catch (e) {
      setError(`Analysis failed: ${(e as Error).message}`)
    } finally {
      setAnalysing(false)
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={styles.header}>
        <Pressable onPress={onBack}>
          <Text style={styles.back}>‹ Back</Text>
        </Pressable>
        <Text style={styles.title}>Capture Hazard</Text>
        <Text style={styles.subtitle}>{project.projectBrief.projectNumber}</Text>
      </View>

      <ScrollView style={styles.body} contentContainerStyle={styles.bodyContent}>
        {/* Photo area */}
        {photoUri ? (
          <View style={styles.previewWrap}>
            <Image source={{ uri: photoUri }} style={styles.preview} resizeMode="cover" />
            <Pressable style={({ pressed }) => [styles.retakeBtn, pressed && { opacity: 0.75 }]} onPress={() => setPhotoUri(null)}>
              <Text style={styles.retakeBtnText}>Retake</Text>
            </Pressable>
          </View>
        ) : (
          <View style={styles.photoPlaceholder}>
            <Text style={styles.photoIcon}>📷</Text>
            <Text style={styles.photoHint}>No photo selected</Text>
            <View style={styles.photoActions}>
              <Pressable style={({ pressed }) => [styles.cameraBtn, pressed && { opacity: 0.75 }]} onPress={pickFromCamera}>
                <Text style={styles.cameraBtnText}>Take Photo</Text>
              </Pressable>
              <Pressable style={({ pressed }) => [styles.galleryBtn, pressed && { opacity: 0.75 }]} onPress={pickFromLibrary}>
                <Text style={styles.galleryBtnText}>Choose from Library</Text>
              </Pressable>
            </View>
          </View>
        )}

        {/* Labels */}
        <View style={styles.fieldWrap}>
          <Text style={styles.fieldLabel}>Site Label *</Text>
          <TextInput
            style={styles.input}
            value={siteLabel}
            onChangeText={setSiteLabel}
            placeholder="e.g. Press nip point — feed side"
            placeholderTextColor={MID_GREY}
          />
        </View>
        <View style={styles.fieldWrap}>
          <Text style={styles.fieldLabel}>Equipment Reference (optional)</Text>
          <TextInput
            style={styles.input}
            value={equipmentRef}
            onChangeText={setEquipmentRef}
            placeholder="e.g. PRS-04, CV-12"
            placeholderTextColor={MID_GREY}
          />
        </View>

        {error && <Text style={styles.error}>{error}</Text>}

        <Pressable
          style={({ pressed }) => [styles.analyseBtn, (!photoUri || analysing) && styles.analyseBtnDisabled, pressed && !!photoUri && !analysing && { opacity: 0.75 }]}
          onPress={handleAnalyse}
          disabled={!photoUri || analysing}
        >
          {analysing ? (
            <ActivityIndicator color={NAVY} />
          ) : (
            <Text style={styles.analyseBtnText}>Analyse with AI →</Text>
          )}
        </Pressable>

        {analysing && (
          <Text style={styles.analysingHint}>
            AI is identifying hazards in this photo…
          </Text>
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
  bodyContent: { padding: 20 },
  photoPlaceholder: {
    backgroundColor: "#fff",
    borderRadius: 12,
    borderWidth: 2,
    borderColor: "#dde3ef",
    borderStyle: "dashed",
    alignItems: "center",
    paddingVertical: 32,
    marginBottom: 20,
  },
  photoIcon: { fontSize: 40, marginBottom: 8 },
  photoHint: { color: MID_GREY, fontSize: 14, marginBottom: 16 },
  photoActions: { flexDirection: "row", gap: 12 },
  cameraBtn: {
    backgroundColor: NAVY,
    borderRadius: 10,
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  cameraBtnText: { color: "#fff", fontWeight: "600", fontSize: 15 },
  galleryBtn: {
    backgroundColor: LIGHT_GREY,
    borderRadius: 10,
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  galleryBtnText: { color: NAVY, fontWeight: "600", fontSize: 15 },
  previewWrap: { marginBottom: 20, borderRadius: 12, overflow: "hidden" },
  preview: { width: "100%", height: 220 },
  retakeBtn: {
    position: "absolute",
    top: 10,
    right: 10,
    backgroundColor: "rgba(0,0,0,0.55)",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  retakeBtnText: { color: "#fff", fontSize: 13, fontWeight: "600" },
  fieldWrap: { marginBottom: 16 },
  fieldLabel: { fontSize: 13, fontWeight: "600", color: NAVY, marginBottom: 6 },
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
  error: { color: "#d32f2f", marginBottom: 12, fontSize: 14 },
  analyseBtn: {
    marginTop: 8,
    backgroundColor: LIME,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
  },
  analyseBtnDisabled: { opacity: 0.5 },
  analyseBtnText: { color: NAVY, fontSize: 17, fontWeight: "700" },
  analysingHint: { textAlign: "center", color: MID_GREY, fontSize: 13, marginTop: 12 },
})
