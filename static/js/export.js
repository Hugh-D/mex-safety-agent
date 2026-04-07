/* MEX Safety Agent — Export page logic */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('steps').innerHTML = renderSteps(3);

  const reviewResult = State.get(State.KEYS.REVIEW_RESULT);
  const reviewPayload= State.get(State.KEYS.REVIEW_PAYLOAD);
  const parseResult  = State.get(State.KEYS.PARSE_RESULT);

  // Guard — must have review result
  if (!reviewResult || !reviewPayload) {
    showToast('No review found — please complete a review first.');
    setTimeout(() => window.location.href = '/review.html', 2000);
    return;
  }

  const project    = reviewPayload.project;
  const exportBtn  = document.getElementById('export-btn');
  const newBtn     = document.getElementById('new-btn');
  const includeChk = document.getElementById('include-parse');
  const parseRow   = document.getElementById('parse-row');

  // Show include-parse option only if parse data exists
  if (parseResult) parseRow.classList.remove('hidden');

  // Summary tiles
  const counts = { CRITICAL:0, MAJOR:0, MINOR:0 };
  (reviewResult.changes||[]).forEach(c => { counts[(c.priority||'').toUpperCase()]++; });
  const statusCls = { fail:'badge-fail', warn:'badge-warn', pass:'badge-pass' }[reviewResult.overall_status] || 'badge-minor';

  document.getElementById('summary').innerHTML = `
    <div class="summary-grid">
      <div class="summary-tile"><div class="label">Project</div><div class="value">${escHtml(project.project_number)}</div></div>
      <div class="summary-tile"><div class="label">Machine</div><div class="value" style="font-size:0.9rem">${escHtml(project.machine)}</div></div>
      <div class="summary-tile"><div class="label">Status</div><div class="value"><span class="badge ${statusCls}">${(reviewResult.overall_status||'').toUpperCase()}</span></div></div>
    </div>
    <div class="summary-grid" style="margin-top:0">
      <div class="summary-tile"><div class="label">Target</div><div class="value">${escHtml(project.target_pl)} / Cat ${escHtml(project.target_category)}</div></div>
      <div class="summary-tile"><div class="label">Critical findings</div><div class="value" style="color:var(--red)">${counts.CRITICAL}</div></div>
      <div class="summary-tile"><div class="label">Total findings</div><div class="value">${(reviewResult.changes||[]).length}</div></div>
    </div>
    <div class="banner ${reviewResult.pl_achievable?'banner-success':'banner-warn'}" style="margin-top:0.75rem">
      ${toBullets(reviewResult.summary||'')}
    </div>
  `;

  exportBtn.addEventListener('click', async () => {
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<div class="spinner"></div> Generating PDF…';
    showLoading('loading', 'Generating PDF report… this may take up to 30 seconds');

    const includeParse = includeChk && includeChk.checked && parseResult ? parseResult : null;

    try {
      const blob = await API.exportPdf(project, reviewResult, includeParse);
      const filename = `${project.project_number}_Compliance_Review.pdf`;
      API.downloadBlob(blob, filename);
      exportBtn.innerHTML = '✓ Download Again';
      exportBtn.disabled = false;
      showToast('PDF downloaded successfully', 'success');
    } catch(e) {
      showToast(e.message || 'Export failed');
      exportBtn.disabled = false;
      exportBtn.innerHTML = 'Download PDF Report';
    } finally {
      hideLoading('loading');
    }
  });

  newBtn.addEventListener('click', () => {
    State.clear();
    window.location.href = '/';
  });
});
