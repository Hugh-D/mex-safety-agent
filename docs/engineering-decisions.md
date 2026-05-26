# MEX Safety Platform — Engineering Decisions

This file records every significant decision point built into the app — why it was made, and how engineers should respond to it in practice. It is the primary source for future training material.

---

## ED-001 — HRN Boundary: "Needs Review" Zone

**Decision:** Scores between 4 and 6 (inclusive) are classified as **Needs Review** (amber) rather than being automatically assigned to Very Low (acceptable) or Low (action required).

**Why:** A single HRN score can mask very different underlying risk profiles. A score of 5 from `DPH=15 (fatality) × LO=0.033 × FE=1 × NP=1 ≈ 0.5` is not the same risk as `DPH=1 × LO=5 × FE=1 × NP=1 = 5`. The number is the same; the severity profile is not. Automatically classifying 5 as "acceptable" without engineer review is not defensible where fatality or serious injury is a credible outcome.

**How engineers should respond:**
- When the app flags Needs Review, examine the individual parameter values — particularly DPH.
- If DPH ≥ 8 (amputation or worse), treat the hazard as Low risk (action required) regardless of the final score.
- If DPH ≤ 2 (fracture or less) and the score is driven by low likelihood, a Very Low classification may be justified — document your reasoning in the Notes field.
- The classification you choose must be recorded and signed off. The app will not auto-resolve this band.

**Bands in full:**

| HRN Score | Band | Acceptable? |
|---|---|---|
| 0–1 | Acceptable | Yes |
| >1–<4 | Very Low | Yes |
| 4–6 | **Needs Review** | Engineer judgment required |
| >6–10 | Low | No — action required |
| >10–50 | Significant | No |
| >50–100 | High | No |
| >100–500 | Very High | No |
| >500–1000 | Extreme | No |
| >1000 | Unacceptable | No |

---

## ED-002 — LO Floor: 0.033 Requires Documented Administrative Controls

**Decision:** The app's AI will challenge any LO value of 0.033 (Almost Impossible) unless administrative controls are formally documented and verified on site.

**Why:** LO = 0.033 is the lowest possible value and produces very low HRN scores even with high severity parameters. Engineers can be tempted to select it to bring a score into an acceptable band. In practice, "almost impossible" is only defensible where there is documented evidence — a formal permit-to-work system, lockout/tagout procedure, or equivalent — not just verbal assurance.

**How engineers should respond:**
- Only select LO = 0.033 when you have sighted and recorded the specific administrative control (e.g. permit number, LOTO procedure reference).
- If challenged by the AI, either upgrade LO or add a note referencing the specific documented control.
- "We always do it that way" is not sufficient justification.

---

## ED-003 — No Visible Guard → LO Must Be ≥ 8

**Decision:** If no physical guard is visible in the photo, the AI will challenge any LO value below 8 (Probable).

**Why:** The absence of a physical guard means there is no engineered barrier preventing access to the hazard zone. In that context, a likelihood rating of "unlikely" or lower is not supportable — the person simply walks into the hazard.

**How engineers should respond:**
- If the photo does not clearly show a guard, assume none is present for rating purposes.
- If a guard exists but is not visible in the photo, take a second photo showing it and note its presence in the Equipment Reference field.
- LO can be reduced from 8 once a guard is confirmed and the post-mitigation HRN is being assessed.

---

## ED-004 — Daily Exposure → FE Must Be ≥ 2.5

**Decision:** If the task involves daily exposure to the hazard zone, the AI will challenge any FE value below 2.5 (Daily).

**Why:** FE represents how often a person is exposed to the hazard. If a task is performed every day, selecting "Monthly" or lower understates the true exposure frequency and produces an artificially low HRN score.

**How engineers should respond:**
- Match FE to the actual observed or documented frequency of the task.
- If frequency is uncertain, select the higher (more conservative) value.
- Planned maintenance tasks that occur weekly or less frequently may justify lower FE — but confirm with the site team.

---

## ED-005 — HRN Acceptance Threshold = 5

**Decision:** The platform uses HRN ≤ 5 as the acceptance threshold below which residual risk is considered tolerable.

**Why:** This is the threshold stated in the HRN methodology literature and commonly applied in Australian industrial safety practice. It aligns with the principle that residual risks below this level, after all reasonably practicable controls are applied, are tolerable.

