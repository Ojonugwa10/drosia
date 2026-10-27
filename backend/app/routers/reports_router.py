"""
Report Generation, Multi-Stage Approval & Export Router for Drosia
Conforms to FR-07, Section 3 Stage 10, and Section 8.7
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from ..services.data_store import data_store


router = APIRouter(prefix="/api/v1/reports", tags=["Reports & Approval Workflow"])


class CreateReportRequest(BaseModel):
    project_id: str
    report_title: str
    report_type: str = "Security Intelligence & Mission Summary"
    executive_summary: Optional[str] = None
    methodology_and_limitations: Optional[str] = None
    findings_included: Optional[List[str]] = []


class TransitionReportRequest(BaseModel):
    new_status: str  # Draft, Validation, Review, Approved, Published, Rejected
    rejection_reason: Optional[str] = None


@router.get("")
def list_reports(project_id: Optional[str] = None):
    return data_store.list_reports(project_id)


@router.get("/{report_id}")
def get_report_details(report_id: str):
    for r in data_store.reports:
        if r["id"] == report_id:
            # Enrich with findings and linked evidence images
            enriched = dict(r)
            finding_details = []
            for fid in r.get("findings_included", []):
                for f in data_store.findings:
                    if f["id"] == fid:
                        f_copy = dict(f)
                        media_list = []
                        for mid in f.get("evidence_ids", []):
                            for m in data_store.media_assets:
                                if m["id"] == mid:
                                    media_list.append(m)
                        f_copy["media_evidence"] = media_list
                        finding_details.append(f_copy)
            enriched["detailed_findings"] = finding_details
            return enriched
    raise HTTPException(status_code=404, detail="Report not found.")


@router.post("")
def create_report(payload: CreateReportRequest):
    actor = data_store.get_current_user()
    if actor["role"] not in ["ops_manager", "analyst", "org_admin"]:
        raise HTTPException(status_code=403, detail="Role not authorized to compile reports.")

    report = data_store.create_report(payload.dict(), actor)
    return report


@router.post("/{report_id}/transition")
def transition_report_status(report_id: str, payload: TransitionReportRequest):
    """
    Manages report lifecycle state transitions:
    Draft -> Validation -> Review -> Approved -> Published.
    Enforces strict role permissions: only 'approver' or 'org_admin' may approve.
    """
    actor = data_store.get_current_user()

    if payload.new_status in ["Approved", "Published"]:
        if actor["role"] not in ["approver", "org_admin"]:
            raise HTTPException(
                status_code=403,
                detail=f"User role '{actor['role']}' is not authorized to approve reports. Requires 'approver' or 'org_admin' role.",
            )

    updated = data_store.update_report_status(
        report_id=report_id,
        new_status=payload.new_status,
        actor=actor,
        rejection_reason=payload.rejection_reason,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found.")

    return updated
