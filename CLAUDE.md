# MEX Safety Agent — CLAUDE.md

## Project Overview
AI-powered machine safety compliance review tool built for **MEX Engineering Group** (mexeng.com.au). Assists Certified Machine Safety Engineers (CMSEs) by parsing electrical drawings, running compliance reviews against Australian and international safety standards, and generating branded redline PDF reports.

**Users:** CMSEs and electrical engineers reviewing machine safety systems.
**Owner:** Buzzy — MEX Engineering Group.

---

## Workflow Principles

1. **Plan first, check in before starting** — for any multi-step task, write the plan and confirm before executing.
2. **No temporary fixes** — find root causes, minimal footprint, only touch what's necessary.
3. **Capture lessons after corrections** — when something goes wrong or gets corrected, update this file so the same mistake doesn't repeat.
4. **Verify before calling it done** — don't mark something complete without demonstrating it works.
5. **Simplicity first** — ask "is there a more elegant way?" before over-engineering.

---

## Core Principle
AI = brain (validates, cross-references, recommends, generates). Engineer = eyes and judgment. Use Claude for interpretation. Use code for calculation and rendering. Never use an LLM where deterministic code will do.

---

## Architecture

```
mex-safety-platform/
├── api/
│   ├── main.py                        FastAPI app, 5 routers, env-configurable CORS
│   ├── models/schemas.py              Pydantic data models
│   ├── routers/
│   │   ├── assessment.py              HRN + PLr + safety distance endpoints (AS4024.1801)
│   │   ├── claude.py                  5 AI endpoints (photo, hrn/validate, risk-reduction, voice, conclusion)
│   │   ├── compliance.py              Drawing + document review + topology extraction + compliance report download
│   │   ├── project.py                 Project CRUD
│   │   └── report.py                  PDF report generation
│   ├── services/
│   │   ├── claude_service.py          5 Claude AI functions — each loads specific standards docs
│   │   ├── voice_service.py           OpenAI gpt-4o-mini-transcribe → Claude field extraction
│   │   ├── compliance_service.py      Drawing vision + design doc review + extract_topology()
│   │   ├── hrn_plr.py                 Deterministic HRN + PLr lookup (never LLM)
│   │   ├── report_generator.py        Branded PDF via ReportLab, DRAFT watermark
│   │   ├── project_store.py           Flat-file JSON persistence, per-project thread locks
│   │   ├── standards.py               Standards catalogue loader
│   │   ├── symbol_lookup.py           DXF block name → type info
│   │   └── dxf_parser.py              Parses DXF bytes, classifies via symbol_lookup
│   ├── data/
│   │   ├── hrn_tables.json            HRN parameter lookup tables
│   │   ├── plr_risk_graph.json        PLr risk graph S/F/P data
│   │   ├── standards_catalogue.json   Single source of truth for all standards + years
│   │   └── projects/                  Flat-file project JSON store
│   └── tests/                         92 passing pytest tests
├── apps/
│   ├── mobile/src/                    Expo React Native — 5-screen field capture flow
│   │   ├── screens/HomeScreen.tsx
│   │   ├── screens/NewProjectScreen.tsx
│   │   ├── screens/CaptureScreen.tsx
│   │   ├── screens/HazardFormScreen.tsx  Voice mic + Apply/Discard UI
│   │   ├── screens/ReviewScreen.tsx
│   │   └── services/api.ts
│   └── web/src/                       Vite React — desktop review tool (run from apps/web/)
│       ├── App.tsx                    Calculator, Projects, Drawing Review, Document Review tabs
│       ├── components/DesignReview.tsx   PDF + Word compliance report download
│       ├── components/DocumentReview.tsx
│       ├── components/ProjectView.tsx    Project detail: hazard list, add hazard, AI photo + HRN validation
│       └── services/api.ts
├── docs/                              Standards reference docs + project docs
│   ├── AS4024_1201_*.md               General principles of design
│   ├── AS4024_1302_*.md               Risk assessment — hazardous substances
│   ├── AS4024_1303_*.md               Risk assessment practical guidance
│   ├── AS4024_1501_*.md               SRP/CS general principles
│   ├── AS4024_1502_*.md               SRP/CS validation
│   ├── AS4024_1503_*.md               SRP/CS design principles (partial)
│   ├── AS4024_1703_*.md               Access openings
│   ├── AS4024_1801_*.md               Safety distances (≡ ISO 13857:2008)
│   ├── AS4024_1803_*.md               Minimum gaps (≡ ISO 13854)
│   ├── AS4024_Cross_Reference_List.md Unified B.1/B.2/B.3 cross-reference
│   ├── engineering-decisions.md       All significant design decisions with rationale
│   ├── data-model.md                  Full data model documentation
│   ├── report-format.md               Standardised report structure spec
│   ├── standards-reference.md         Standards coverage matrix
│   └── agent-personas.md              Agent system prompts and expert knowledge
└── symbols/Elec_Symbols.dxf           Electrical symbol library (6.7 MB — should be Git LFS)
```

---

## Two Modes

