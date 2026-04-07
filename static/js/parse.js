/* MEX Safety Agent — Parse page logic */
document.addEventListener('DOMContentLoaded', () => {
  const dropzone   = document.getElementById('dropzone');
  const fileInput  = document.getElementById('file-input');
  const uploadBtn  = document.getElementById('upload-btn');
  const skipBtn    = document.getElementById('skip-btn');
  const continueBtn= document.getElementById('continue-btn');
  const resultPanel= document.getElementById('result-panel');
  const loadingEl  = document.getElementById('loading');

  let selectedFile = null;

  // Render steps
  document.getElementById('steps').innerHTML = renderSteps(1);

  // Show existing parse result if present
  const existing = State.get(State.KEYS.PARSE_RESULT);
  if (existing) showResult(existing, false);

  // Dropzone interactions
  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('drag-over'); });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
  dropzone.addEventListener('drop', e => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  });
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) setFile(fileInput.files[0]); });

  function setFile(f) {
    if (!f.name.toLowerCase().endsWith('.pdf')) { showToast('Only PDF files are supported.'); return; }
    selectedFile = f;
    dropzone.classList.add('has-file');
    dropzone.querySelector('.dropzone-file').textContent = `📄 ${f.name}  (${(f.size/1024/1024).toFixed(1)} MB)`;
    uploadBtn.disabled = false;
  }

  uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<div class="spinner"></div> Parsing…';
    showLoading('loading', 'Analysing drawing with Claude… this may take up to 30 seconds');

    try {
      const result = await API.parseDrawing(selectedFile);
      State.set(State.KEYS.PARSE_RESULT, result);
      showResult(result, true);
      continueBtn.disabled = false;
      showToast('Drawing parsed successfully', 'success');
    } catch(e) {
      showToast(e.message || 'Parse failed');
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.innerHTML = '⟳ Re-parse';
      hideLoading('loading');
    }
  });

  skipBtn.addEventListener('click', () => {
    State.remove(State.KEYS.PARSE_RESULT);
    window.location.href = '/review.html';
  });

  continueBtn.addEventListener('click', () => { window.location.href = '/review.html'; });

  function showResult(data, animate) {
    const safety = (data.components || []).filter(c =>
      ['estop','safety_plc','contactor'].includes(c.type));
    const other  = (data.components || []).filter(c =>
      !['estop','safety_plc','contactor'].includes(c.type));

    resultPanel.innerHTML = `
      <div class="card-header">
        <h2>Parsed drawing — ${escHtml(data.drawing_type||'')} · ${data.page_count||'?'} pages</h2>
        <span class="badge badge-info">${(data.components||[]).length} components</span>
      </div>
      <div class="banner banner-success">${toBullets(data.summary||'')}</div>
      ${(data.safety_concerns||[]).length ? `
        <div class="banner banner-warn">
          <strong>⚠ Safety concerns:</strong>
          <ul style="margin:0.4rem 0 0 1rem;padding:0;list-style:disc">
            ${data.safety_concerns.map(s => `<li style="margin-bottom:0.2rem">${escHtml(s)}</li>`).join('')}
          </ul>
        </div>` : ''}
      <table class="preview-table">
        <thead><tr><th>ID</th><th>Label</th><th>Type</th><th>Manufacturer / Model</th><th>Location</th></tr></thead>
        <tbody>${(data.components||[]).map(c => `
          <tr>
            <td><strong>${escHtml(c.id||'')}</strong></td>
            <td>${escHtml(c.label||'')}</td>
            <td><span class="badge badge-${c.type==='estop'?'critical':c.type==='safety_plc'?'warn':'minor'}">${escHtml(c.type||'')}</span></td>
            <td>${escHtml([c.manufacturer,c.model].filter(Boolean).join(' ') || '—')}</td>
            <td class="text-sm text-mid">${escHtml(c.location||'—')}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
    resultPanel.classList.remove('hidden');
    continueBtn.disabled = false;
    if (animate) resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
