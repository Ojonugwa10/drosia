/**
 * Data Quality & Canonical Standardization Component
 * Implements Section 3 Stages 4 & 5, Section 6, and FR-03/FR-04
 */

const dataQuality = {
  currentBatch: null,
  activeFile: null,

  async loadBatch(batchId) {
    try {
      const batch = await api.get(`/uploads/${batchId}`);
      this.currentBatch = batch;
      if (batch.files && batch.files.length > 0) {
        this.selectFile(batch.files[0]);
      }
    } catch (e) {
      console.error('Error loading batch quality:', e);
    }
  },

  selectFile(fileRecord) {
    this.activeFile = fileRecord;
    this.renderQualityOverview(fileRecord);
    this.renderIssuesTable(fileRecord);
    this.renderRecordsSample(fileRecord);
  },

  renderQualityOverview(file) {
    const container = document.getElementById('data-quality-file-header');
    if (!container) return;

    const breakdown = file.quality_breakdown || {
      'Completeness': 100,
      'Validity': 95,
      'Consistency': 90,
      'Uniqueness': 100,
      'Timeliness': 92,
      'Geospatial Reliability': 96,
      'Provenance': 100,
    };

    const isQuarantined = file.validation_status === 'Quarantined';
    const isWarning = file.validation_status === 'Accepted with Warnings';
    const badgeClass = isQuarantined ? 'badge-quarantined' : (isWarning ? 'badge-warnings' : 'badge-accepted');

    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
        <div>
          <div style="font-size:18px; font-weight:700; color:#fff;">${file.original_filename}</div>
          <div style="font-family:var(--font-mono); font-size:11px; color:#94a3b8; margin-top:2px;">
            SHA-256: <span style="color:#00f0ff;">${file.sha256_checksum.slice(0, 24)}...</span> | Size: ${(file.file_size_bytes / 1024).toFixed(1)} KB
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
          <span class="badge-status ${badgeClass}" style="font-size:12px; padding:4px 10px;">${file.validation_status}</span>
          ${!isQuarantined && !file.is_standardized ? `
            <button class="btn-tactical btn-primary-cyan btn-sm" onclick="dataQuality.triggerStandardize('${file.id}')">
              Standardize to Canonical Schema
            </button>
          ` : (file.is_standardized ? '<span style="color:#10b981; font-family:var(--font-mono); font-size:12px;">✓ CANONICAL SCHEMA APPLIED</span>' : '')}
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 180px 1fr; gap:24px; align-items:center; background:rgba(0,0,0,0.25); padding:16px; border-radius:8px; border:1px solid rgba(255,255,255,0.06);">
        <div style="text-align:center;">
          <div style="font-size:36px; font-weight:800; color:${file.overall_quality_score >= 85 ? '#10b981' : (file.overall_quality_score >= 70 ? '#f59e0b' : '#ef4444')};">
            ${file.overall_quality_score || 100}%
          </div>
          <div style="font-family:var(--font-mono); font-size:10px; color:#64748b; text-transform:uppercase;">Composite Quality Score</div>
        </div>
        <div>
          ${Object.entries(breakdown).map(([dim, score]) => `
            <div class="quality-dim-row">
              <span class="dim-name">${dim}</span>
              <div class="dim-progress-track">
                <div class="dim-progress-fill" style="width:${score}%; background:${score >= 85 ? '#00f0ff' : (score >= 70 ? '#f59e0b' : '#ef4444')};"></div>
              </div>
              <span class="dim-pct" style="color:${score >= 85 ? '#00f0ff' : (score >= 70 ? '#f59e0b' : '#ef4444')};">${score.toFixed(0)}%</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderIssuesTable(file) {
    const container = document.getElementById('quality-issues-table-body');
    if (!container) return;

    const issues = file.validation_issues || [];
    if (issues.length === 0) {
      container.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#10b981; padding:20px;">✓ All structural, coordinate, timestamp, and schema integrity checks passed!</td></tr>';
      return;
    }

    container.innerHTML = issues.map(iss => {
      const isCritical = iss.severity === 'CRITICAL';
      const badgeClass = isCritical ? 'badge-quarantined' : 'badge-warnings';

      return `
        <tr>
          <td><span class="badge-status ${badgeClass}">${iss.severity}</span></td>
          <td style="font-family:var(--font-mono); font-size:11px; color:#94a3b8;">${iss.dimension || 'Validity'}</td>
          <td class="cell-mono">${iss.row ? 'Row ' + iss.row : 'Header/File'}</td>
          <td style="color:#f1f5f9; font-size:12.5px;">${iss.message}</td>
          <td style="color:#00f0ff; font-size:12px;">${iss.resolution || 'Inspect source record'}</td>
        </tr>
      `;
    }).join('');
  },

  renderRecordsSample(file) {
    const container = document.getElementById('raw-records-sample-body');
    const headContainer = document.getElementById('raw-records-sample-head');
    if (!container || !headContainer) return;

    const sample = file.parsed_records_sample || [];
    if (sample.length === 0) {
      headContainer.innerHTML = '<tr><th>No tabular records extracted</th></tr>';
      container.innerHTML = '<tr><td style="color:#64748b;">File contains no parsed records or is non-tabular.</td></tr>';
      return;
    }

    const headers = Object.keys(sample[0]);
    headContainer.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;

    container.innerHTML = sample.slice(0, 8).map(row => `
      <tr>
        ${headers.map(h => `<td class="cell-mono" style="font-size:11.5px;">${row[h] !== undefined ? row[h] : ''}</td>`).join('')}
      </tr>
    `).join('');
  },

  async triggerStandardize(fileId) {
    try {
      const res = await api.post(`/uploads/files/${fileId}/standardize`, {});
      alert(`Standardization complete! Converted ${res.standardized_count} records into canonical units with ${res.transformation_count} logged transformations.`);
      // Refresh
      if (this.currentBatch) {
        await this.loadBatch(this.currentBatch.id);
      }
    } catch (e) {
      alert('Standardization error: ' + e.message);
    }
  },
};
