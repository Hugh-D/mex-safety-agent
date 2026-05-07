# Standards Audit Log

## Purpose
Verify that all standards interpretations, data tables, clause references, and lookup logic encoded in the platform are accurate and current. This audit must be completed by a qualified person before the platform is used on live projects.

## Audit Scope

| Item | File | Auditor | Date | Status |
|---|---|---|---|---|
| HRN parameter tables (LO, FE, DPH, NP values and labels) | `api/data/hrn_tables.json` | | | ⬜ Not started |
| HRN risk banding thresholds and acceptance criteria | `api/data/hrn_tables.json` | | | ⬜ Not started |
| Hazard type vocabulary | `api/data/hazard_types.json` | | | ⬜ Not started |
| PLr risk graph lookup (S/F/P → PLr) | `api/data/plr_risk_graph.json` | | | ⬜ Not started |
| AS4024.1801 safe distance tables (reaching over/around) | `skills/standards-lookup/SKILL.md` | | | ⬜ Not started |
| AS4024.3610 conveyor e-stop requirements | `skills/standards-lookup/SKILL.md` | | | ⬜ Not started |
| ISO 13849-1 category/architecture definitions | `skills/compliance-reviewer/SKILL.md` | | | ⬜ Not started |
| IEC 61800-5-2 drive safety function definitions (STO, SS1) | `skills/compliance-reviewer/SKILL.md` | | | ⬜ Not started |
| Report boilerplate text (methodology, limits, liability) | `api/templates/boilerplate/` | | | ⬜ Not started |
| Agent persona standards reasoning | `docs/agent-personas.md` | | | ⬜ Not started |

## Auditor Requirements
- CMSE® or equivalent qualification
- Current working knowledge of AS/NZS 4024 series and ISO 13849-1
- Independent of the person who originally encoded the content

## Process
1. Auditor reviews each item against the current published standard
2. Records pass/fail and any corrections needed
3. Developer applies corrections
4. Auditor re-verifies corrected items
5. Sign-off recorded in this file

## Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| Auditor | | | |
| Developer | | | |
| Director | | | |
