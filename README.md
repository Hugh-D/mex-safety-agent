# MEX Safety Agent — Backend

Machine safety compliance review system for MEX Engineering Group.
Analyses electrical drawings against AS4024, ISO 13849-1, and IEC 61800-5-2.

---

## Prerequisites

- Python 3.11 or later
- An Anthropic API key (get one at console.anthropic.com)

---

## Setup — first time only

### 1. Clone or copy this folder to your machine

### 2. Create a virtual environment

```bash
cd mex_safety_agent
python -m venv venv
```

### 3. Activate the virtual environment

Windows:
```bash
venv\Scripts\activate
```

Mac / Linux:
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set your Anthropic API key

Windows (Command Prompt):
```bash
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxx"
```

Mac / Linux:
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

> Tip: Add this to a `.env` file and use `python-dotenv` to avoid setting it every session.

---

## Running the server

```bash
python main.py
```

The server starts at **http://localhost:8000**

- API docs (interactive): http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## API Endpoints

### 1. Parse a drawing
```
POST /api/parse/drawing
Content-Type: multipart/form-data
Body: file = <your PDF>
```

Returns: identified components, wiring observations, safety concerns.

### 2. Run compliance review
```
POST /api/review/
Content-Type: application/json
Body: {
  "project": { ... project data ... },
  "parse_result": { ... optional, from step 1 ... }
}
```

Returns: overall status, PL achievability, list of findings with standard references and redline actions.

### 3. Export redline PDF
```
POST /api/export/pdf
Content-Type: application/json
Body: {
  "project": { ... },
  "review_result": { ... from step 2 ... },
  "parse_result": { ... optional ... }
}
```

Returns: branded MEX redline report PDF (download).

---

## Typical workflow

1. Engineer uploads drawing PDF → `/api/parse/drawing`
2. Engineer submits project data + equipment list + parse result → `/api/review/`
3. System returns findings → engineer reviews in browser UI
4. Engineer triggers export → `/api/export/pdf` → downloads redline report

---

## Project structure

```
mex_safety_agent/
├── main.py                     # FastAPI app, routes, CORS
├── requirements.txt
├── models/
│   └── __init__.py             # Pydantic data models
├── routers/
│   ├── parse.py                # /api/parse
│   ├── review.py               # /api/review
│   └── export.py               # /api/export
├── services/
│   ├── claude_client.py        # Anthropic API wrapper
│   ├── parser_service.py       # Drawing analysis logic
│   ├── review_service.py       # Compliance review logic
│   └── export_service.py       # PDF generation
└── static/                     # Optional: serve frontend files
```

---

## Notes

- PDF size limit: 20 MB per upload
- Both vector and scanned/raster PDFs are supported
- The compliance review agent uses Claude claude-opus-4-5
- API costs: roughly AUD $0.05–0.15 per full review depending on drawing complexity

---

## Next steps (Stage 2)

- Equipment library: SQLite database of SICK, AB, Pilz, Schmersal, ABB devices with PL ratings
- Frontend: serve the browser UI from `/static`
- Auth: add API key header for multi-engineer access
- Deployment: Railway or Fly.io for hosted access (~AUD $25/month)

---

## Support

Internal MEX tool — contact the MEX digital team for issues.
