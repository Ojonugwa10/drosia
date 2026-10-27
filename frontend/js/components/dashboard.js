/**
 * Dashboard & KPI Analytics Component
 */

const dashboard = {
  charts: {},

  async loadData() {
    try {
      const projId = store.state.currentProject ? store.state.currentProject.id : null;
      const [perf, coverage, incSummary, fleet] = await Promise.all([
        api.get(`/analytics/mission-performance${projId ? `?project_id=${projId}` : ''}`),
        api.get('/analytics/coverage'),
        api.get(`/analytics/incidents-summary${projId ? `?project_id=${projId}` : ''}`),
        api.get('/analytics/fleet-health'),
      ]);

      this.renderKPITiles(perf, coverage, incSummary, fleet);
      this.renderCharts(incSummary, perf);
    } catch (e) {
      console.error('Error loading dashboard analytics:', e);
    }
  },

  renderKPITiles(perf, coverage, incSummary, fleet) {
    const container = document.getElementById('dashboard-kpi-grid');
    if (!container) return;

    container.innerHTML = `
      <div class="kpi-tile">
        <div class="kpi-top-row">
          <span class="kpi-label">Mission Completion</span>
          <svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        </div>
        <div class="kpi-value">${perf.mission_completion_rate_pct}%</div>
        <div class="kpi-subtext">
          <span class="highlight">${perf.missions_completed}</span> of ${perf.missions_attempted} eligible completed
        </div>
      </div>

      <div class="kpi-tile">
        <div class="kpi-top-row">
          <span class="kpi-label">Flight Hours</span>
          <svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        </div>
        <div class="kpi-value">${perf.total_flight_hours} <span style="font-size:14px; font-weight:500;">hrs</span></div>
        <div class="kpi-subtext">
          Avg duration: <span class="highlight">${perf.avg_mission_duration_min} min</span>
        </div>
      </div>

      <div class="kpi-tile">
        <div class="kpi-top-row">
          <span class="kpi-label">Corridor Coverage</span>
          <svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
        </div>
        <div class="kpi-value">${coverage.corridor_coverage_pct}%</div>
        <div class="kpi-subtext" title="Track coverage; ground visibility qualified">
          Track: <span class="highlight">${coverage.observed_track_length_km} km</span> (dev ${coverage.route_deviation_mean_m}m)
        </div>
      </div>

      <div class="kpi-tile">
        <div class="kpi-top-row">
          <span class="kpi-label">Verified Observations</span>
          <svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
        </div>
        <div class="kpi-value">${incSummary.verification_ratio_pct}%</div>
        <div class="kpi-subtext">
          <span class="highlight">${incSummary.total_incidents_recorded}</span> total observations logged
        </div>
      </div>

      <div class="kpi-tile">
        <div class="kpi-top-row">
          <span class="kpi-label">Fleet Readiness</span>
          <svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
        </div>
        <div class="kpi-value">${fleet.fleet_availability_pct}%</div>
        <div class="kpi-subtext">
          <span class="highlight">${fleet.active_available_aircraft}</span> of ${fleet.total_aircraft_in_fleet} UAVs available
        </div>
      </div>

      <div class="kpi-tile">
        <div class="kpi-top-row">
          <span class="kpi-label">Processing Turnaround</span>
          <svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
        </div>
        <div class="kpi-value">${perf.avg_turnaround_time_min} <span style="font-size:14px; font-weight:500;">min</span></div>
        <div class="kpi-subtext">
          <span class="highlight">Automated</span> ingest to dashboard
        </div>
      </div>
    `;
  },

  renderCharts(incSummary, perf) {
    // Incident Category Doughnut Chart
    const catCanvas = document.getElementById('chart-incident-categories');
    if (catCanvas && window.Chart) {
      if (this.charts.cat) this.charts.cat.destroy();

      const labels = Object.keys(incSummary.by_category || {});
      const values = Object.values(incSummary.by_category || {});

      this.charts.cat = new Chart(catCanvas, {
        type: 'doughnut',
        data: {
          labels: labels.length ? labels : ['Perimeter Breach', 'Thermal Anomaly', 'Suspicious Loitering'],
          datasets: [{
            data: values.length ? values : [1, 1, 1],
            backgroundColor: ['#ef4444', '#f59e0b', '#00f0ff', '#3b82f6', '#10b981'],
            borderColor: '#0c121d',
            borderWidth: 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: { color: '#94a3b8', font: { family: 'Outfit', size: 11 } },
            },
          },
          cutout: '70%',
        },
      });
    }

    // Severity & Verification Breakdown Bar Chart
    const verCanvas = document.getElementById('chart-verification-status');
    if (verCanvas && window.Chart) {
      if (this.charts.ver) this.charts.ver.destroy();

      const verLabels = Object.keys(incSummary.by_verification_status || {});
      const verValues = Object.values(incSummary.by_verification_status || {});

      this.charts.ver = new Chart(verCanvas, {
        type: 'bar',
        data: {
          labels: verLabels,
          datasets: [{
            label: 'Observations',
            data: verValues,
            backgroundColor: ['#64748b', '#00f0ff', '#10b981', '#ef4444'],
            borderRadius: 4,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' } },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }
  },
};
