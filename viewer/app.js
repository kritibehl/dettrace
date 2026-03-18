const els = {
  expectedPath: document.getElementById('expectedPath'),
  actualPath: document.getElementById('actualPath'),
  loadBtn: document.getElementById('loadBtn'),
  taskFilter: document.getElementById('taskFilter'),
  workerFilter: document.getElementById('workerFilter'),
  applyFiltersBtn: document.getElementById('applyFiltersBtn'),
  clearFiltersBtn: document.getElementById('clearFiltersBtn'),
  expectedTableBody: document.getElementById('expectedTableBody'),
  actualTableBody: document.getElementById('actualTableBody'),
  expectedMeta: document.getElementById('expectedMeta'),
  actualMeta: document.getElementById('actualMeta'),
  changeSummary: document.getElementById('changeSummary'),
  rootCauseHints: document.getElementById('rootCauseHints'),
  invariantExplorer: document.getElementById('invariantExplorer'),
  beforeAfter: document.getElementById('beforeAfter'),
};

const state = {
  expected: [],
  actual: [],
  firstDivergence: null,
  divergenceReport: null,
  swiftReport: null,
};

async function fetchText(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return res.text();
}

async function fetchJsonMaybe(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

function parseJSONL(text) {
  return text.trim().split(/\n+/).filter(Boolean).map(line => JSON.parse(line));
}

function rowMatchesFilter(row, taskFilter, workerFilter) {
  const taskOk = taskFilter === null || row.task === taskFilter;
  const workerOk = workerFilter === null || row.worker === workerFilter;
  return taskOk && workerOk;
}

function firstDivergence(expected, actual) {
  const n = Math.min(expected.length, actual.length);
  for (let i = 0; i < n; i++) {
    const a = expected[i];
    const b = actual[i];
    if (
      a.seq !== b.seq ||
      a.type !== b.type ||
      a.task !== b.task ||
      a.worker !== b.worker ||
      a.queue !== b.queue
    ) return i;
  }
  if (expected.length !== actual.length) return n;
  return null;
}

function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

function renderTableRows(rows, otherRows, divergenceIndex, tbody, taskFilter, workerFilter) {
  tbody.innerHTML = '';
  rows.forEach((row, idx) => {
    const tr = document.createElement('tr');
    const isMismatch = divergenceIndex !== null && idx === divergenceIndex;
    const isContext = divergenceIndex !== null && Math.abs(idx - divergenceIndex) <= 2 && idx !== divergenceIndex;
    const hidden = !rowMatchesFilter(row, taskFilter, workerFilter);
    if (isMismatch) tr.classList.add('mismatch');
    else if (isContext) tr.classList.add('context');
    if (hidden) tr.classList.add('hidden-row');
    tr.innerHTML = `
      <td>${row.seq}</td>
      <td>${escapeHtml(row.type)}</td>
      <td>${row.task}</td>
      <td>${row.worker === null ? 'null' : row.worker}</td>
      <td>${row.queue === null ? 'null' : row.queue}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderSummary() {
  const idx = state.firstDivergence;
  const report = state.divergenceReport || state.swiftReport;
  if (idx === null) {
    els.changeSummary.innerHTML = `
      <p><strong>No divergence detected.</strong></p>
      <p>The two executions currently match exactly.</p>
    `;
    return;
  }
  const expected = report?.expected || state.expected[idx];
  const actual = report?.actual || state.actual[idx];
  els.changeSummary.innerHTML = `
    <dl class="kv-list">
      <dt>First divergence</dt><dd><strong>${idx}</strong></dd>
      <dt>Expected</dt><dd><code>${expected.type} task=${expected.task} worker=${expected.worker ?? 'null'} queue=${expected.queue ?? 'null'}</code></dd>
      <dt>Actual</dt><dd><code>${actual.type} task=${actual.task} worker=${actual.worker ?? 'null'} queue=${actual.queue ?? 'null'}</code></dd>
      <dt>Interpretation</dt><dd>Passing and failing executions split at the first mismatched event, which changes downstream behavior.</dd>
    </dl>
  `;
}

function buildHints() {
  const hints = [];
  const idx = state.firstDivergence;
  if (idx === null) {
    hints.push('No mismatch detected between the compared traces.');
    return hints;
  }
  const expected = (state.divergenceReport || state.swiftReport)?.expected || state.expected[idx];
  const actual = (state.divergenceReport || state.swiftReport)?.actual || state.actual[idx];

  if (expected?.type === 'TASK_DEQUEUED' && actual?.type === 'TASK_DEQUEUED') {
    hints.push(`Ordering divergence began at dequeue: expected task ${expected.task}, observed task ${actual.task}.`);
  }
  if (expected?.task !== actual?.task) {
    hints.push('Task identity changed at the divergence point, which likely shifted downstream scheduling order.');
  }
  if (state.expected.length !== state.actual.length) {
    hints.push(`Trace lengths differ (${state.expected.length} vs ${state.actual.length}), indicating early termination or truncated execution.`);
  } else {
    hints.push('Trace lengths match, so the primary issue is event ordering rather than missing terminal data.');
  }
  hints.push('Compare 2–3 events before and after the split to see whether a scheduler decision or queue ordering changed first.');
  return hints;
}

function renderHints() {
  els.rootCauseHints.innerHTML = buildHints()
    .map(h => `<li>${escapeHtml(h)}</li>`)
    .join('');
}

function renderInvariantExplorer() {
  const report = state.divergenceReport || state.swiftReport;
  const invariantFailures = report?.invariant_failures || [];
  if (invariantFailures.length === 0) {
    els.invariantExplorer.innerHTML = `
      <p class="status-good"><strong>No invariant failures reported.</strong></p>
      <p>The expected/reference path validates, so the current known issue is execution divergence rather than an explicit invariant violation report.</p>
    `;
    return;
  }
  els.invariantExplorer.innerHTML = invariantFailures.map((failure, i) => `
    <div class="card" style="padding:0.75rem; margin-bottom:0.5rem;">
      <strong>Invariant ${i + 1}</strong>
      <pre>${escapeHtml(JSON.stringify(failure, null, 2))}</pre>
    </div>
  `).join('');
}

function renderBeforeAfter() {
  const idx = state.firstDivergence;
  if (idx === null) {
    els.beforeAfter.innerHTML = '<p>No divergence to inspect.</p>';
    return;
  }
  const start = Math.max(0, idx - 2);
  const end = Math.min(Math.max(state.expected.length, state.actual.length), idx + 3);
  const lines = [];
  for (let i = start; i < end; i++) {
    const e = state.expected[i];
    const a = state.actual[i];
    lines.push(`
      <div class="scenario-card">
        <h3>Event ${i}${i === idx ? ' <span class="status-danger">(first divergence)</span>' : ''}</h3>
        <div class="kv-list">
          <dt>Expected</dt><dd>${e ? `<code>${e.type} task=${e.task} worker=${e.worker ?? 'null'} queue=${e.queue ?? 'null'}</code>` : '<em>missing</em>'}</dd>
          <dt>Actual</dt><dd>${a ? `<code>${a.type} task=${a.task} worker=${a.worker ?? 'null'} queue=${a.queue ?? 'null'}</code>` : '<em>missing</em>'}</dd>
        </div>
      </div>
    `);
  }
  els.beforeAfter.innerHTML = lines.join('');
}

function renderAll() {
  const taskFilter = els.taskFilter.value === '' ? null : Number(els.taskFilter.value);
  const workerFilter = els.workerFilter.value === '' ? null : Number(els.workerFilter.value);

  renderTableRows(state.expected, state.actual, state.firstDivergence, els.expectedTableBody, taskFilter, workerFilter);
  renderTableRows(state.actual, state.expected, state.firstDivergence, els.actualTableBody, taskFilter, workerFilter);
  els.expectedMeta.textContent = `${state.expected.length} events`;
  els.actualMeta.textContent = `${state.actual.length} events`;
  renderSummary();
  renderHints();
  renderInvariantExplorer();
  renderBeforeAfter();
}

async function loadDiagnostics() {
  els.changeSummary.textContent = 'Loading traces...';
  const [expectedText, actualText, divergenceReport, swiftReport] = await Promise.all([
    fetchText(els.expectedPath.value),
    fetchText(els.actualPath.value),
    fetchJsonMaybe('/reports/divergence_report.json'),
    fetchJsonMaybe('/reports/divergence_report_swift.json'),
  ]);
  state.expected = parseJSONL(expectedText);
  state.actual = parseJSONL(actualText);
  state.divergenceReport = divergenceReport;
  state.swiftReport = swiftReport;
  state.firstDivergence = firstDivergence(state.expected, state.actual);
  renderAll();
}

els.loadBtn.addEventListener('click', () => {
  loadDiagnostics().catch(err => {
    els.changeSummary.innerHTML = `<p class="status-danger"><strong>Failed to load diagnostics:</strong> ${escapeHtml(err.message)}</p>`;
  });
});
els.applyFiltersBtn.addEventListener('click', renderAll);
els.clearFiltersBtn.addEventListener('click', () => {
  els.taskFilter.value = '';
  els.workerFilter.value = '';
  renderAll();
});

loadDiagnostics().catch(err => {
  els.changeSummary.innerHTML = `<p class="status-danger"><strong>Failed to load diagnostics:</strong> ${escapeHtml(err.message)}</p>`;
});
