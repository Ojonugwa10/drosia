"""
Canonical Domain Models for Drosia: Drone Security Intelligence & Analytics Platform
Version 1.0 — Adheres to Section 5 Canonical Data Model
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    ORG_ADMIN = "org_admin"
    OPS_MANAGER = "ops_manager"
    PILOT = "pilot"
    ANALYST = "analyst"
    SUPERVISOR = "supervisor"
    MAINTENANCE = "maintenance"
    APPROVER = "approver"
    AUDITOR = "auditor"


class ProjectType(str, Enum):
    PERIMETER_SURVEILLANCE = "Perimeter Surveillance"
    PIPELINE_RECON = "Pipeline Reconnaissance"
    MARITIME_PORT = "Port & Maritime Security"
    CRITICAL_INFRASTRUCTURE = "Critical Infrastructure Protection"
    BORDER_PATROL = "Border & Corridor Patrol"


class SensitivityLevel(str, Enum):
    UNCLASSIFIED = "Unclassified"
    OFFICIAL_SENSITIVE = "Official Sensitive"
    CONFIDENTIAL = "Confidential"
    RESTRICTED = "Restricted"


class MissionStatus(str, Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ABORTED = "Aborted"
    CANCELLED = "Cancelled"


class ValidationOutcome(str, Enum):
    ACCEPTED = "Accepted"
    ACCEPTED_WITH_WARNINGS = "Accepted with Warnings"
    QUARANTINED = "Quarantined"


class QualityDimension(str, Enum):
    COMPLETENESS = "Completeness"
    VALIDITY = "Validity"
    CONSISTENCY = "Consistency"
    UNIQUENESS = "Uniqueness"
    TIMELINESS = "Timeliness"
    GEOSPATIAL_RELIABILITY = "Geospatial Reliability"
    PROVENANCE = "Provenance"


class IncidentCategory(str, Enum):
    PERIMETER_BREACH = "Perimeter Breach"
    UNAUTHORIZED_VEHICLE = "Unauthorized Vehicle"
    THERMAL_ANOMALY = "Thermal Anomaly"
    INFRASTRUCTURE_TAMPERING = "Infrastructure Tampering"
    UNATTENDED_OBJECT = "Unattended Object"
    SUSPICIOUS_LOITERING = "Suspicious Loitering"
    EQUIPMENT_MALFUNCTION = "Sensor/Equipment Warning"


class VerificationStatus(str, Enum):
    UNVERIFIED = "Unverified"
    VERIFIED = "Verified Observation"
    FALSE_ALARM = "False Alarm"
    CONFIRMED_THREAT = "Confirmed Threat"


class IncidentSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ReviewDecision(str, Enum):
    ACCEPT = "Accept"
    REJECT = "Reject"
    INCONCLUSIVE = "Mark Inconclusive"
    REQUEST_MORE_EVIDENCE = "Request More Evidence"
    ESCALATE = "Escalate to High Priority"


class ReportStatus(str, Enum):
    DRAFT = "Draft"
    VALIDATION = "Validation"
    REVIEW = "Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    REJECTED = "Rejected"


# ---------------------------------------------------------------------------
# Core Entities
# ---------------------------------------------------------------------------

class User(BaseModel):
    id: str
    organization_id: str
    display_name: str
    email: str
    role: UserRole
    status: str = "Active"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Organization(BaseModel):
    id: str
    name: str
    status: str = "Active"
    jurisdiction: str = "Nigeria / West Africa"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(BaseModel):
    id: str
    organization_id: str
    name: str
    project_type: ProjectType
    sensitivity_level: SensitivityLevel
    retention_days: int = 365
    operating_area: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Asset(BaseModel):
    id: str
    organization_id: str
    asset_code: str
    manufacturer: str
    model: str
    asset_type: str = "UAV Quadcopter"
    serial_reference: str
    status: str = "Active"
    total_flight_hours: float = 0.0
    last_service_date: Optional[str] = None


class Mission(BaseModel):
    id: str
    project_id: str
    mission_code: str
    mission_type: str
    objective: str
    planned_start_at: Optional[datetime] = None
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    assigned_pilot_id: str
    assigned_pilot_name: str
    asset_id: str
    asset_code: str
    planned_route_waypoints: List[Dict[str, Any]] = []
    status: MissionStatus = MissionStatus.PLANNED
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TelemetryPoint(BaseModel):
    id: str
    mission_id: str
    asset_id: str
    observed_at: datetime
    latitude: float
    longitude: float
    altitude_value: float  # in meters
    altitude_reference: str = "AGL"  # AGL, MSL, HOME
    speed_value: float  # in m/s
    heading: float = 0.0  # degrees
    battery_level: Optional[float] = None  # percentage 0-100
    source_record_id: Optional[str] = None


class FlightTrack(BaseModel):
    id: str
    mission_id: str
    asset_id: str
    source_file_id: Optional[str] = None
    coordinate_reference_system: str = "EPSG:4326"
    start_at: datetime
    end_at: datetime
    total_distance_km: float
    max_speed_ms: float
    avg_speed_ms: float
    max_altitude_m: float
    track_geometry: List[List[float]] = []  # [[lng, lat, alt], ...]
    data_quality_status: str = "Verified"


class MediaAsset(BaseModel):
    id: str
    mission_id: str
    source_file_id: Optional[str] = None
    original_filename: str
    captured_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None
    media_type: str = "image/jpeg"
    sensor_type: str = "Optical Zoom 4K"
    storage_path: str
    thumbnail_path: Optional[str] = None
    integrity_status: str = "Verified"
    metadata_json: Dict[str, Any] = {}


class Incident(BaseModel):
    id: str
    project_id: str
    mission_id: Optional[str] = None
    category: IncidentCategory
    description: str
    observed_at: datetime
    latitude: float
    longitude: float
    altitude_m: Optional[float] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    evidence_links: List[str] = []  # media asset IDs or source file IDs


class Finding(BaseModel):
    id: str
    analysis_run_id: str
    finding_type: str
    summary: str
    detailed_explanation: str
    supporting_metrics: Dict[str, Any] = {}
    evidence_ids: List[str] = []
    geographic_context: Optional[Dict[str, Any]] = None
    uncertainty_information: str
    data_quality_limitations: str
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    review_status: str = "Pending Review"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewAction(BaseModel):
    id: str
    finding_id: str
    reviewer_id: str
    reviewer_name: str
    decision: ReviewDecision
    rationale: str
    previous_status: str
    new_status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Report(BaseModel):
    id: str
    project_id: str
    report_title: str
    report_type: str = "Security Intelligence & Mission Summary"
    reporting_period_start: datetime
    reporting_period_end: datetime
    version_number: int = 1
    status: ReportStatus = ReportStatus.DRAFT
    analysis_run_id: Optional[str] = None
    executive_summary: str
    methodology_and_limitations: str
    findings_included: List[str] = []
    storage_key: Optional[str] = None
    is_stale: bool = False
    approved_by: Optional[str] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UploadBatch(BaseModel):
    id: str
    project_id: str
    mission_id: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "Processing"
    processing_version: str = "v1.0.0"
    file_count: int = 0
    files: List[Dict[str, Any]] = []


class SourceFile(BaseModel):
    id: str
    upload_batch_id: str
    original_filename: str
    media_type: str
    file_size_bytes: int
    sha256_checksum: str
    storage_key: str
    parser_version: str = "1.0.0"
    validation_status: ValidationOutcome
    quality_score: float = 100.0
    quality_breakdown: Dict[str, float] = {}
    error_count: int = 0
    warning_count: int = 0
    validation_issues: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(BaseModel):
    id: str
    organization_id: str
    actor_id: str
    actor_name: str
    actor_role: str
    action_type: str
    resource_type: str
    resource_id: str
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
    previous_hash: str
    event_hash: str
    metadata: Dict[str, Any] = {}
