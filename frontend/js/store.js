/**
 * Drosia Client State Store
 */

const store = {
  state: {
    currentUser: null,
    capabilities: {},
    availableUsers: [],
    projects: [],
    currentProject: null,
    missions: [],
    currentMission: null,
    activeView: 'dashboard',
    uploadBatches: [],
    findings: [],
    reports: [],
    auditSeal: { valid: true, status: 'Active' },
  },

  listeners: [],

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  },

  notify(event, data) {
    this.listeners.forEach(listener => listener(event, data, this.state));
  },

  setUserContext(user, capabilities) {
    this.state.currentUser = user;
    this.state.capabilities = capabilities;
    this.notify('USER_CHANGED', user);
  },

  setProjects(projects) {
    this.state.projects = projects;
    if (projects.length > 0 && !this.state.currentProject) {
      this.state.currentProject = projects[0];
    }
    this.notify('PROJECTS_LOADED', projects);
  },

  setCurrentProject(project) {
    this.state.currentProject = project;
    this.notify('CURRENT_PROJECT_CHANGED', project);
  },

  setMissions(missions) {
    this.state.missions = missions;
    if (missions.length > 0) {
      this.state.currentMission = missions[0];
    }
    this.notify('MISSIONS_LOADED', missions);
  },

  setCurrentMission(mission) {
    this.state.currentMission = mission;
    this.notify('CURRENT_MISSION_CHANGED', mission);
  },

  setActiveView(viewName) {
    this.state.activeView = viewName;
    this.notify('VIEW_CHANGED', viewName);
  },
};
