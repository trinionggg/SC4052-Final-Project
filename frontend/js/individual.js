// let indRadarChart;

// async function analyzeIndividual() {
//   console.log("analyzeIndividual called");
//   const name   = document.getElementById('ind-name').value.trim();
//   const tag    = document.getElementById('ind-tag').value.trim();
//   const region = document.getElementById('ind-region').value;
//   const { riotK, oaiK } = getKeys();

//   if (!name || !tag)   return alert('Enter summoner name and tag.');
//   if (!riotK || !oaiK) return alert('Enter both API keys above.');

//   hideError('ind-error');
//   document.getElementById('ind-result').classList.add('hidden');
//   document.getElementById('ind-loader').classList.add('active');

//   try {
//     const res = await fetch(`${API_BASE}/analyze/individual`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'X-Riot-Key':   riotK,
//         'X-OpenAI-Key': oaiK,
//       },
//       body: JSON.stringify({ summoner: name, tag, region }),
//     });
//     console.log("API response received", res)
//     if (!res.ok) {
//       const e = await res.json();
//       throw new Error(e.detail || res.statusText);
//     }

//     const { data: d } = await res.json();

//     renderIndividualHeader(d);
//     renderIndividualStats(d);
//     document.getElementById('ind-report').innerHTML = formatReport(d.coaching_report);
//     indRadarChart = buildRadar('ind-radar', [radarVals(d)], [d.champion], indRadarChart);

//     document.getElementById('ind-result').classList.remove('hidden');
//   } catch (e) {
//     showError('ind-error', e.message);
//   } finally {
//     document.getElementById('ind-loader').classList.remove('active');
//   }
// }

// function renderIndividualHeader(d) {
//   document.getElementById('ind-header').innerHTML = `
//     <div class="champ-block">
//       <div class="champ-name">${d.champion}</div>
//       <div class="champ-meta">${d.role} &nbsp;·&nbsp; ${d.duration} min &nbsp;·&nbsp; ${d.match_id}</div>
//     </div>
//     <div class="result-header-right">
//       <span class="pill ${d.win ? 'pill-win' : 'pill-loss'}">${d.win ? 'Victory' : 'Defeat'}</span>
//       <div class="grade-badge grade-${d.grade}">${d.grade}</div>
//     </div>
//   `;
// }

// function renderIndividualStats(d) {
//   const stats = [
//     [`${d.kills}/${d.deaths}/${d.assists}`, 'KDA'],
//     [d.kda,                                 'Ratio'],
//     [d.cs_per_min,                          'CS/min'],
//     [d.vision_score,                        'Vision'],
//     [`${Math.round(d.damage_dealt / 1000)}k`, 'Damage'],
//     [d.wards_placed,                        'Wards'],
//   ];
//   document.getElementById('ind-stats').innerHTML = stats
//     .map(([v, l]) => `
//       <div class="stat-box">
//         <div class="stat-val">${v}</div>
//         <div class="stat-lbl">${l}</div>
//       </div>`)
//     .join('');
// }

let indRadarChart;

async function analyzeIndividual() {
  console.log("analyzeIndividual called");
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
    console.log("Data received:", d);

    renderIndividualHeader(d);
    renderIndividualStats(d);
    renderCoachingReport(d);
    renderModelInsights(d);
    indRadarChart = buildRadar('ind-radar', [radarVals(d)], [d.champion], indRadarChart);

    document.getElementById('ind-result').classList.remove('hidden');
  } catch (e) {
    console.error("Error:", e);
    showError('ind-error', e.message);
  } finally {
    document.getElementById('ind-loader').classList.remove('active');
  }
}

// ── Header: champion, role, result, grade ──
function renderIndividualHeader(d) {
  document.getElementById('ind-header').innerHTML = `
    <div class="champ-block">
      <div class="champ-name">${d.champion}</div>
      <div class="champ-meta">${d.role} &nbsp;·&nbsp; ${d.duration} min &nbsp;·&nbsp; ${d.match_id ?? ''}</div>
    </div>
    <div class="result-header-right">
      <span class="pill ${d.win ? 'pill-win' : 'pill-loss'}">${d.win ? 'Victory' : 'Defeat'}</span>
      <div class="grade-badge grade-${d.grade}">${d.grade}</div>
    </div>
  `;
}

// ── Stat boxes ──
function renderIndividualStats(d) {
  const stats = [
    [`${d.kills}/${d.deaths}/${d.assists}`, 'KDA'],
    [d.kda,                                  'Ratio'],
    [d.cs_per_min,                           'CS/min'],
    [d.vision_score,                         'Vision'],
    [`${Math.round(d.damage_dealt / 1000)}k`, 'Damage'],
    [d.wards_placed,                         'Wards'],
    [`${Math.round(d.win_probability * 100)}%`, 'Win Prob'],
  ];
  document.getElementById('ind-stats').innerHTML = stats
    .map(([v, l]) => `
      <div class="stat-box">
        <div class="stat-val">${v}</div>
        <div class="stat-lbl">${l}</div>
      </div>`)
    .join('');
}

// ── Coaching report ──
function renderCoachingReport(d) {
  const r = d.coaching_report;
  console.log("Coaching report:", r);
  console.log("r.summary:", r.summary);

  // fallback if report is a plain string
  if (typeof r === 'string') {
    document.getElementById('ind-report').innerHTML = `<p class="report-summary">${r}</p>`;
    return;
  }

  document.getElementById('ind-report').innerHTML = `
    <p class="report-summary">${r.summary}</p>

    <div class="report-section">
      <div class="report-section-title">💪 Strengths</div>
      ${r.strengths.map(s => `
        <div class="report-item report-item-positive">
          <div class="report-item-stat">${s.stat}</div>
          <div class="report-item-text">${s.observation}</div>
        </div>`).join('')}
    </div>

    <div class="report-section">
      <div class="report-section-title">📈 Areas to Improve</div>
      ${r.improvements.map(i => `
        <div class="report-item report-item-negative">
          <div class="report-item-stat">${i.area}</div>
          <div class="report-item-text">${i.advice}</div>
        </div>`).join('')}
    </div>

    <div class="report-section">
      <div class="report-section-title">🎯 Drill for Next Game</div>
      <div class="report-drill">${r.drill}</div>
    </div>
  `;
}

// ── Model insights: win probability bar + SHAP ──
function renderModelInsights(d) {
  const el = document.getElementById('ind-insights');
  if (!el) return;

  const pct = Math.round(d.win_probability * 100);

  el.innerHTML = `
    <div class="insight-label-row">
      <span class="insight-assessment">${d.performance_label}</span>
    </div>

    <div class="insight-row">
      <div class="insight-label">Win Probability</div>
      <div class="insight-bar-wrap">
        <div class="insight-bar" style="width:${pct}%"></div>
      </div>
      <div class="insight-val">${pct}%</div>
    </div>

    <div class="shap-row">
      <div class="shap-col">
        <div class="shap-title">✅ What helped</div>
        ${(d.top_positive || []).map(p => `
          <div class="shap-item shap-positive">
            <span>${p.feature}</span>
            <span>+${p.impact}</span>
          </div>`).join('')}
      </div>
      <div class="shap-col">
        <div class="shap-title">❌ What hurt</div>
        ${(d.top_negative || []).map(p => `
          <div class="shap-item shap-negative">
            <span>${p.feature}</span>
            <span>${p.impact}</span>
          </div>`).join('')}
      </div>
    </div>
  `;
}