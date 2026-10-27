"""
Data Store Service for Drosia: Central In-Memory & File-Persisted State Repository
Coordinates CRUD, data lineage linking, and transaction auditing across all entities
Conforms to Section 5 Canonical Data Model & Lineage Requirements
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .sample_data_generator import generate_initial_state, write_sample_csv_and_geojson_files
from .audit_service import audit_service


class DataStore:
    def __init__(self, data_dir: str = "data/storage"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.state_file = os.path.join(self.data_dir, "platform_state.json")

        self.organization: Dict[str, Any] = {}
        self.users: List[Dict[str, Any]] = []
        self.projects: List[Dict[str, Any]] = []
        self.assets: List[Dict[str, Any]] = []
        self.missions: List[Dict[str, Any]] = []
        self.telemetry_points: List[Dict[str, Any]] = []
        self.flight_tracks: List[Dict[str, Any]] = []
        self.media_assets: List[Dict[str, Any]] = []
        self.incidents: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, Any]] = []
        self.review_actions: List[Dict[str, Any]] = []
        self.reports: List[Dict[str, Any]] = []
        self.upload_batches: List[Dict[str, Any]] = []
        self.source_files: List[Dict[str, Any]] = []
        self.transformations: List[Dict[str, Any]] = []

        # Current active user session (simulated RBAC switchable role)
        self.current_user_id = "usr-ops-02"  # Defaults to Chukwuma Eze (Ops Manager)

        self.initialize()

    def initialize(self):
        """Loads state or initializes with realistic initial data."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.organization = data.get("organization", {})
                    self.users = data.get("users", [])
                    self.projects = data.get("projects", [])
                    self.assets = data.get("assets", [])
                    self.missions = data.get("missions", [])
                    self.telemetry_points = data.get("telemetry_points", [])
                    self.flight_tracks = data.get("flight_tracks", [])
                    self.media_assets = data.get("media_assets", [])
                    self.incidents = data.get("incidents", [])
                    self.findings = data.get("findings", [])
                    self.review_actions = data.get("review_actions", [])
                    self.reports = data.get("reports", [])
                    self.upload_batches = data.get("upload_batches", [])
                    self.source_files = data.get("source_files", [])
                    self.transformations = data.get("transformations", [])
                return
            except Exception:
                pass

        # Generate fresh initial state
        init_data = generate_initial_state()
        self.organization = init_data["organization"]
        self.users = init_data["users"]
        self.projects = init_data["projects"]
        self.assets = init_data["assets"]
        self.missions = init_data["missions"]
        self.telemetry_points = init_data["telemetry_points"]
        self.flight_tracks = init_data["flight_tracks"]
        self.media_assets = init_data["media_assets"]
        self.incidents = init_data["incidents"]
        self.findings = init_data["findings"]
        self.reports = init_data["reports"]

        # Write physical sample files for UI batch uploader
        write_sample_csv_and_geojson_files("frontend/assets/samples")

        # Initial audit log
        audit_service.record_event(
            organization_id=self.organization["id"],
            actor_id="usr-admin-01",
            actor_name="Babatunde Adeleke",
            actor_role="org_admin",
            action_type="SYSTEM_INITIALIZATION",
            resource_type="ORGANIZATION",
            resource_id=self.organization["id"],
            metadata={"system_version": "v1.0.0", "status": "Initialized canonical repositories"},
        )

        self.save()

    def save(self):
        try:
            state = {
                "organization": self.organization,
                "users": self.users,
                "projects": self.projects,
                "assets": self.assets,
                "missions": self.missions,
                "telemetry_points": self.telemetry_points,
                "flight_tracks": self.flight_tracks,
                "media_assets": self.media_assets,
                "incidents": self.incidents,
                "findings": self.findings,
                "review_actions": self.review_actions,
                "reports": self.reports,
                "upload_batches": self.upload_batches,
                "source_files": self.source_files,
                "transformations": self.transformations,
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving state: {e}")

    # RBAC User context
    def get_current_user(self) -> Dict[str, Any]:
        for u in self.users:
            if u["id"] == self.current_user_id:
                return u
        return self.users[0]

    def set_current_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        for u in self.users:
            if u["id"] == user_id:
                self.current_user_id = user_id
                audit_service.record_event(
                    organization_id=self.organization["id"],
                    actor_id=u["id"],
                    actor_name=u["display_name"],
                    actor_role=u["role"],
                    action_type="USER_ROLE_SWITCH",
                    resource_type="USER_SESSION",
                    resource_id=u["id"],
                    metadata={"new_role": u["role"]},
                )
                return u
        return None

    # Projects
    def list_projects(self) -> List[Dict[str, Any]]:
        return self.projects

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        for p in self.projects:
            if p["id"] == project_id:
                return p
        return None

    def create_project(self, payload: Dict[str, Any], actor: Dict[str, Any]) -> Dict[str, Any]:
        proj_id = f"proj-{uuid.uuid4().hex[:8]}"
        project = {
            "id": proj_id,
            "organization_id": self.organization["id"],
            "name": payload.get("name", "New Security Surveillance Project"),
            "project_type": payload.get("project_type", "Perimeter Surveillance"),
            "sensitivity_level": payload.get("sensitivity_level", "Official Sensitive"),
            "retention_days": int(payload.get("retention_days", 365)),
            "operating_area": payload.get("operating_area", "Nigeria"),
            "center": payload.get("center", [6.4253, 3.8614]),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.projects.append(project)
        audit_service.record_event(
            organization_id=self.organization["id"],
            actor_id=actor["id"],
            actor_name=actor["display_name"],
            actor_role=actor["role"],
            action_type="CREATE_PROJECT",
            resource_type="PROJECT",
            resource_id=proj_id,
            metadata={"project_name": project["name"]},
        )
        self.save()
        return project

    # Missions
    def list_missions(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if project_id:
            return [m for m in self.missions if m["project_id"] == project_id]
        return self.missions

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        for m in self.missions:
            if m["id"] == mission_id:
                return m
        return None

    def create_mission(self, payload: Dict[str, Any], actor: Dict[str, Any]) -> Dict[str, Any]:
        m_id = f"msn-{uuid.uuid4().hex[:8]}"
        mission = {
            "id": m_id,
            "project_id": payload.get("project_id", self.projects[0]["id"]),
            "mission_code": payload.get("mission_code", f"MSN-{uuid.uuid4().hex[:6].upper()}"),
            "mission_type": payload.get("mission_type", "Perimeter Surveillance"),
            "objective": payload.get("objective", "Standard security reconnaissance"),
            "planned_start_at": payload.get("planned_start_at"),
            "actual_start_at": payload.get("actual_start_at"),
            "actual_end_at": payload.get("actual_end_at"),
            "assigned_pilot_id": payload.get("assigned_pilot_id", "usr-pilot-03"),
            "assigned_pilot_name": payload.get("assigned_pilot_name", "Capt. Fatima Al-Hassan"),
            "asset_id": payload.get("asset_id", self.assets[0]["id"]),
            "asset_code": payload.get("asset_code", self.assets[0]["asset_code"]),
            "planned_route_waypoints": payload.get("planned_route_waypoints", []),
            "status": payload.get("status", "Planned"),
            "created_by": actor["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.missions.append(mission)
        audit_service.record_event(
            organization_id=self.organization["id"],
            actor_id=actor["id"],
            actor_name=actor["display_name"],
            actor_role=actor["role"],
            action_type="REGISTER_MISSION",
            resource_type="MISSION",
            resource_id=m_id,
            metadata={"mission_code": mission["mission_code"]},
        )
        self.save()
        return mission

    # Assets
    def list_assets(self) -> List[Dict[str, Any]]:
        return self.assets

    # Upload Batches & Source Files
    def record_upload_batch(
        self,
        batch_id: str,
        project_id: str,
        mission_id: Optional[str],
        files_info: List[Dict[str, Any]],
        actor: Dict[str, Any],
    ) -> Dict[str, Any]:
        batch = {
            "id": batch_id,
            "project_id": project_id,
            "mission_id": mission_id,
            "uploaded_by": actor["id"],
            "uploaded_by_name": actor["display_name"],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "status": "Validated",
            "processing_version": "v1.0.0",
            "file_count": len(files_info),
            "files": files_info,
        }
        self.upload_batches.append(batch)
        for f in files_info:
            self.source_files.append(f)

        audit_service.record_event(
            organization_id=self.organization["id"],
            actor_id=actor["id"],
            actor_name=actor["display_name"],
            actor_role=actor["role"],
            action_type="BATCH_DATA_UPLOAD",
            resource_type="UPLOAD_BATCH",
            resource_id=batch_id,
            metadata={"files_uploaded": len(files_info)},
        )
        self.save()
        return batch

    # Findings & Reviews
    def list_findings(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.findings

    def record_review_action(
        self,
        finding_id: str,
        decision: str,
        rationale: str,
        actor: Dict[str, Any],
    ) -> Dict[str, Any]:
        action_id = f"rev-{uuid.uuid4().hex[:8]}"
        prev_status = "Pending Review"
        new_status = decision

        for f in self.findings:
            if f["id"] == finding_id:
                prev_status = f.get("review_status", "Pending Review")
                f["review_status"] = decision
                if decision in ["Accept", "Verified Observation"]:
                    f["verification_status"] = "Verified Observation"
                elif decision == "Confirmed Threat":
                    f["verification_status"] = "Confirmed Threat"
                elif decision == "Reject":
                    f["verification_status"] = "False Alarm"
                break

        action = {
            "id": action_id,
            "finding_id": finding_id,
            "reviewer_id": actor["id"],
            "reviewer_name": actor["display_name"],
            "reviewer_role": actor["role"],
            "decision": decision,
            "rationale": rationale,
            "previous_status": prev_status,
            "new_status": new_status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.review_actions.append(action)

        audit_service.record_event(
            organization_id=self.organization["id"],
            actor_id=actor["id"],
            actor_name=actor["display_name"],
            actor_role=actor["role"],
            action_type="REVIEW_FINDING_DECISION",
            resource_type="FINDING",
            resource_id=finding_id,
            metadata={"decision": decision, "rationale": rationale},
        )
        self.save()
        return action

    # Reports & Approvals
    def list_reports(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if project_id:
            return [r for r in self.reports if r["project_id"] == project_id]
        return self.reports

    def create_report(self, payload: Dict[str, Any], actor: Dict[str, Any]) -> Dict[str, Any]:
        rep_id = f"rep-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        report = {
            "id": rep_id,
            "project_id": payload.get("project_id", self.projects[0]["id"]),
            "report_title": payload.get("report_title", "Security Surveillance Intelligence Report"),
            "report_type": payload.get("report_type", "Security Intelligence & Mission Summary"),
            "reporting_period_start": payload.get("reporting_period_start", now.isoformat()),
            "reporting_period_end": payload.get("reporting_period_end", now.isoformat()),
            "version_number": 1,
            "status": "Draft",
            "analysis_run_id": payload.get("analysis_run_id", "run-041-01"),
            "executive_summary": payload.get("executive_summary", "Operational summary pending."),
            "methodology_and_limitations": payload.get("methodology_and_limitations", "Conforms to EPSG:4326."),
            "findings_included": payload.get("findings_included", []),
            "storage_key": f"reports/{rep_id}_v1.json",
            "is_stale": False,
            "approved_by": None,
            "approved_by_name": None,
            "approved_at": None,
            "rejection_reason": None,
            "created_by": actor["id"],
            "created_at": now.isoformat(),
        }
        self.reports.append(report)
        audit_service.record_event(
            organization_id=self.organization["id"],
            actor_id=actor["id"],
            actor_name=actor["display_name"],
            actor_role=actor["role"],
            action_type="CREATE_DRAFT_REPORT",
            resource_type="REPORT",
            resource_id=rep_id,
            metadata={"report_title": report["report_title"]},
        )
        self.save()
        return report

    def update_report_status(
        self,
        report_id: str,
        new_status: str,
        actor: Dict[str, Any],
        rejection_reason: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        for r in self.reports:
            if r["id"] == report_id:
                prev_status = r["status"]
                r["status"] = new_status
                if new_status == "Approved":
                    r["approved_by"] = actor["id"]
                    r["approved_by_name"] = actor["display_name"]
                    r["approved_at"] = datetime.now(timezone.utc).isoformat()
                    r["rejection_reason"] = None
                elif new_status == "Rejected":
                    r["rejection_reason"] = rejection_reason

                audit_service.record_event(
                    organization_id=self.organization["id"],
                    actor_id=actor["id"],
                    actor_name=actor["display_name"],
                    actor_role=actor["role"],
                    action_type="REPORT_APPROVAL_TRANSITION",
                    resource_type="REPORT",
                    resource_id=report_id,
                    metadata={"from_status": prev_status, "to_status": new_status, "rejection_reason": rejection_reason},
                )
                self.save()
                return r
        return None


data_store = DataStore()
