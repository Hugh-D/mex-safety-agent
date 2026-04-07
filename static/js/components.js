/* MEX Safety Agent — Shared UI components */

/* ── Toast ── */
function showToast(msg, type = 'error', duration = 6000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity 0.3s'; setTimeout(() => t.remove(), 300); }, duration);
}

/* ── Loading bar ── */
function showLoading(containerId, msg = 'Processing… this may take up to 30 seconds') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="loading-bar"><div class="spinner spinner-dark"></div><span>${msg}</span></div>`;
  el.classList.remove('hidden');
}

function hideLoading(containerId) {
  const el = document.getElementById(containerId);
  if (el) { el.innerHTML = ''; el.classList.add('hidden'); }
}

/* ── Equipment row ── */
let _eqRowId = 0;

function buildEquipmentRow(data = {}) {
  const id = ++_eqRowId;
  const tr = document.createElement('tr');
  tr.dataset.rowId = id;
  const plOptions = ['', 'PLa', 'PLb', 'PLc', 'PLd', 'PLe'].map(v =>
    `<option value="${v}" ${data.pl_rating === v ? 'selected' : ''}>${v || '—'}</option>`
  ).join('');
  tr.innerHTML = `
    <td><input type="text" placeholder="e.g. SICK" value="${data.manufacturer||''}" data-field="manufacturer"></td>
    <td><input type="text" placeholder="e.g. deTec4" value="${data.model||''}" data-field="model"></td>
    <td><input type="text" placeholder="e.g. Light curtain" value="${data.function||''}" data-field="function"></td>
    <td><select data-field="pl_rating">${plOptions}</select></td>
    <td><input type="number" min="1" value="${data.qty||1}" data-field="qty" style="width:60px"></td>
    <td><button class="btn btn-danger" onclick="removeEquipmentRow(this)">✕</button></td>
  `;
  return tr;
}

function removeEquipmentRow(btn) {
  btn.closest('tr').remove();
}

function collectEquipment() {
  const rows = document.querySelectorAll('#eq-tbody tr');
  const items = [];
  rows.forEach(tr => {
    const get = f => tr.querySelector(`[data-field="${f}"]`).value.trim();
    const manufacturer = get('manufacturer');
    const model        = get('model');
    if (!manufacturer && !model) return;
    const item = { manufacturer: manufacturer || '(unknown)', model: model || '(unknown)', qty: parseInt(get('qty')) || 1 };
    const fn  = get('function');  if (fn)  item.function  = fn;
    const pl  = get('pl_rating'); if (pl)  item.pl_rating = pl;
    items.push(item);
  });
  return items;
}

/* ── Finding card ── */
function buildFindingCard(ch) {
  const pri = (ch.priority || '').toUpperCase();
  const div = document.createElement('div');
  div.className = `finding-card finding-${pri}`;
  div.innerHTML = `
    <div class="finding-header">
      <div class="finding-num">${ch.id}</div>
      <strong>${pri}</strong>
      <span style="flex:1;font-size:0.85rem;margin-left:0.25rem">${toBullets(ch.description||'')}</span>
    </div>
    <div class="finding-body">
      <div class="finding-ref">📋 ${escHtml(ch.reference||'')}</div>
    </div>
    <div class="finding-action">→ ${escHtml(ch.action||'')}</div>
  `;
  return div;
}

/* ── Step progress ── */
function renderSteps(current) {
  const steps = [
    { n:1, label:'Parse Drawing', href:'/' },
    { n:2, label:'Review',        href:'/review.html' },
    { n:3, label:'Export PDF',    href:'/export.html' },
  ];
  return steps.map((s, i) => {
    const cls = s.n === current ? 'active' : s.n < current ? 'done' : '';
    const sep = i < steps.length-1 ? '<span class="step-sep">›</span>' : '';
    return `<div class="step ${cls}"><div class="step-num">${s.n < current ? '✓' : s.n}</div>${s.label}</div>${sep}`;
  }).join('');
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/**
 * Render a value as a bullet list. Accepts:
 *   - an array of strings (new format from API)
 *   - a plain string (fallback — split on newlines or ' · ')
 * Single-item input renders as plain text, not a list.
 */
function toBullets(val) {
  if (!val) return '';
  const parts = Array.isArray(val)
    ? val.map(s => String(s).trim()).filter(Boolean)
    : String(val).split(/\n| · /).map(s => s.trim()).filter(Boolean);
  if (parts.length <= 1) return escHtml(parts[0] || String(val));
  return '<ul style="margin:0.3rem 0 0 1.1rem;padding:0;list-style:disc">' +
    parts.map(p => `<li style="margin-bottom:0.3rem">${escHtml(p)}</li>`).join('') +
    '</ul>';
}
