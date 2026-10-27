# Drosia — Drone Security Intelligence & Analytics Platform
## Implementation Blueprint & Operational System Guide — Version 1.0

**Drosia** is an aerospace/defense-grade intelligence platform engineered to transform heterogeneous drone-operation data (flight logs, GPS telemetry, incident logs, GIS corridors, and multi-spectral sensor imagery) into validated, explainable, and auditable operational intelligence.

---

## 1. Quick Start & Execution

The platform is running locally at **[http://localhost:8000](http://localhost:8000)**.

To restart the server at any time on Windows:
```cmd
run_platform.bat
```
Or directly using Python:
```powershell
py backend\run.py
```

---

## 2. Platform Architecture & Blueprint Mapping

The implementation directly fulfills every section and requirement of the **Version 1.0 Blueprint**:

```
drosia/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint & static mounts
│   │   ├── models/
│   │   │   └── domain.py               # Canonical Pydantic schemas (Section 5 model)
│   │   ├── services/
│   │   │   ├── audit_service.py        # Append-only SHA-256 chained audit ledger (FR-08)
│   │   │   ├── validation_engine.py    # 7-dimensional data quality scorer & QA rules (FR-03, Sec 6)
│   │   │   ├── standardization.py      # Canonical schema mapper & unit converter (FR-04)
│   │   │   ├── analytics_engine.py     # Deterministic KPIs, route deviation, fleet health (FR-05)
│   │   │   ├── explanation_engine.py   # Grounded AI operational explanations (FR-06)
│   │   │   ├── data_store.py           # Relational repository with JSON persistence
│   │   │   └── sample_data_generator.py# Realistic Nigerian surveillance datasets & test fixtures
│   │   └── routers/
│   │       ├── auth_router.py          # RBAC & interactive role switcher HUD (FR-01, Sec 2)
│   │       ├── projects_router.py      # Projects, missions & fleet assets (Sec 3 Stage 1 & 2)
│   │       ├── uploads_router.py       # Multi-file batch uploader & QA engine (FR-02)
│   │       ├── analytics_router.py     # Operational KPIs & GIS layers (Sec 7, Sec 8.4)
│   │       ├── findings_router.py      # Human-in-the-loop review workbench (Sec 3 Stage 8 & 9)
│   │       ├── reports_router.py       # Multi-stage report approval & PDF export (FR-07)
│   │       └── audit_router.py         # Cryptographic seal verification & export (Sec 10.4)
│   └── run.py                          # Dedicated server runner
├── frontend/
│   ├── index.html                      # Tactical Single-Page Application
│   ├── css/
│   │   ├── variables.css               # Design tokens, obsidian dark theme, cyan glow
│   │   ├── layout.css                  # HUD header, responsive sidebar, viewport
│   │   ├── components.css              # Metric tiles, tables, dropzone, badges, modals
│   │   ├── map.css                     # Tactical GIS HUD overlay & custom pulsing beacons
│   │   └── report.css                  # Executive intelligence document & print-to-PDF styles
│   ├── js/
│   │   ├── api.js                      # REST API client
│   │   ├── store.js                    # Reactive client state
│   │   ├── components/                 # UI components
│   │   └── app.js                      # Bootstrap loader
│   └── assets/
│       ├── images/                     # Authentic 4K optical and thermal FLIR drone evidence
│       └── samples/                    # 4 pre-packaged realistic test datasets
└── run_platform.bat                    # One-click Windows launcher
```

---

## 3. Key Feature Walkthrough

### 3.1 Role-Based Access Control (RBAC) Switcher
Click the user badge in the top right header (`Chukwuma Eze / OPS MANAGER`) to toggle between the **8 distinct organizational roles** defined in Section 2:
1. **Organization Administrator** (`org_admin`) — Manage projects, users, and organizational settings.
2. **Operations Manager** (`ops_manager`) — Mission dispatch, fleet readiness, review assignments.
3. **Drone Pilot** (`pilot`) — Upload flight records, correct telemetry anomalies.
4. **Data Analyst** (`analyst`) — Clean datasets, execute canonical standardization.
5. **Security Supervisor** (`supervisor`) — Review queue, verify observations, escalate threats.
6. **Maintenance Specialist** (`maintenance`) — Monitor battery degradation curves and flight hours.
7. **Report Approver** (`approver`) — Formal report sign-off and publication.
8. **Auditor** (`auditor`) — Inspect immutable cryptographic audit records.

### 3.2 Tactical GIS Map HUD
- **Leaflet Dark Basemap** centered on critical infrastructure facilities (e.g. Lekki Free Trade Zone perimeter).
- **Flown GPS Flight Tracks**: Colored cyan line rendered from 120 recorded telemetry points.
- **Planned Route Corridor**: Dashed amber corridor with waypoint altitude marks.
- **Incident Markers**: Pulsing beacon pins indicating High/Critical security events. Clicking a marker reveals the attached **4K Optical Zoom** or **Thermal Infrared (FLIR)** sensor capture with GPS and timestamp metadata.
- **Floating Telemetry HUD**: Real-time readouts of Latitude, Longitude, Altitude AGL, Ground Speed, and Battery SOC.

### 3.3 Batch Upload & Automated Data Quality Engine
- Drag-and-drop batch ingestion supporting CSV, JSON, GeoJSON, and Imagery files.
- **Cryptographic SHA-256 Checksums** calculated per file to detect duplicate uploads.
- **7-Dimensional Data Quality Radar**:
  * Completeness (Missing columns, empty files)
  * Validity (Coordinate bounds `[-90, 90]`, battery `0-100%`)
  * Consistency (Chronological timestamp ordering, speed anomalies `> 45 m/s`)
  * Uniqueness (Duplicate telemetry epochs)
  * Timeliness (Logging latency and gaps)
  * Geospatial Reliability (EPSG:4326 compliance, valid coordinates)
  * Provenance (Lineage linking back to raw upload)
- **Tri-State Validation Outcomes**: *Accepted*, *Accepted with Warnings*, or *Quarantined*.
- **Pre-packaged sample datasets** available in the UI for instant testing:
  * `telemetry_mission_lekki_perimeter.csv` (Valid drone flight log)
  * `incidents_lekki_perimeter.csv` (Perimeter breach & thermal hotspot log)
  * `planned_route_lekki_corridor.geojson` (Planned GIS corridor)
  * `corrupted_sample_for_qa_testing.csv` (Demonstrates automated quarantine on invalid coordinates & time regressions)

### 3.4 Canonical Standardization
- 1-click execution to normalize coordinates into canonical WGS-84 decimal degrees, convert speeds (km/h & knots to m/s), altitudes (feet to meters AGL), and standardize timestamps to ISO UTC.
- Preserves raw originals in storage; logs every transformation with source field, old value, transformed value, rule applied, timestamp, and actor.

### 3.5 Human-in-the-Loop Review Workbench
- Reviewer actions: **Accept Finding**, **Escalate Threat**, **Reject (False Alarm)**, or **Request More Evidence**.
- Enforces mandatory substantive review rationale for every status change, recording reviewer ID and timestamp into the audit trail.

### 3.6 Evidence-Grounded AI Operational Explanations
- Adheres to the Section 7 Module F requirement: AI explains validated deterministic calculations rather than hallucinating them.
- Formulates plain-language intelligence briefings citing exact numerical figures and linked evidence IDs.
- Cites mandatory data quality limitations: *"Track coverage confirms aircraft presence only; optical ground occlusion factors (trees/berms) remain documented."*

### 3.7 Executive Report Builder & Printable PDF Export
- Manages multi-stage lifecycle: **Draft → Validation → Review → Approved → Published**.
- Displays official classification banner (`OFFICIAL SENSITIVE // RESTRICTED`), executive summary, findings gallery, evidence photos, sensor metadata, and formal approver sign-off block.
- **Print / Export PDF**: Click button to invoke browser print styles configured specifically for executive document layouts.

### 3.8 Tamper-Evident Cryptographic Audit Trail
- Every critical event (initialization, role switch, batch upload, review decision, report sign-off) is chained using SHA-256 hash pointers (`previous_hash` + `event_payload` -> `event_hash`).
- Click **"Verify Cryptographic Seal"** to run an automated integrity check verifying that no audit log entry has been retroactively altered or deleted.