**How engineers should respond:**
- The threshold applies to **post-mitigation** HRN, not the initial score.
- A pre-mitigation HRN of 5 does not mean the hazard requires no action — it means the current state happens to score low. Always assess whether the parameters are realistic (see ED-002, ED-003).
- For the Needs Review zone (ED-001), engineer sign-off is required before a score of 4–6 is treated as acceptable.

---

## ED-006 — DRAFT Watermark Until Audit Complete

**Decision:** All generated PDF reports carry a diagonal DRAFT watermark on every page until the environment variable `AUDIT_COMPLETE=true` is set on the server.

**Why:** The AI generates conclusions and recommendations that must be reviewed by a qualified person (CMSE or equivalent) before being issued to a client. An unreviewed AI-assisted report could contain errors in standards citations, incorrect risk classifications, or incomplete findings. The watermark prevents a draft being inadvertently used as a final document.

**How engineers should respond:**
- Reports generated during field assessment or desktop review are always DRAFT.
- The reviewing engineer must read the full report, correct any errors, and only then authorise the AUDIT_COMPLETE flag to be set for a final re-generation.
- DRAFT reports may be shared internally for review but must not be issued to clients or included in formal compliance documentation.

---

## ED-007 — AI Suggests, Engineer Decides

**Decision:** The AI pre-fills HRN parameters, hazard types, mode, and task from photo analysis. The engineer can accept, modify, or override any value. The AI may challenge parameter selections but cannot block the engineer from proceeding.

**Why:** The AI has no liability. The CMSE signing the report does. The engineer's professional judgment must govern every classification. The AI's role is to reduce transcription effort and prompt the engineer to consider parameters they might overlook — not to replace their assessment.

**How engineers should respond:**
- Treat AI-suggested values as a starting point, not a verdict.
- If the AI challenges a value and you disagree, override it and note your reasoning in the Notes field.
- If the AI suggests a hazard type you do not observe, deselect it.
- Your signature on the report means you accept professional responsibility for every value in it.

---

## ED-008 — Safety Distance Calculations Default to Table 2 (High Risk)

**Decision:** When the app performs safety distance lookups (AS/NZS 4024.1801), it defaults to Table 2 (High Risk) values unless the engineer explicitly selects Low Risk.

**Why:** AS/NZS 4024.1801 states: "Only risks arising from hazards such as friction or abrasion, where long-term or irreversible damage to the body is not foreseeable, can lead to low risks. In most machinery safety contexts, Table 2 (high risk) applies." Defaulting to the lower (Table 1) values without a justified risk assessment is non-conservative and not defensible.

**How engineers should respond:**
- Only select Low Risk (Table 1) when a risk assessment has confirmed the hazard falls within the narrow category of friction/abrasion with no foreseeable permanent injury.
- Document the justification for any Low Risk selection.
- When in doubt, use Table 2.

---

## ED-009 — No Interpolation in Safety Distance Tables

**Decision:** When input dimensions fall between values in AS/NZS 4024.1801 Tables 1 and 2, the app always selects the more conservative (safer) adjacent table value — never interpolates between them.

**Why:** The standard explicitly prohibits interpolation: "There shall be no interpolation of the values in Table 1" (and equally Table 2). The tables are derived from anthropometric data with built-in margins. Interpolating between rows or columns undermines those margins.

**Conservative selection rules:**
- For **a** (hazard zone height): use the row with the **higher** a value
- For **b** (protective structure height): use the column with the **lower** b value
- For **c** (safety distance): use the result with the **greater** c value

**How engineers should respond:**
- Never manually interpolate safety distances.
- If a site dimension falls between table values, apply the conservative rule above.
- If the resulting safety distance is impractical for the installation, this is a design problem to resolve — not a reason to interpolate.

---

## ED-010 — Standards Docs Loaded Selectively Per AI Endpoint

**Decision:** Each Claude AI function loads only the AS/NZS 4024 standards docs relevant to its task. Docs are read from `docs/` on first call and cached in-process for the server lifetime.

**Mapping:**

| Endpoint | Standards loaded |
|---|---|
| `analyse_photo` | 1302, 1303 |
| `validate_hrn` | 1302, 1303, 1501, 1801, 1803 |
| `recommend_risk_reduction` | 1201, 1501, 1503, 1703, 1801, 1803 |
| `extract_voice_fields` | none |
| `synthesise_conclusion` | all 9 docs |

**Why:** Loading all 9 docs (~8,000 lines) into every prompt would add significant token cost to lightweight calls like photo analysis that don't need minimum gap tables. Selective loading keeps context lean per call while still giving the AI authoritative reference for edge cases in each function. `synthesise_conclusion` gets everything because conclusions must reference any standard the assessment touched.