**Field Mode — Risk Assessment**
- Photo capture + hazard identification (`POST /api/ai/photo`)
- Voice note capture → structured field extraction (`POST /api/ai/voice`)
- HRN scoring: LO × FE × DPH × NP (deterministic — `api/data/hrn_tables.json`)
- PLr determination: ISO 13849-1 risk graph S/F/P (deterministic — `api/data/plr_risk_graph.json`)
- Safety distance lookups: AS/NZS 4024.1801 Tables 1–7 (`POST /api/assessment/safety-distances/*`)
- Branded PDF report generation (`POST /api/report/draft`)
- Mobile: expandable hazard cards with full HRN breakdown, edit-hazard flow, PDF download via expo-file-system + expo-sharing
- Web: project detail view (ProjectView.tsx) with add-hazard form, AI photo analysis, AI HRN validation

**Design Mode — Compliance Review**
- Drawing parsing and component extraction (`POST /api/compliance/dxf`)
- Document review (`POST /api/compliance/design-review`)
- Topology extraction runs in parallel with compliance analysis when DXF provided (`extract_topology`)
- Gap analysis against target PL/Category
- PDF + Word compliance report download (`POST /api/compliance/report`)
- Redline report output matching MEX's branded report structure (see `docs/report-format.md`)

The risk assessment produces a PLr target. The compliance review checks designs against it.

---

## AI Standards Loading

Each Claude AI function loads specific AS/NZS 4024 standards docs into its context. Docs are read once and cached in-process. This is the authoritative mapping — do not change without updating `engineering-decisions.md`.

| Endpoint | Standards loaded |
|---|---|
| `analyse_photo` | 1302, 1303 |
| `validate_hrn` | 1302, 1303, 1501, 1801, 1803 |
| `recommend_risk_reduction` | 1201, 1501, 1503, 1703, 1801, 1803 |
| `extract_voice_fields` | none (extraction only) |
| `synthesise_conclusion` | all 9 docs |

---

## Standards Coverage
AS/NZS 4024 series (1201, 1302, 1303, 1501, 1502, 1503, 1703, 1801, 1803), ISO 13849-1:2015, IEC 62061, IEC 61800-5-2, EN ISO 14119, ISO 14120, Australian WHS legislation.

---

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude AI calls |
| `OPENAI_API_KEY` | Yes | Voice transcription (gpt-4o-mini-transcribe) |
| `API_PORT` | No | API port (default 8000) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins. Defaults to localhost:5173, 19006, 19007 |
| `AUDIT_COMPLETE` | No | Set `true` to remove DRAFT watermark from PDF reports |

---

## Running the Project

```bash
# API
cd api && uvicorn main:app --reload --port 8000

# Mobile (browser)
cd apps/mobile && npx expo start --web

# Web
cd apps/web && npm run dev

# Tests
cd api && python -m pytest tests/ -v
```

---

## Build Sequence
1. ✅ Project structure
2. ✅ Symbol library — DXF parser + symbol_lookup built; physical symbols pending engineering team
3. ✅ Report generation engine — branded PDF, DRAFT watermark, HRN risk bands
4. ✅ Field capture workflow — 5-screen mobile flow, photo, voice, HRN, PLr, report; expandable hazard cards + edit-hazard flow; PDF download on device via expo-file-system + expo-sharing
5. ✅ Web risk assessment — ProjectView with add-hazard, AI photo analysis, AI HRN validation, report download
6. ⏳ Design review mode — compliance service + topology extraction + PDF/Word download exists; needs further testing and UX polish
7. 🔜 PostgreSQL migration — deferred, pre-deployment only
8. 🔜 Training pack — engineering-decisions.md is primary source material

---

## Known Issues / Deferred
- PDF text overflow in some table cells (acknowledged, deferred)
- ~~Mobile report download on native device~~ — DONE: `expo-file-system/legacy` downloads to `cacheDirectory`, `expo-sharing` opens share sheet; user selects PDF viewer
- Conclusion synthesis too verbose — needs MEX team redline example before tightening
- No CI/CD, no Dockerfile
- No rate-limiting or API auth — cost-liability vector, must resolve before production
- `symbols/Elec_Symbols.dxf` is 6.7 MB committed to git — should be Git LFS
- AS4024.1503 doc is partial — clauses 1–11 + annexes A–B only
- Web hazard photos not persisted — `photos: []` stored in JSON; blob URL only lives in current browser session. Pre-production: add server-side photo storage endpoint.
- All changes uncommitted — 26 modified files, several untracked

---

## Reference Files
Read on demand — do not preload everything.
- `docs/data-model.md` — Full data model
- `docs/report-format.md` — Standardised report structure
- `docs/standards-reference.md` — Standards coverage matrix
- `docs/agent-personas.md` — Agent system prompts and expert knowledge
- `docs/engineering-decisions.md` — All significant design decisions with rationale

---

## Lessons Learned
- **Restart the API server after adding new routes.** New FastAPI routes are not picked up by a running server even with `--reload` if the server was started before the route file existed. Confirm routes are registered via `/openapi.json` before testing.
- **System prompt updates are reactive only.** Do not speculatively update `claude_service.py` system prompts — only update when new standards docs or confirmed requirements land.
- **Standards docs go in `docs/` and are loaded selectively per endpoint** — not globally into every prompt. See the AI Standards Loading table above.
- **Vite dev server must be started from `apps/web/`**, not the project root. Running `vite` from the root serves 404 on all routes — `index.html` is not found. Always: `cd apps/web && npm run dev`.
