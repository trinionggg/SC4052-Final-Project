let indRadarChart;

async function analyzeIndividual() {
  const name   = document.getElementById('ind-name').value.trim();
  const tag    = document.getElementById('ind-tag').value.trim();
  const region = document.getElementById('ind-region').value;
  const { riotK, oaiK } = getKeys();

  if (!name || !tag)   return alert('Enter summoner name and tag.');
  if (!riotK || !oaiK) return alert('Enter both API keys above.');

  hideError('ind-error');
  document.getElementById('ind-result').classList.add('hidden');
  document.getElementById('ind-loader').classList.add('active');

  try {
    const res = await fetch(`${API_BASE}/analyze/individual`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Riot-Key':   riotK,
        'X-OpenAI-Key': oaiK,
      },
      body: JSON.stringify({ summoner: name, tag, region }),
    });

    if (!res.ok) {
      const e = await res.json();
      throw new Error(e.detail || res.statusText);
    }

    const { data: d } = await res.json();

    renderIndividualHeader(d);
    renderIndividualStats(d);
    document.getElementById('ind-report').innerHTML = formatReport(d.coaching_report);
    indRadarChart = buildRadar('ind-radar', [radarVals(d)], [d.champion], indRadarChart);

    document.getElementById('ind-result').classList.remove('hidden');
  } catch (e) {
    showError('ind-error', e.message);
  } finally {
    document.getElementById('ind-loader').classList.remove('active');
  }
}

function renderIndividualHeader(d) {
  document.getElementById('ind-header').innerHTML = `
    <div class="champ-block">
      <div class="champ-name">${d.champion}</div>
      <div class="champ-meta">${d.role} &nbsp;·&nbsp; ${d.duration} min &nbsp;·&nbsp; ${d.match_id}</div>
    </div>
    <div class="result-header-right">
      <span class="pill ${d.win ? 'pill-win' : 'pill-loss'}">${d.win ? 'Victory' : 'Defeat'}</span>
      <div class="grade-badge grade-${d.grade}">${d.grade}</div>
    </div>
  `;
}

function renderIndividualStats(d) {
  const stats = [
    [`${d.kills}/${d.deaths}/${d.assists}`, 'KDA'],
    [d.kda,                                 'Ratio'],
    [d.cs_per_min,                          'CS/min'],
    [d.vision_score,                        'Vision'],
    [`${Math.round(d.damage_dealt / 1000)}k`, 'Damage'],
    [d.wards_placed,                        'Wards'],
  ];
  document.getElementById('ind-stats').innerHTML = stats
    .map(([v, l]) => `
      <div class="stat-box">
        <div class="stat-val">${v}</div>
        <div class="stat-lbl">${l}</div>
      </div>`)
    .join('');
}
