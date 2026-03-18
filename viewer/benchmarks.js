async function loadScenarios() {
  const res = await fetch('/viewer/scenarios.json');
  if (!res.ok) throw new Error(`Failed to load scenarios: ${res.status}`);
  return res.json();
}

function renderScenarioCard(s) {
  const reports = (s.reports || []).map(r => `<li><code>${r}</code></li>`).join('');
  const reproduce = (s.reproduce || []).join('\n');
  return `
    <article class="scenario-card">
      <h3>${s.name}</h3>
      <p>${s.summary}</p>
      <dl class="kv-list">
        <dt>Status</dt><dd class="status-good">${s.status}</dd>
        <dt>Workers</dt><dd>${s.workers}</dd>
        <dt>Events</dt><dd>${s.events}</dd>
        <dt>Divergence index</dt><dd>${s.divergence_index}</dd>
        <dt>Invariant status</dt><dd>${s.invariant_status}</dd>
      </dl>
      <h4>Reports</h4>
      <ul>${reports}</ul>
      <h4>Reproduce</h4>
      <pre>${reproduce}</pre>
    </article>
  `;
}

(async function init() {
  const grid = document.getElementById('scenarioGrid');
  try {
    const scenarios = await loadScenarios();
    grid.innerHTML = scenarios.map(renderScenarioCard).join('');
  } catch (err) {
    grid.innerHTML = `<article class="scenario-card"><h3>Failed to load scenarios</h3><p>${err.message}</p></article>`;
  }
})();
