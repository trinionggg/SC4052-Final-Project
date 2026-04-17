let dmgChart, csChart, visionChart, mvpChart, goldChart;

async function analyzeMatch() {
  const name   = document.getElementById('match-name').value.trim();
  const tag    = document.getElementById('match-tag').value.trim();
  const region = document.getElementById('match-region').value;
  const { riotK, oaiK } = getKeys();

  if (!name || !tag)   return alert('Enter summoner name and tag.');
  if (!riotK || !oaiK) return alert('Enter both API keys above.');

  hideError('match-error');
  document.getElementById('match-result').classList.add('hidden');
  document.getElementById('match-loader').classList.add('active');

  try {
    const res = await fetch(`${API_BASE}/analyze/match`, {
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

    const data = await res.json();

    renderMatchMeta(data);
    renderScoreboard(data);
    renderMatchCharts(data);
    renderAIReports(data);

    document.getElementById('match-result').classList.remove('hidden');
  } catch (e) {
    showError('match-error', e.message);
  } finally {
    document.getElementById('match-loader').classList.remove('active');
  }
}

function renderMatchMeta(data) {
  document.getElementById('match-meta').textContent =
    `Match ${data.match_id} · ${data.duration} min · ${data.blue_won ? 'Blue' : 'Red'} team won`;
}

function renderScoreboard(data) {
  function teamHTML(team, label, cls, won) {
    return `
      <div class="team-col">
        <div class="team-header">
          <span class="team-name ${cls}">${label}</span>
          <span class="pill ${won ? 'pill-win' : 'pill-loss'}">${won ? 'Victory' : 'Defeat'}</span>
        </div>
        ${team.map(p => `
          <div class="player-row">
            <div>
              <div class="player-champ">${p.champion}</div>
              <div class="player-role">${p.role}</div>
            </div>
            <div>
              <div class="player-kda">${p.kills}/${p.deaths}/${p.assists}</div>
              <div class="player-sub">${p.cs_per_min} cs/m &nbsp;·&nbsp; ${p.vision_score} vis</div>
            </div>
            <div class="player-grade" style="color:${gradeColor(p.grade)}">${p.grade}</div>
          </div>`).join('')}
      </div>`;
  }

  document.getElementById('scoreboard').innerHTML =
    teamHTML(data.blue_team, 'Blue Team', 'team-blue', data.blue_won) +
    teamHTML(data.red_team,  'Red Team',  'team-red',  !data.blue_won);
}

function renderMatchCharts(data) {
  // Damage bar
  const all = [...data.blue_team, ...data.red_team].sort((a, b) => b.damage_dealt - a.damage_dealt);
  if (dmgChart) dmgChart.destroy();
  dmgChart = new Chart(document.getElementById('damage-chart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: all.map(p => `${p.champion} (${p.role})`),
      datasets: [{
        data:            all.map(p => p.damage_dealt),
        backgroundColor: all.map(p => p.team_id === 100 ? '#0bc4e333' : '#e8405733'),
        borderColor:     all.map(p => p.team_id === 100 ? '#0bc4e3'   : '#e84057'),
        borderWidth: 1, borderRadius: 4,
      }],
    },
    options: { ...chartBase(), indexAxis: 'y', plugins: { legend: { display: false } } },
  });

  // CS per role
  if (csChart) csChart.destroy();
  csChart = new Chart(document.getElementById('cs-chart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.blue_team.map(p => p.role),
      datasets: [
        { label: 'Blue', data: data.blue_team.map(p => p.cs_per_min), backgroundColor: '#0bc4e333', borderColor: '#0bc4e3', borderWidth: 1, borderRadius: 4 },
        { label: 'Red',  data: data.red_team.map(p => p.cs_per_min),  backgroundColor: '#e8405733', borderColor: '#e84057', borderWidth: 1, borderRadius: 4 },
      ],
    },
    options: chartBase(),
  });

  // Vision per role
  if (visionChart) visionChart.destroy();
  visionChart = new Chart(document.getElementById('vision-chart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: data.blue_team.map(p => p.role),
      datasets: [
        { label: 'Blue', data: data.blue_team.map(p => p.vision_score), backgroundColor: '#0bc4e333', borderColor: '#0bc4e3', borderWidth: 1, borderRadius: 4 },
        { label: 'Red',  data: data.red_team.map(p => p.vision_score),  backgroundColor: '#e8405733', borderColor: '#e84057', borderWidth: 1, borderRadius: 4 },
      ],
    },
    options: chartBase(),
  });

  // MVP radar
  const blueMVP = data.blue_team.reduce((a, b) => a.kda > b.kda ? a : b);
  const redMVP  = data.red_team.reduce((a, b)  => a.kda > b.kda ? a : b);
  mvpChart = buildRadar(
    'mvp-radar',
    [radarVals(blueMVP), radarVals(redMVP)],
    [`Blue: ${blueMVP.champion}`, `Red: ${redMVP.champion}`],
    mvpChart
  );

  // Gold donut
  const blueGold = data.blue_team.reduce((s, p) => s + p.gold_earned, 0);
  const redGold  = data.red_team.reduce((s, p)  => s + p.gold_earned, 0);
  if (goldChart) goldChart.destroy();
  goldChart = new Chart(document.getElementById('gold-chart').getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Blue team', 'Red team'],
      datasets: [{
        data:            [blueGold, redGold],
        backgroundColor: ['#0bc4e333', '#e8405733'],
        borderColor:     ['#0bc4e3',   '#e84057'],
        borderWidth: 2,
      }],
    },
    options: {
      plugins: { legend: { labels: { color: CHART_TICK, font: CHART_FONT } } },
      cutout: '62%',
    },
  });
}

function renderAIReports(data) {
  document.getElementById('blue-report').innerHTML = formatReport(data.blue_report);
  document.getElementById('red-report').innerHTML  = formatReport(data.red_report);
}
