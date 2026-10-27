/**
 * Drosia Application Bootstrap
 */

document.addEventListener('DOMContentLoaded', async () => {
  console.log('Initializing Drosia: Drone Security Intelligence & Analytics Platform v1.0...');

  try {
    // 1. Fetch initial user session and capabilities
    const [me, users, projects] = await Promise.all([
      api.get('/auth/me'),
      api.get('/auth/users'),
      api.get('/projects'),
    ]);

    store.setUserContext(me.user, me.capabilities);
    store.state.availableUsers = users;
    store.setProjects(projects);

    // 2. Fetch missions for current project
    if (projects.length > 0) {
      const missions = await api.get(`/missions?project_id=${projects[0].id}`);
      store.setMissions(missions);
    }

    // 3. Initialize components
    navigation.init();
    dashboard.loadData();
    tacticalMap.init();
    uploader.init();
    findingsReview.init();
    reportBuilder.init();
    auditTrail.init();
    aiExplanation.init();

    // Attach globals for inline event handlers
    window.api = api;
    window.store = store;
    window.navigation = navigation;
    window.dashboard = dashboard;
    window.tacticalMap = tacticalMap;
    window.uploader = uploader;
    window.dataQuality = dataQuality;
    window.findingsReview = findingsReview;
    window.reportBuilder = reportBuilder;
    window.auditTrail = auditTrail;
    window.aiExplanation = aiExplanation;

    console.log('Drosia Platform initialized successfully.');
  } catch (e) {
    console.error('Fatal initialization error:', e);
    const container = document.querySelector('.main-viewport');
    if (container) {
      container.innerHTML = `
        <div style="padding:40px; text-align:center; color:#ef4444;">
          <h3>Connection Error</h3>
          <p>Failed to connect to Drosia Backend API at /api/v1. Ensure backend server is running.</p>
          <pre style="font-family:monospace; margin-top:12px; color:#94a3b8;">${e.stack || e.message}</pre>
        </div>
      `;
    }
  }
});
