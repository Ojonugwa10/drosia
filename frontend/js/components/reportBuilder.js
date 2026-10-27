/**
 * Report Builder & Multi-Stage Approval Workflow Component
 * Implements Section 3 Stage 10, Section 8.7, and FR-07
 */

const reportBuilder = {
  activeReport: null,

  async init() {
    await this.loadReports();
    this.bindEvents();
  },

  bindEvents() {
    const printBtn = document.getElementById('btn-print-report-pdf');
    if (printBtn) {
      printBtn.addEventListener('click', () => window.print());
    }

    const exportCsvBtn = document.getElementById('btn-export-report-csv');
    if (exportCsvBtn) {
      exportCsvBtn.addEventListener('click', () => this.exportCSV());
    }
  },

  async loadReports() {
    try {
      const reports = await api.get('/reports');
      store.state.reports = reports;
      if (reports.length > 0) {
        await this.loadReportDetails(reports[0].id);
      }
    } catch (e) {
      console.error('Error loading reports:', e);
    }
  },

  async loadReportDetails(reportId) {
    try {
      const rep = await api.get(`/reports/${reportId}`);
      this.activeReport = rep;
      this.renderReportPreview(rep);
      this.renderApprovalControls(rep);
    } catch (e) {
      console.error('Error loading report details:', e);
    }
  },

  renderReportPreview(rep) {
    const container = document.getElementById('report-document-body');
    if (!container) return;

    let findingsHtml = '';
    if (rep.detailed_findings && rep.detailed_findings.length > 0) {
      findingsHtml = rep.detailed_findings.map(f => {
        let mediaHtml = '';
        if (f.media_evidence && f.media_evidence.length > 0) {
          mediaHtml = `
            <div class="report-evidence-grid" style="margin-top:12px;">
              ${f.media_evidence.map(m => `
                <div class="report-evidence-card">
                  <img src="${m.thumbnail_path}" class="report-evidence-img" alt="Evidence Photo" onerror="this.style.display='none'"/>
                  <div class="report-evidence-caption">
                    <span class="evidence-caption-title">${m.original_filename}</span>
                    <span class="evidence-caption-meta">Sensor: ${m.sensor_type} | Alt: ${m.altitude_m || 120}m AGL | Status: ${m.integrity_status}</span>
                  </div>
                </div>
              `).join('')}
            </div>
          `;
        }

        return `
          <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-weight:700; color:#fff; font-size:14px;">${f.summary}</span>
              <span class="badge-status ${f.verification_status === 'Confirmed Threat' ? 'badge-threat' : 'badge-verified'}">${f.verification_status}</span>
            </div>
            <p style="font-size:13px; color:#cbd5e1; line-height:1.6;">${f.detailed_explanation}</p>
            ${mediaHtml}
          </div>
        `;
      }).join('');
    }

    container.innerHTML = `
      <div class="report-classification-banner">
        OFFICIAL SENSITIVE // RESTRICTED SECURITY SURVEILLANCE INTELLIGENCE
      </div>

      <div class="report-header-block">
        <div class="report-title-area">
          <h2>${rep.report_title}</h2>
          <div style="font-size:12px; color:#94a3b8; font-family:var(--font-mono);">
            DOCUMENT REF: ${rep.id.toUpperCase()} // VERSION ${rep.version_number}.0 // STATUS: <span style="color:#00f0ff; font-weight:700;">${rep.status.toUpperCase()}</span>
          </div>
        </div>
        <div class="report-meta-grid">
          <div><strong>Period:</strong> ${rep.reporting_period_start.slice(0, 10)} to ${rep.reporting_period_end.slice(0, 10)}</div>
          <div><strong>Compiled By:</strong> Operations Analysis Unit</div>
          <div><strong>Classification:</strong> Official Sensitive</div>
          <div><strong>Storage Key:</strong> ${rep.storage_key || 'reports/rep_v1.json'}</div>
        </div>
      </div>

      <div class="report-section">
        <div class="report-section-title">1. Executive Operational Summary</div>
        <div class="report-narrative">${rep.executive_summary}</div>
      </div>

      <div class="report-section">
        <div class="report-section-title">2. Operational Findings & Verified Evidence Lineage</div>
        ${findingsHtml || '<p style="color:#94a3b8;">No linked operational findings.</p>'}
      </div>

      <div class="report-section">
        <div class="report-section-title">3. Analytical Methodology & Sensor Limitations</div>
        <div class="report-disclaimer-box">
          <div class="disclaimer-title">Mandatory Governance & Uncertainty Disclosure</div>
          <div class="disclaimer-text">${rep.methodology_and_limitations}</div>
        </div>
      </div>

      <div class="report-signoff-block">
        <div>
          <div>Report Approver: <strong style="color:#fff;">${rep.approved_by_name || 'Pending Review Sign-off'}</strong></div>
          <div style="color:#64748b; font-size:10.5px;">Authorization Timestamp: ${rep.approved_at ? rep.approved_at.replace('T', ' ').slice(0, 19) + ' UTC' : 'Awaiting Final Signature'}</div>
        </div>
        <div class="signoff-seal">
          <div class="pulse-dot"></div>
          <span>CRYPTOGRAPHIC VERIFICATION SEAL ACTIVE</span>
        </div>
      </div>
    `;
  },

  renderApprovalControls(rep) {
    const controls = document.getElementById('report-approval-action-bar');
    if (!controls) return;

    const role = store.state.currentUser ? store.state.currentUser.role : 'ops_manager';
    const isApprover = ['approver', 'org_admin'].includes(role);

    controls.innerHTML = `
      <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-family:var(--font-mono); font-size:12px; color:#94a3b8;">
          Workflow State: <strong style="color:#00f0ff;">${rep.status}</strong>
        </span>
        ${rep.status === 'Draft' ? `
          <button class="btn-tactical btn-outline btn-sm" onclick="reportBuilder.transitionStatus('${rep.id}', 'Validation')">
            Submit for Validation
          </button>
        ` : ''}
        ${rep.status === 'Validation' ? `
          <button class="btn-tactical btn-outline btn-sm" onclick="reportBuilder.transitionStatus('${rep.id}', 'Review')">
            Send for Supervisor Review
          </button>
        ` : ''}
        ${rep.status === 'Review' && isApprover ? `
          <button class="btn-tactical btn-success btn-sm" onclick="reportBuilder.transitionStatus('${rep.id}', 'Approved')">
            ✓ Sign & Approve Report
          </button>
          <button class="btn-tactical btn-danger btn-sm" onclick="reportBuilder.rejectReport('${rep.id}')">
            Reject Report
          </button>
        ` : (rep.status === 'Review' && !isApprover ? `
          <span style="font-size:11px; color:#f59e0b;">(Requires 'approver' or 'org_admin' role to sign off)</span>
        ` : '')}
        ${rep.status === 'Approved' && isApprover ? `
          <button class="btn-tactical btn-primary-cyan btn-sm" onclick="reportBuilder.transitionStatus('${rep.id}', 'Published')">
            Publish Report
          </button>
        ` : ''}
      </div>
    `;
  },

  async transitionStatus(reportId, newStatus) {
    try {
      await api.post(`/reports/${reportId}/transition`, { new_status: newStatus });
      await this.loadReportDetails(reportId);
      alert(`Report transitioned to ${newStatus}`);
    } catch (e) {
      alert('Error updating report status: ' + e.message);
    }
  },

  async rejectReport(reportId) {
    const reason = prompt('Please enter rejection reason / remediation requirement:');
    if (!reason) return;
    try {
      await api.post(`/reports/${reportId}/transition`, {
        new_status: 'Rejected',
        rejection_reason: reason,
      });
      await this.loadReportDetails(reportId);
      alert('Report rejected with documented remediation feedback.');
    } catch (e) {
      alert('Error rejecting report: ' + e.message);
    }
  },

  exportCSV() {
    if (!this.activeReport) return;
    const csvContent = "data:text/csv;charset=utf-8," +
      "Report_ID,Title,Period_Start,Period_End,Status,Approved_By\n" +
      `"${this.activeReport.id}","${this.activeReport.report_title}","${this.activeReport.reporting_period_start}","${this.activeReport.reporting_period_end}","${this.activeReport.status}","${this.activeReport.approved_by_name || 'N/A'}"`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${this.activeReport.id}_summary.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
};
