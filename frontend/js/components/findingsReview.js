/**
 * Findings & Human-in-the-Loop Review Workbench Component
 * Implements Section 3 Stages 8 & 9, and FR-06
 */

const findingsReview = {
  activeFindingId: null,

  async init() {
    await this.loadFindings();
    this.bindEvents();
  },

  bindEvents() {
    const confirmBtn = document.getElementById('submit-review-decision-btn');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => this.submitDecision());
    }
  },

  async loadFindings() {
    try {
      const findings = await api.get('/findings');
      store.state.findings = findings;
      this.renderFindingsList(findings);
    } catch (e) {
      console.error('Error loading findings:', e);
    }
  },

  renderFindingsList(findings) {
    const container = document.getElementById('findings-list-container');
    if (!container) return;

    if (findings.length === 0) {
      container.innerHTML = '<div style="color:#64748b; padding:20px; text-align:center;">No findings recorded for active project.</div>';
      return;
    }

    container.innerHTML = findings.map(f => {
      const isThreat = f.verification_status === 'Confirmed Threat';
      const isVerified = f.verification_status === 'Verified Observation';
      const badgeClass = isThreat ? 'badge-threat' : (isVerified ? 'badge-verified' : 'badge-unverified');

      let evidenceHtml = '';
      if (f.media_evidence && f.media_evidence.length > 0) {
        evidenceHtml = f.media_evidence.map(m => `
          <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:10px; display:flex; gap:12px; align-items:center; margin-top:8px;">
            <img src="${m.thumbnail_path}" style="width:110px; height:70px; object-fit:cover; border-radius:6px; cursor:pointer;" onclick="findingsReview.zoomImage('${m.thumbnail_path}')" alt="Evidence" onerror="this.style.display='none'"/>
            <div>
              <div style="font-weight:600; font-size:12px; color:#fff;">${m.original_filename}</div>
              <div style="font-family:var(--font-mono); font-size:11px; color:#00f0ff;">Sensor: ${m.sensor_type}</div>
              <div style="font-size:10.5px; color:#64748b;">Integrity: ${m.integrity_status}</div>
            </div>
          </div>
        `).join('');
      }

      return `
        <div class="tactical-panel" style="margin-bottom:16px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
            <div>
              <div style="display:flex; align-items:center; gap:10px;">
                <span class="badge-status ${badgeClass}">${f.verification_status}</span>
                <span style="font-family:var(--font-mono); font-size:11px; color:#00f0ff; font-weight:700;">${f.id}</span>
                <span style="font-family:var(--font-mono); font-size:11px; color:#64748b;">${f.review_status}</span>
              </div>
              <h4 style="font-size:16px; font-weight:700; color:#fff; margin-top:6px;">${f.summary}</h4>
            </div>
            <div style="display:flex; gap:8px;">
              <button class="btn-tactical btn-outline btn-sm" onclick="findingsReview.openDecisionModal('${f.id}', 'Accept')">Accept Finding</button>
              <button class="btn-tactical btn-danger btn-sm" onclick="findingsReview.openDecisionModal('${f.id}', 'Confirmed Threat')">Escalate Threat</button>
              <button class="btn-tactical btn-outline btn-sm" onclick="findingsReview.openDecisionModal('${f.id}', 'Reject')">Reject (False Alarm)</button>
            </div>
          </div>

          <p style="font-size:13px; color:#cbd5e1; line-height:1.6; margin-bottom:10px;">${f.detailed_explanation}</p>

          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; background:rgba(0,0,0,0.2); padding:10px 14px; border-radius:6px; font-size:11.5px; margin-bottom:10px;">
            <div><strong>Supporting Metrics:</strong> <span style="font-family:var(--font-mono); color:#00f0ff;">${JSON.stringify(f.supporting_metrics)}</span></div>
            <div><strong>Confidence / Uncertainty:</strong> <span style="color:#94a3b8;">${f.uncertainty_information}</span></div>
          </div>

          <div style="font-size:11px; color:#f59e0b; background:rgba(245,158,11,0.06); padding:8px 12px; border-radius:6px; border-left:2px solid #f59e0b; margin-bottom:10px;">
            <strong>Data Limitations:</strong> ${f.data_quality_limitations}
          </div>

          ${evidenceHtml}
        </div>
      `;
    }).join('');
  },

  openDecisionModal(findingId, defaultDecision) {
    this.activeFindingId = findingId;
    const modal = document.getElementById('finding-decision-modal');
    const select = document.getElementById('review-decision-select');
    const rationale = document.getElementById('review-rationale-input');

    if (!modal) return;
    if (select) select.value = defaultDecision;
    if (rationale) rationale.value = '';

    modal.classList.add('active');
  },

  async submitDecision() {
    if (!this.activeFindingId) return;

    const select = document.getElementById('review-decision-select');
    const rationale = document.getElementById('review-rationale-input');

    const decision = select.value;
    const reason = rationale.value.trim();

    if (!reason || reason.length < 5) {
      alert('Please enter a substantive review rationale for audit tracking.');
      return;
    }

    try {
      await api.post(`/findings/${this.activeFindingId}/review`, {
        decision: decision,
        rationale: reason,
      });

      navigation.closeModal('finding-decision-modal');
      await this.loadFindings();
      alert(`Review decision recorded: ${decision}`);
    } catch (e) {
      alert('Error recording review: ' + e.message);
    }
  },

  zoomImage(src) {
    const modal = document.getElementById('evidence-zoom-modal');
    const img = document.getElementById('evidence-zoomed-img');
    if (modal && img) {
      img.src = src;
      modal.classList.add('active');
    }
  },
};
