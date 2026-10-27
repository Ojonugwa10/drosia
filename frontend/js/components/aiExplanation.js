/**
 * Evidence-Grounded Operational Intelligence & AI Explanation Component
 * Implements Section 7 Module F, Section 3 Stage 8, and FR-06
 */

const aiExplanation = {
  async init() {
    await this.loadExplanation();
  },

  async loadExplanation() {
    try {
      const data = await api.get('/analytics/explanation');
      this.render(data);
    } catch (e) {
      console.error('Error loading AI explanation:', e);
    }
  },

  render(data) {
    const container = document.getElementById('ai-explanation-content');
    if (!container) return;

    const claims = data.structured_claims || [];

    container.innerHTML = `
      <div style="background:rgba(0,240,255,0.04); border:1px solid rgba(0,240,255,0.25); border-radius:10px; padding:20px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <svg style="width:20px; height:20px; color:#00f0ff;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10H12V2z"></path><path d="M12 12L2.5 7.5"></path></svg>
            <h4 style="font-size:16px; font-weight:700; color:#fff;">Evidence-Grounded Intelligence Briefing // ${data.mission_code}</h4>
          </div>
          <span class="badge-status badge-verified">${data.governance_compliance}</span>
        </div>
        <p style="font-size:14px; color:#e2e8f0; line-height:1.7;">
          ${data.executive_summary}
        </p>
      </div>

      <div style="font-size:15px; font-weight:700; color:#fff; margin-bottom:12px; display:flex; align-items:center; gap:8px;">
        <span>3. Structured Analytical Claims & Evidence Lineage</span>
        <span style="font-size:11px; font-family:var(--font-mono); color:#64748b;">(Deterministic calculations paired with verified evidence links)</span>
      </div>

      <div style="display:flex; flex-direction:column; gap:14px;">
        ${claims.map(c => `
          <div class="tactical-panel" style="padding:16px; border-left:3px solid #00f0ff;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <span style="font-family:var(--font-mono); font-size:11px; color:#00f0ff; text-transform:uppercase; font-weight:700;">${c.claim_type}</span>
              <span style="font-size:11px; color:#10b981; font-family:var(--font-mono);">Confidence: ${c.confidence}</span>
            </div>
            <div style="font-size:13.5px; font-weight:600; color:#fff; line-height:1.6; margin-bottom:8px;">
              "${c.statement}"
            </div>
            <div style="background:rgba(0,0,0,0.25); padding:10px; border-radius:6px; font-size:11.5px; margin-bottom:8px;">
              <strong style="color:#94a3b8;">Supporting Evidence Citations:</strong>
              <ul style="margin:4px 0 0 18px; color:#cbd5e1;">
                ${c.supporting_evidence.map(e => `<li>${e}</li>`).join('')}
              </ul>
            </div>
            <div style="font-size:11px; color:#f59e0b; background:rgba(245,158,11,0.06); padding:6px 10px; border-radius:4px; border:1px solid rgba(245,158,11,0.2);">
              <strong>Governance Limitation:</strong> ${c.limitations}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  },
};
