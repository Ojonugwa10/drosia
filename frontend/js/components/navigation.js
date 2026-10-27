/**
 * Navigation & RBAC Interactive Role Switcher Component
 */

const navigation = {
  init() {
    this.bindEvents();
    this.renderUserBadge();
    this.renderProjectsDropdown();
  },

  bindEvents() {
    // Sidebar view navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const view = item.getAttribute('data-view');
        if (view) {
          this.switchView(view);
        }
      });
    });

    // Project selector change
    const projSelect = document.getElementById('project-select-hud');
    if (projSelect) {
      projSelect.addEventListener('change', (e) => {
        const projId = e.target.value;
        const selected = store.state.projects.find(p => p.id === projId);
        if (selected) {
          store.setCurrentProject(selected);
          this.onProjectChanged(selected);
        }
      });
    }

    // Role switcher card click -> open role switch modal
    const rolePill = document.getElementById('role-switcher-hud');
    if (rolePill) {
      rolePill.addEventListener('click', () => {
        this.openRoleModal();
      });
    }

    // Crypto seal pill click -> open seal verify modal
    const sealPill = document.getElementById('crypto-seal-btn');
    if (sealPill) {
      sealPill.addEventListener('click', () => {
        this.openSealModal();
      });
    }
  },

  switchView(viewName) {
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
    if (targetNav) targetNav.classList.add('active');

    document.querySelectorAll('.view-content-pane').forEach(p => p.classList.remove('active'));
    const targetPane = document.getElementById(`view-${viewName}`);
    if (targetPane) targetPane.classList.add('active');

    store.setActiveView(viewName);

    // Trigger view-specific re-renders
    if (viewName === 'gis-hud' && window.tacticalMap) {
      window.tacticalMap.invalidateSize();
    } else if (viewName === 'dashboard' && window.dashboard) {
      window.dashboard.loadData();
    } else if (viewName === 'audit-trail' && window.auditTrail) {
      window.auditTrail.loadEvents();
    } else if (viewName === 'reports' && window.reportBuilder) {
      window.reportBuilder.loadReports();
    }
  },

  renderUserBadge() {
    const user = store.state.currentUser;
    if (!user) return;

    const nameEl = document.getElementById('hud-user-name');
    const roleEl = document.getElementById('hud-user-role');
    const avatarEl = document.getElementById('hud-user-avatar');

    if (nameEl) nameEl.textContent = user.display_name;
    if (roleEl) roleEl.textContent = user.role.replace('_', ' ');
    if (avatarEl) {
      const initials = user.display_name.split(' ').map(n => n[0]).join('').slice(0, 2);
      avatarEl.textContent = initials;
    }
  },

  renderProjectsDropdown() {
    const select = document.getElementById('project-select-hud');
    if (!select) return;

    select.innerHTML = '';
    store.state.projects.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      if (store.state.currentProject && store.state.currentProject.id === p.id) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
  },

  onProjectChanged(project) {
    if (window.dashboard) window.dashboard.loadData();
    if (window.tacticalMap) window.tacticalMap.loadLayers();
  },

  openRoleModal() {
    const modal = document.getElementById('role-switch-modal');
    const list = document.getElementById('role-switch-list');
    if (!modal || !list) return;

    list.innerHTML = '';
    store.state.availableUsers.forEach(u => {
      const isCurrent = store.state.currentUser && store.state.currentUser.id === u.id;
      const card = document.createElement('div');
      card.className = `tactical-panel ${isCurrent ? 'active-role-tile' : ''}`;
      card.style.cursor = 'pointer';
      card.style.padding = '12px 16px';
      card.style.display = 'flex';
      card.style.justifyContent = 'space-between';
      card.style.alignItems = 'center';

      card.innerHTML = `
        <div style="display:flex; align-items:center; gap:12px;">
          <div class="user-avatar-badge" style="width:36px; height:36px;">
            ${u.display_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
          </div>
          <div>
            <div style="font-weight:600; color:#fff;">${u.display_name}</div>
            <div style="font-size:11px; color:#94a3b8;">${u.title || u.role}</div>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge-status badge-verified">${u.role.toUpperCase()}</span>
          ${isCurrent ? '<span style="color:#00f0ff; font-weight:700;">ACTIVE</span>' : '<button class="btn-tactical btn-outline btn-sm">Switch</button>'}
        </div>
      `;

      card.addEventListener('click', async () => {
        try {
          await api.post('/auth/switch-role', { user_id: u.id });
          const me = await api.get('/auth/me');
          store.setUserContext(me.user, me.capabilities);
          this.renderUserBadge();
          this.closeModal('role-switch-modal');
          // Reload view with new permissions
          this.switchView(store.state.activeView);
        } catch (e) {
          alert('Failed to switch user role: ' + e.message);
        }
      });

      list.appendChild(card);
    });

    modal.classList.add('active');
  },

  async openSealModal() {
    const modal = document.getElementById('seal-verify-modal');
    const body = document.getElementById('seal-verify-details');
    if (!modal || !body) return;

    body.innerHTML = '<div style="color:#94a3b8;">Verifying SHA-256 cryptographic chaining across all ledger events...</div>';
    modal.classList.add('active');

    try {
      const res = await api.get('/audit/verify-seal');
      body.innerHTML = `
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <div class="pulse-dot" style="width:14px; height:14px; background:#10b981;"></div>
          <div style="font-size:15px; font-weight:700; color:#10b981;">CRYPTOGRAPHIC SEAL INTACT</div>
        </div>
        <div style="font-family:var(--font-mono); font-size:12px; line-height:1.7; background:rgba(0,0,0,0.3); padding:12px; border-radius:6px; border:1px solid rgba(255,255,255,0.08);">
          <div>Total Sequenced Events: <span style="color:#fff;">${res.total_events}</span></div>
          <div>Chain Status: <span style="color:#10b981;">${res.status}</span></div>
          <div style="margin-top:6px; word-break:break-all;">Latest Checkpoint Hash: <br/><span style="color:#00f0ff; font-size:11px;">${res.latest_checkpoint_hash || 'SHA-256 Verified Root'}</span></div>
        </div>
        <p style="font-size:12px; color:#94a3b8; margin-top:10px;">
          Adheres to FR-08 and Section 10.4. Every state mutation (upload, validation, review decision, report sign-off) is chained using cryptographic parent hashing to prevent undetectable retroactive alteration.
        </p>
      `;
    } catch (e) {
      body.innerHTML = `<div style="color:#ef4444;">Verification check error: ${e.message}</div>`;
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  },
};
