FROM python:3.11-slim

WORKDIR /app

# Build context is the REPO ROOT (see docker-compose.yml). The standards docs
# and symbol library live outside api/ and are resolved by the code at
# /app/../docs and /app/../symbols — they MUST be baked into the image or the
# AI runs without its standards reference and DXF lookup silently fails.
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/
COPY docs/ /docs/
COPY symbols/ /symbols/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
