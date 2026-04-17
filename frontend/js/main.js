// ── Enter key triggers active tab's analyze ──
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  if (document.getElementById('tab-individual').classList.contains('active')) {
    analyzeIndividual();
  } else {
    analyzeMatch();
  }
});
