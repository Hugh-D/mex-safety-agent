import React, { useEffect, useState } from "react"
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native"
import { listProjects } from "../services/api"
import { LIGHT_GREY, LIME, MID_GREY, NAVY } from "../constants"

interface Props {
  onNewAssessment: () => void
  onOpenProject: (projectNumber: string) => void
}

export default function HomeScreen({ onNewAssessment, onOpenProject }: Props) {
  const [projects, setProjects] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const result = await listProjects()
      setProjects(result.projectNumbers)
    } catch (e) {
      setError("Could not load projects. Is the API running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.brand}>MEX Engineering Group</Text>
        <Text style={styles.tagline}>Field Safety Assessment</Text>
      </View>

      <Pressable style={({ pressed }) => [styles.newBtn, pressed && { opacity: 0.75 }]} onPress={onNewAssessment}>
        <Text style={styles.newBtnText}>+ New Assessment</Text>
      </Pressable>

      <Text style={styles.sectionTitle}>Recent Projects</Text>

      {loading && <ActivityIndicator color={NAVY} style={{ marginTop: 24 }} />}
      {error && <Text style={styles.error}>{error}</Text>}

      {!loading && projects.length === 0 && (
        <Text style={styles.empty}>No projects yet. Start a new assessment above.</Text>
      )}

      <FlatList
        data={projects}
        keyExtractor={(item) => item}
        renderItem={({ item }) => (
          <Pressable style={({ pressed }) => [styles.projectRow, pressed && { opacity: 0.75 }]} onPress={() => onOpenProject(item)}>
            <Text style={styles.projectNumber}>{item}</Text>
            <Text style={styles.projectArrow}>›</Text>
          </Pressable>
        )}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fb" },
  header: {
    backgroundColor: NAVY,
    paddingTop: 56,
    paddingBottom: 24,
    paddingHorizontal: 24,
  },
  brand: { color: "#fff", fontSize: 20, fontWeight: "700" },
  tagline: { color: LIME, fontSize: 13, marginTop: 4 },
  newBtn: {
    margin: 20,
    backgroundColor: LIME,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
  },
  newBtnText: { color: NAVY, fontSize: 17, fontWeight: "700" },
  sectionTitle: {
    marginHorizontal: 20,
    marginBottom: 8,
    fontSize: 13,
    fontWeight: "600",
    color: MID_GREY,
    textTransform: "uppercase",
    letterSpacing: 0.8,
  },
  projectRow: {
    marginHorizontal: 20,
    marginBottom: 10,
    backgroundColor: "#fff",
    borderRadius: 10,
    paddingVertical: 16,
    paddingHorizontal: 18,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  projectNumber: { fontSize: 15, fontWeight: "600", color: NAVY },
  projectArrow: { fontSize: 22, color: MID_GREY },
  empty: { marginHorizontal: 20, marginTop: 16, color: MID_GREY, fontSize: 14 },
  error: { marginHorizontal: 20, marginTop: 16, color: "#d32f2f", fontSize: 14 },
})
