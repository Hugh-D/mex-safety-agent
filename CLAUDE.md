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
mex_safety_agent/
├── main.py                    FastAPI app, routing, serves static frontend
├── models/__init__.py         Pydantic data models
├── api/
│   ├── routes/                Endpoint handlers
│   └── data/
│       ├── hrn_tables.json    HRN lookup tables
│       └── plr_risk_graph.json  PLr risk graph data
├── docs/
│   ├── data-model.md          Full data model documentation
│   ├── report-format.md       Standardised report structure spec
│   ├── standards-reference.md Standards coverage matrix
│   └── agent-personas.md      Agent system prompts and expert knowledge
└── skills/*/SKILL.md          Individual agent skill definitions
```

## Two Modes

**Field Mode — Risk Assessment**
- Photo capture + hazard identification
- HRN scoring: LO × FE × DPH × NP (tables in `api/data/hrn_tables.json`)
- PLr determination: ISO 13849-1 risk graph S/F/P (lookup in `api/data/plr_risk_graph.json`)
- Branded report generation

**Design Mode — Compliance Review**
- Drawing parsing and component extraction
- Gap analysis against target PL/Category
- Redline report output matching MEX's branded report structure (see `docs/report-format.md`)

The risk assessment produces a PLr target. The compliance review checks designs against it.

---

## Standards Coverage
AS/NZS 4024 series, ISO 13849-1:2015, IEC 62061, IEC 61800-5-2, EN ISO 14119, ISO 14120, Australian WHS legislation.

---

## Build Sequence
1. ✅ Project structure created
2. ⏳ Symbol library (pending from engineering team)
3. 🔜 Report generation engine (next)
4. Field capture workflow
5. Design review mode

---

## Reference Files
Read on demand — do not preload everything.
- `docs/data-model.md` — Full data model
- `docs/report-format.md` — Standardised report structure
- `docs/standards-reference.md` — Standards coverage matrix
- `docs/agent-personas.md` — Agent system prompts and expert knowledge
- `skills/*/SKILL.md` — Individual agent skill definitions

---

## Lessons Learned
_Capture errors and corrections here as they occur._