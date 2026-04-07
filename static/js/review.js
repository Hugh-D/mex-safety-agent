/* MEX Safety Agent — Review page logic */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('steps').innerHTML = renderSteps(2);

  const parseResult  = State.get(State.KEYS.PARSE_RESULT);
  const prevPayload  = State.get(State.KEYS.REVIEW_PAYLOAD);
  const prevReview   = State.get(State.KEYS.REVIEW_RESULT);

  const reviewBtn    = document.getElementById('review-btn');
  const resultPanel  = document.getElementById('result-panel');
  const exportBtn    = document.getElementById('export-btn');
  const tbody        = document.getElementById('eq-tbody');
  const addRowBtn    = document.getElementById('add-row-btn');

  // Pre-populate banner
  if (parseResult) {
    document.getElementById('parse-banner').classList.remove('hidden');
  }

  // Pre-populate equipment from parse result or previous payload
  const equipSource = prevPayload?.equipment || [];
  const parseComps  = parseResult
    ? (parseResult.components || [])
        .filter(c => ['estop','safety_plc','contactor','vfd'].includes(c.type))
        .map(c => ({ manufacturer: c.manufacturer||'', model: c.model||c.label||'', function: c.label||'', pl_rating: c.pl_rating||'' }))
    : [];

  const initialRows = equipSource.length ? equipSource : parseComps;
  initialRows.forEach(d => tbody.appendChild(buildEquipmentRow(d)));
  if (!initialRows.length) tbody.appendChild(buildEquipmentRow());

  // Pre-populate project fields
  if (prevPayload?.project) {
    const p = prevPayload.project;
    document.getElementById('project_number').value = p.project_number || '';
    document.getElementById('client').value         = p.client || '';
    document.getElementById('machine').value        = p.machine || '';
    document.getElementById('target_pl').value      = p.target_pl || 'PLd';
    document.getElementById('target_category').value= p.target_category || '3';
    const stds = (p.standards||[]).join(', ');
    if (stds) document.getElementById('standards').value = stds;
  }

  // Show previous result if present
  if (prevReview) {
    showResult(prevReview);
    exportBtn.classList.remove('hidden');
  }

  addRowBtn.addEventListener('click', () => {
    tbody.appendChild(buildEquipmentRow());
  });

  reviewBtn.addEventListener('click', async () => {
    const projectNumber = document.getElementById('project_number').value.trim();
    const client        = document.getElementById('client').value.trim();
    const machine       = document.getElementById('machine').value.trim();
    const targetPl      = document.getElementById('target_pl').value;
    const targetCat     = document.getElementById('target_category').value;
    const standards     = document.getElementById('standards').value.split(',').map(s=>s.trim()).filter(Boolean);

    if (!projectNumber || !client || !machine) {
      showToast('Please fill in project number, client and machine name.');
      return;
    }

    const equipment = collectEquipment();
    if (!equipment.length) { showToast('Add at least one equipment item.'); return; }

    const project = {
      project_number: projectNumber,
      client, machine,
      target_pl: targetPl,
      target_category: targetCat,
      standards: standards.length ? standards : ['AS4024', 'ISO 13849-1:2015'],
      equipment,
    };

    State.set(State.KEYS.REVIEW_PAYLOAD, { project, equipment });

    reviewBtn.disabled = true;
    reviewBtn.innerHTML = '<div class="spinner"></div> Reviewing…';
    showLoading('loading', 'Running compliance review with Claude… this may take up to 30 seconds');
    resultPanel.classList.add('hidden');

    try {
      const result = await API.runReview(project, parseResult);
      State.set(State.KEYS.REVIEW_RESULT, result);
      showResult(result);
      exportBtn.classList.remove('hidden');
      exportBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      showToast('Review complete', 'success');
    } catch(e) {
      showToast(e.message || 'Review failed');
    } finally {
      reviewBtn.disabled = false;
      reviewBtn.innerHTML = '⟳ Re-run Review';
      hideLoading('loading');
    }
  });

  exportBtn.addEventListener('click', () => { window.location.href = '/export.html'; });

  function showResult(data) {
    const statusCls = { fail:'badge-fail', warn:'badge-warn', pass:'badge-pass' }[data.overall_status] || 'badge-minor';
    const counts = { CRITICAL:0, MAJOR:0, MINOR:0 };
    (data.changes||[]).forEach(c => { counts[(c.priority||'').toUpperCase()]++; });

    resultPanel.innerHTML = `
      <div class="card-header">
        <h2>Review result — J#${escHtml(data.project_number||'')}</h2>
        <span class="badge ${statusCls}">${data.overall_status?.toUpperCase()}</span>
      </div>
      <div class="summary-grid">
        <div class="summary-tile"><div class="label">PL Achievable</div><div class="value" style="color:${data.pl_achievable?'#196F3D':'var(--red)'}">${data.pl_achievable?'Yes':'No'}</div></div>
        <div class="summary-tile"><div class="label">Findings</div><div class="value">${(data.changes||[]).length}</div></div>
        <div class="summary-tile"><div class="label">Critical</div><div class="value" style="color:var(--red)">${counts.CRITICAL}</div></div>
      </div>
      <div class="banner ${data.pl_achievable?'banner-success':'banner-warn'}">${toBullets(data.pl_reasoning||'')}</div>
      <p style="margin:0.75rem 0 0.35rem;font-size:0.8rem;font-weight:600;color:var(--grey-mid);text-transform:uppercase">Summary</p>
      <div style="font-size:0.875rem;color:var(--grey-dark);margin-bottom:1rem">${toBullets(data.summary||'')}</div>
    `;

    ['CRITICAL','MAJOR','MINOR'].forEach(pri => {
      const items = (data.changes||[]).filter(c => (c.priority||'').toUpperCase()===pri);
      if (!items.length) return;
      const hdr = document.createElement('p');
      hdr.style.cssText = 'font-size:0.8rem;font-weight:700;text-transform:uppercase;margin:0.75rem 0 0.35rem';
      hdr.style.color = pri==='CRITICAL'?'var(--red)':pri==='MAJOR'?'var(--amber)':'#2471A3';
      hdr.textContent = `${pri} (${items.length})`;
      resultPanel.appendChild(hdr);
      items.forEach(ch => resultPanel.appendChild(buildFindingCard(ch)));
    });

    if ((data.equipment_notes||[]).length) {
      const hdr = document.createElement('p');
      hdr.style.cssText = 'font-size:0.8rem;font-weight:600;text-transform:uppercase;margin:1rem 0 0.35rem;color:var(--grey-mid)';
      hdr.textContent = 'Equipment notes';
      resultPanel.appendChild(hdr);
      data.equipment_notes.forEach(en => {
        const d = document.createElement('div');
        d.style.cssText = 'display:flex;gap:0.6rem;align-items:flex-start;margin-bottom:0.4rem;font-size:0.85rem';
        d.innerHTML = `<span class="badge badge-${en.status}">${en.status.toUpperCase()}</span><span><strong>${escHtml(en.item)}</strong> — ${escHtml(en.note)}</span>`;
        resultPanel.appendChild(d);
      });
    }

    resultPanel.classList.remove('hidden');
  }
});
