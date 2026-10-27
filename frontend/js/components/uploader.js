/**
 * Batch Data Upload & Pre-Flight Validation Component
 * Implements Stage 3 & 4 with real-time dropzone and sample dataset test loaders
 */

const uploader = {
  selectedFiles: [],

  init() {
    this.bindEvents();
    this.loadUploadHistory();
  },

  bindEvents() {
    const dropzone = document.getElementById('batch-upload-dropzone');
    const fileInput = document.getElementById('batch-file-input');
    const uploadBtn = document.getElementById('submit-upload-batch-btn');

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-active');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-active');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-active');
        if (e.dataTransfer.files.length) {
          this.handleFiles(Array.from(e.dataTransfer.files));
        }
      });

      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
          this.handleFiles(Array.from(e.target.files));
        }
      });
    }

    if (uploadBtn) {
      uploadBtn.addEventListener('click', () => this.submitBatch());
    }

    // Pre-packaged sample dataset loaders
    document.querySelectorAll('.btn-load-sample').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const sampleName = btn.getAttribute('data-sample');
        if (sampleName) {
          await this.loadPrepackagedSample(sampleName);
        }
      });
    });
  },

  handleFiles(files) {
    this.selectedFiles = [...this.selectedFiles, ...files];
    this.renderSelectedFiles();
  },

  renderSelectedFiles() {
    const container = document.getElementById('staged-files-list');
    const uploadBtn = document.getElementById('submit-upload-batch-btn');
    if (!container) return;

    if (this.selectedFiles.length === 0) {
      container.innerHTML = '<div style="color:#64748b; font-size:12px; text-align:center; padding:12px;">No files selected. Drag files above or click a pre-packaged sample below.</div>';
      if (uploadBtn) uploadBtn.style.display = 'none';
      return;
    }

    if (uploadBtn) uploadBtn.style.display = 'inline-flex';

    container.innerHTML = this.selectedFiles.map((f, i) => `
      <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.08); margin-bottom:6px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <svg style="width:16px; height:16px; color:#00f0ff;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
          <span style="font-weight:600; color:#fff; font-size:12.5px;">${f.name}</span>
          <span style="font-family:var(--font-mono); font-size:11px; color:#64748b;">(${(f.size / 1024).toFixed(1)} KB)</span>
        </div>
        <button onclick="uploader.removeFile(${i})" style="background:transparent; border:none; color:#ef4444; cursor:pointer; font-size:14px;">✕</button>
      </div>
    `).join('');
  },

  removeFile(index) {
    this.selectedFiles.splice(index, 1);
    this.renderSelectedFiles();
  },

  async loadPrepackagedSample(filename) {
    try {
      const resp = await fetch(`/assets/samples/${filename}`);
      if (!resp.ok) throw new Error('Could not fetch sample file');
      const blob = await resp.blob();
      const file = new File([blob], filename, { type: blob.type || 'text/csv' });
      this.handleFiles([file]);
    } catch (e) {
      alert('Error loading sample dataset: ' + e.message);
    }
  },

  async submitBatch() {
    if (this.selectedFiles.length === 0) return;

    const projId = store.state.currentProject ? store.state.currentProject.id : 'proj-lekki-01';
    const missionId = store.state.currentMission ? store.state.currentMission.id : 'msn-lekki-041';

    const formData = new FormData();
    formData.append('project_id', projId);
    if (missionId) formData.append('mission_id', missionId);

    this.selectedFiles.forEach(f => {
      formData.append('files', f);
    });

    const statusEl = document.getElementById('upload-status-indicator');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:#00f0ff;">Uploading & running automated multi-dimensional validation engine...</span>';
    }

    try {
      const res = await api.uploadFiles('/uploads', formData);
      this.selectedFiles = [];
      this.renderSelectedFiles();
      if (statusEl) {
        statusEl.innerHTML = `<span style="color:#10b981;">Batch ${res.id} processed! Validated ${res.file_count} file(s).</span>`;
      }
      this.loadUploadHistory();
      // Switch to Data Quality view to inspect issues
      navigation.switchView('data-quality');
      if (window.dataQuality) window.dataQuality.loadBatch(res.id);
    } catch (e) {
      if (statusEl) {
        statusEl.innerHTML = `<span style="color:#ef4444;">Upload error: ${e.message}</span>`;
      }
    }
  },

  async loadUploadHistory() {
    try {
      const batches = await api.get('/uploads');
      const container = document.getElementById('upload-history-table-body');
      if (!container) return;

      if (batches.length === 0) {
        container.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b;">No previous upload batches.</td></tr>';
        return;
      }

      container.innerHTML = batches.map(b => {
        const files = b.files || [];
        const hasQuarantine = files.some(f => f.validation_status === 'Quarantined');
        const hasWarning = files.some(f => f.validation_status === 'Accepted with Warnings');
        const badgeClass = hasQuarantine ? 'badge-quarantined' : (hasWarning ? 'badge-warnings' : 'badge-accepted');
        const statusText = hasQuarantine ? 'Quarantined' : (hasWarning ? 'Warnings' : 'Accepted');

        return `
          <tr>
            <td class="cell-mono" style="color:#00f0ff; font-weight:600;">${b.id}</td>
            <td>${files.map(f => f.original_filename).join(', ') || 'Dataset batch'}</td>
            <td>${files.length} file(s)</td>
            <td class="cell-mono">${b.uploaded_at.slice(0, 19).replace('T', ' ')}</td>
            <td><span class="badge-status ${badgeClass}">${statusText}</span></td>
            <td>
              <button class="btn-tactical btn-outline btn-sm" onclick="dataQuality.loadBatch('${b.id}'); navigation.switchView('data-quality');">
                Inspect Quality
              </button>
            </td>
          </tr>
        `;
      }).join('');
    } catch (e) {
      console.error('Error loading upload history:', e);
    }
  },
};
