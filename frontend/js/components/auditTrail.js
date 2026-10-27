/**
 * Tamper-Evident Cryptographic Audit Trail Component
 * Implements Section 5.1, Section 10.4, and FR-08
 */

const auditTrail = {
  events: [],

  async init() {
    await this.loadEvents();
    this.bindEvents();
  },

  bindEvents() {
    const filterSelect = document.getElementById('audit-action-filter');
    if (filterSelect) {
      filterSelect.addEventListener('change', () => this.filterEvents());
    }

    const verifyBtn = document.getElementById('btn-verify-audit-chain');
    if (verifyBtn) {
      verifyBtn.addEventListener('click', () => navigation.openSealModal());
    }

    const exportBtn = document.getElementById('btn-export-audit-csv');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportAuditCSV());
    }
  },

  async loadEvents() {
    try {
      const events = await api.get('/audit/events');
      this.events = events;
      this.renderTable(events);
    } catch (e) {
      const container = document.getElementById('audit-events-table-body');
      if (container) {
        container.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#ef4444; padding:20px;">Access restricted: ${e.message}</td></tr>`;
      }
    }
  },

  renderTable(events) {
    const container = document.getElementById('audit-events-table-body');
    if (!container) return;

    if (events.length === 0) {
      container.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b; padding:20px;">No audit events recorded.</td></tr>';
      return;
    }

    container.innerHTML = events.map(ev => `
      <tr>
        <td class="cell-mono" style="color:#00f0ff; font-weight:600;">${ev.id}</td>
        <td class="cell-mono">${ev.event_timestamp ? ev.event_timestamp.slice(0, 19).replace('T', ' ') : ''}</td>
        <td>
          <div style="font-weight:600; color:#fff;">${ev.actor_name}</div>
          <div style="font-family:var(--font-mono); font-size:10px; color:#94a3b8;">${ev.actor_role}</div>
        </td>
        <td><span class="badge-status badge-verified">${ev.action_type}</span></td>
        <td class="cell-mono">${ev.resource_type}: ${ev.resource_id}</td>
        <td class="cell-mono" style="font-size:10px; color:#64748b;" title="Event Hash: ${ev.event_hash} | Parent: ${ev.previous_hash}">
          ${ev.event_hash.slice(0, 16)}...
        </td>
      </tr>
    `).join('');
  },

  filterEvents() {
    const filterSelect = document.getElementById('audit-action-filter');
    const action = filterSelect ? filterSelect.value : '';
    const filtered = action ? this.events.filter(e => e.action_type === action) : this.events;
    this.renderTable(filtered);
  },

  exportAuditCSV() {
    if (!this.events.length) return;
    let csv = "Event_ID,Timestamp,Actor_Name,Actor_Role,Action_Type,Resource_Type,Resource_ID,SHA256_Hash\n";
    this.events.forEach(e => {
      csv += `"${e.id}","${e.event_timestamp}","${e.actor_name}","${e.actor_role}","${e.action_type}","${e.resource_type}","${e.resource_id}","${e.event_hash}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `drosia_audit_trail_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  },
};
