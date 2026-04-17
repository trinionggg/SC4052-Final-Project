// ── API base URL — change for production ──
const API_BASE = "http://localhost:8000";

// ── Grade colours ──
const GRADE_COLORS = {
  S: '#ff9900',
  A: '#4caf50',
  B: '#0bc4e3',
  C: '#ff9800',
  D: '#e84057',
};

function gradeColor(g) {
  return GRADE_COLORS[g] || '#888';
}

// ── Keys helper ──
function getKeys() {
  return {
    riotK: document.getElementById('riot-key').value.trim(),
    oaiK:  document.getElementById('openai-key').value.trim(),
  };
}

// ── Error helpers ──
function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = 'Error: ' + msg;
  el.style.display = 'block';
}

function hideError(id) {
  document.getElementById(id).style.display = 'none';
}

// ── Markdown-lite formatter ──
function formatReport(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/#{1,3} (.*)/g, '<span class="section-heading">$1</span>');
}

// ── Tab switcher ──
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach((b, i) =>
    b.classList.toggle('active', ['individual', 'match'][i] === name)
  );
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
}
