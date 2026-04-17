// ── Shared chart style constants ──
const CHART_TICK  = '#4e5f78';
const CHART_GRID  = 'rgba(255,255,255,0.05)';
const CHART_FONT  = { family: 'DM Sans', size: 11 };

function chartBase() {
  return {
    plugins: {
      legend: { labels: { color: CHART_TICK, font: CHART_FONT } },
    },
    scales: {
      x: { ticks: { color: CHART_TICK, font: CHART_FONT }, grid: { color: CHART_GRID } },
      y: { ticks: { color: CHART_TICK, font: CHART_FONT }, grid: { color: CHART_GRID } },
    },
  };
}

// ── Radar chart builder ──
function buildRadar(canvasId, datasets, labels, existingChart) {
  if (existingChart) existingChart.destroy();
  return new Chart(document.getElementById(canvasId).getContext('2d'), {
    type: 'radar',
    data: {
      labels: ['KDA', 'CS/min', 'Vision', 'Damage', 'Wards'],
      datasets: datasets.map((d, i) => ({
        label: labels[i],
        data: d,
        borderColor:     ['#c89b3c', '#0bc4e3'][i],
        backgroundColor: ['#c89b3c22', '#0bc4e322'][i],
        borderWidth: 2,
        pointRadius: 3,
      })),
    },
    options: {
      plugins: { legend: { labels: { color: CHART_TICK, font: CHART_FONT } } },
      scales: {
        r: {
          grid:        { color: CHART_GRID },
          ticks:       { color: CHART_TICK, backdropColor: 'transparent', font: { size: 9 } },
          pointLabels: { color: CHART_TICK, font: { size: 10 } },
          suggestedMin: 0, suggestedMax: 10,
        },
      },
    },
  });
}

// ── Normalise raw stats into 0-10 radar values ──
function radarVals(s) {
  return [
    Math.min(s.kda / 10, 1) * 10,
    Math.min(s.cs_per_min / 10, 1) * 10,
    Math.min(s.vision_score / 40, 1) * 10,
    Math.min(s.damage_dealt / 30000, 1) * 10,
    Math.min(s.wards_placed / 20, 1) * 10,
  ];
}