**How engineers should respond:**
- The AI's recommendations are backed by the specific standards listed above for each action — engineers can cite this mapping when explaining how the platform works.
- If a recommendation seems to reference the wrong standard, check whether that standard is in the loaded set for that endpoint.
- To add a doc to an endpoint's set, update `_system_blocks(...)` call in `api/services/claude_service.py` and add an entry here.

---

## ED-011 — Topology Extraction Runs in Parallel with Compliance Analysis

**Decision:** When a DXF file is uploaded alongside a drawing image, `extract_topology()` runs concurrently with `analyse_drawing()` using `asyncio.gather`. The topology result is attached to the `DrawingAnalysisResponse` alongside the compliance analysis — no extra wait time.

**Why:** Topology extraction and compliance analysis both require reading the image and are fully independent of each other. Running them sequentially would double the wall-clock time for users who provide a DXF. `asyncio.gather` lets them overlap completely, with the combined response only as slow as the slower of the two.

**How engineers should respond:**
- Topology data appears in the response only when a DXF is provided — the `topology` field is `null` otherwise.
- If topology extraction fails (e.g. AI returns malformed JSON), the compliance analysis still succeeds; `topology` is `null` and the error is logged.
- Do not add synchronous blocking calls between the two tasks — they must remain independent.

---

## ED-012 — Mobile PDF Download: expo-file-system/legacy + expo-sharing

**Decision:** On native device, the PDF report is downloaded to `FileSystem.cacheDirectory` using `expo-file-system/legacy`'s `downloadAsync`, then opened via `expo-sharing`'s `shareAsync`. This replaces the earlier approach of generating a blob in the browser.

**Why:** Expo's standard `expo-file-system` (v18+) removed `downloadAsync` from the default export. Using the `/legacy` sub-path restores it. `cacheDirectory` is writable without additional permissions on both iOS and Android. `shareAsync` opens the native share sheet, from which the user can pick a PDF viewer (Adobe Reader, iOS Files, etc.) or email the report.

**How engineers should respond:**
- Import from `expo-file-system/legacy`, not `expo-file-system`, or `downloadAsync` will be undefined.
- The safe filename strips non-alphanumeric chars: `projectNumber.replace(/[^a-zA-Z0-9\-_. ]/g, "_")` — MEX project numbers like "J# 2357" become "J_ 2357" in the cache filename. The PDF content is unaffected.
- Cache files are not permanent — they may be cleared by the OS. The report must be regenerated for a second share if the cache is cleared.

---

## ED-013 — Offline Capability: What Works Without a Signal

**Context:** Engineers use the app on industrial sites where mobile signal is unreliable or absent. This entry documents exactly what the app can and cannot do without connectivity, so engineers know what to expect and how to plan their workflow.

---

**What the engineer can do fully offline (no network required):**
- Create a new project and fill in site/machine details
- Capture photos — the camera is local; images are stored on the device
- Record voice notes — the microphone is local; audio is stored on the device
- Enter mode, task, hazard types, and typed notes manually
- Score HRN — LO × FE × DPH × NP is calculated on-device
- Get the risk band from the HRN score — this lookup is also on-device
- Save hazard entries — data is held in the app session while it remains open

**What queues until connectivity is restored:**
- AI photo analysis — the app will submit the photo to Claude once signal returns; until then, hazard types, mode, task, and HRN suggestions are blank and must be filled manually
- Voice transcription — audio is stored locally; the transcription and field extraction run when the server is reachable
- AI HRN validation — the "Validate HRN with AI" step requires the server; the engineer can still set HRN values manually
- Risk reduction recommendations — AI-generated; queued until connected
- Syncing project data to the server — local saves are pushed when connectivity returns

**What requires connectivity to complete:**
- PDF and Word report generation — this runs on the server; the engineer cannot produce a final report until the device has a working connection and all data has synced
- Viewing projects on a second device or via the web — server sync must complete first

---

**How engineers should respond in the field:**
- If signal is lost mid-assessment: continue capturing photos, recording voice notes, and entering HRN values manually. The math works without the network.
- Use the Notes field to record observations you would normally rely on AI analysis for — you can run AI validation retrospectively once you have signal (e.g. back at the vehicle or office).
- Do not close the app until all data has saved and synced, or you risk losing unsaved entries.
- Generate the PDF report after returning to a reliable connection, not on site.

---

*Last updated: 2026-05-22. Add new entries as decisions are made during development.*
