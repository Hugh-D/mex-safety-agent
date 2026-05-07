# MEX Safety Platform — Project Brief

## What Is This?

A unified AI-powered platform for MEX Engineering Group's Machine Safety Division that covers the full machine safety lifecycle — from field-based risk assessment through to safety system design review and compliance reporting.

## The Problem

MEX engineers currently spend the majority of their report production time on:
- Formatting and assembling standardised report documents (copy-paste from Word templates)
- Manually cross-referencing findings against safety standards (AS/NZS 4024, ISO 13849)
- Calculating HRN scores and determining PLr targets
- Writing repetitive boilerplate sections that are identical across reports
- Manually reviewing electrical drawings for compliance gaps

The field observation and engineering judgment is the valuable work. Everything downstream of that is automation-ready.

## The Solution

One platform with two modes:

### Field Mode — Risk Assessment
Engineers capture hazards on site using a mobile app with built-in geotagged camera, voice notes, and typed observations. The AI validates their HRN parameters, cross-references standards, and generates a branded risk assessment report matching MEX's exact format.

### Design Mode — Safety Compliance Review
Engineers upload electrical drawings and equipment lists. The AI parses components, reviews the safety circuit design against the PLr target from the risk assessment, and generates a redline compliance report with schematic output.

### The Bridge
The risk assessment produces a PLr target (e.g., PLd, Category 3). The compliance review checks the proposed safety system design against that target. One feeds the other.

## Who Uses It

- **CMSEs (Certified Machinery Safety Experts)** — Primary users, conduct field assessments and design reviews
- **Senior engineers** — Review and sign-off on AI-generated reports
- **Directors** — Oversight and quality assurance

## Success Criteria

- Significant reduction in report turnaround time (from days to hours)
- Standardised report format across all engineers
- Every finding linked to a specific standard clause reference
- PLr determination automated from hazard data
- Zero manual formatting — reports are generated, not assembled

## Build Sequence

1. **Merge projects** — Unify risk assessment and compliance review into single platform
2. **Symbol library** — Receive DXF symbol library from engineering team (blocks schematic rendering)
3. **Report generation engine** — Build the output first using test data
4. **Field capture workflow** — Mobile app for on-site data capture
5. **Design review mode** — Connect risk assessment output to compliance review input

## Standards Covered

AS/NZS 4024.1201, AS/NZS 4024.1801, AS/NZS 4024.1503, AS/NZS 4024.3610, ISO 13849-1:2015, ISO 13849-2, IEC 62061, IEC 61800-5-2, EN ISO 14119, ISO 14120, AS/NZS 4024.1302, Australian WHS legislation

## Tech Stack

React Native (mobile) · React/TypeScript (web) · Python FastAPI (API) · PostgreSQL · Claude API (claude-sonnet-4-6) · ReportLab · ezdxf · Whisper/Deepgram (STT)
