/* MEX Safety Agent — API layer */
const API = (() => {
  const BASE = 'https://mex-safety-agent-production.up.railway.app';
  const API_KEY = 'cf79f4cd47506a284b9bd75ff35d24ff00e97dbadff6b9002cea958dc4984ea1';

  async function _handleResponse(res) {
    if (!res.ok) {
      let msg = `Server error (${res.status})`;
      try {
        const j = await res.json();
        if (j.detail) {
          msg = Array.isArray(j.detail)
            ? j.detail.map(e => e.msg || JSON.stringify(e)).join('; ')
            : String(j.detail);
        }
      } catch {}
      throw { message: msg, status: res.status };
    }
    return res;
  }

  async function parseDrawing(file) {
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch(`${BASE}/api/parse/drawing`, {
      method: 'POST',
      headers: { 'X-API-Key': API_KEY },
      body: fd,
    });
    await _handleResponse(res);
    return res.json();
  }

  async function runReview(project, parseResult) {
    const body = { project };
    if (parseResult) body.parse_result = parseResult;
    const res = await fetch(`${BASE}/api/review/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
      body: JSON.stringify(body),
    });
    await _handleResponse(res);
    return res.json();
  }

  async function exportPdf(project, reviewResult, parseResult) {
    const body = { project, review_result: reviewResult };
    if (parseResult) body.parse_result = parseResult;
    const res = await fetch(`${BASE}/api/export/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
      body: JSON.stringify(body),
    });
    await _handleResponse(res);
    return res.blob();
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a   = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  return { parseDrawing, runReview, exportPdf, downloadBlob };
})();
