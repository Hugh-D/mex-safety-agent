# Bug & Safety Fix — Deferred Items

Generated from `/review` + `/security-review` pass on 2026-05-18.
Items below were identified but not fixed in this session. Address before next production milestone.

---

## Low Priority

### 3. `project_number` validation — FIXED
~~**File:** `api/models/schemas.py`~~ Pattern now includes `#` → `r"^[\w\-\. #]{1,64}$"`. Existing "J# 2357" loads correctly.

### (was #3) PDF text overflow in some table cells
**File:** [api/models/schemas.py](../api/models/schemas.py) — `ProjectBrief.project_number`
**Detected by:** Security review (fix applied: `pattern=r"^[\w\-\. ]{1,64}$"`)
**Note:** The existing project file `api/data/projects/J# 2357.json` has `project_number = "J# 2357"` which contains `#` — **this will now fail Pydantic validation on load**. Before going to production either:
1. Rename the file and update the `project_number` field inside it to remove `#`, or
2. Broaden the pattern to include `#` if that's a valid MEX project number format: `r"^[\w\-\. #]{1,64}$"`

### 4. PDF text overflow in some table cells
**Detected by:** Known issue (pre-existing, listed in CLAUDE.md)
**File:** [api/services/report_generator.py](../api/services/report_generator.py)
**Issue:** Some table cells overflow their bounds in the generated PDF report.
**Deferred:** Acknowledged — needs MEX team to identify specific cells.

### 5. Mobile report download on native device not implemented
**Detected by:** Known issue (pre-existing, listed in CLAUDE.md)
**File:** [apps/mobile/src/screens/ReviewScreen.tsx](../apps/mobile/src/screens/ReviewScreen.tsx)
**Issue:** PDF download works in web preview but not on a native device — needs `expo-file-system` to write the PDF to device storage.
**Deferred:** Needs scoping with engineers before implementation.

---

## Already Fixed (this session — 2026-05-18)

| # | File | Fix |
|---|---|---|
| S1 | `api/main.py` | CORS wildcard injection — origin allowlist regex |
| S2 | `api/models/schemas.py` | Path traversal — `project_number` pattern |
| S3 | `api/models/schemas.py` | Unbounded floats — `ge`/`le` on all safety distance request fields |
| B1 | `api/services/claude_service.py` | Silent miss on missing standards docs — `logging.warning` |
| B2 | `api/routers/assessment.py` | Dict mutation — `ReachingThroughResponse` built explicitly |
| B3 | `apps/mobile/src/App.tsx` | `openProject` catch block — navigate Home on load failure |
| B4 | `apps/mobile/src/screens/HazardFormScreen.tsx` | Validate button shows disabled on every press |
| B5 | `apps/mobile/src/screens/HazardFormScreen.tsx` | Voice state machine fully wired — expo-audio re-added with expo-asset pin |
| B6 | `apps/mobile/src/App.tsx` | Null render guards — fallback to HomeScreen instead of blank screen |
| B7 | `api/models/schemas.py` | `project_number` pattern broadened to include `#` (MEX "J# NNNN" format) |
