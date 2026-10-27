"""
Findings & Human-in-the-Loop Review Router for Drosia
Conforms to FR-06, Section 3 Stages 8 & 9, and Section 8.6
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from ..services.data_store import data_store


router = APIRouter(prefix="/api/v1/findings", tags=["Findings & Review Workbench"])


class ReviewFindingRequest(BaseModel):
    decision: str  # Accept, Reject, Mark Inconclusive, Request More Evidence, Escalate to High Priority
    rationale: str


@router.get("")
def list_findings(project_id: Optional[str] = None):
    """Lists findings with supporting metrics, linked evidence assets, and current review status."""
    findings = data_store.list_findings(project_id)
    # Enrich with linked media details
    enriched = []
    for f in findings:
        f_copy = dict(f)
        media_list = []
        for ev_id in f.get("evidence_ids", []):
            for m in data_store.media_assets:
                if m["id"] == ev_id:
                    media_list.append(m)
        f_copy["media_evidence"] = media_list
        enriched.append(f_copy)
    return enriched


@router.post("/{finding_id}/review")
def submit_finding_review(finding_id: str, payload: ReviewFindingRequest):
    """
    Records an authorized human reviewer action on an analytical finding.
    Tracks reviewer ID, rationale, decision, and status transitions in immutable audit trail.
    """
    actor = data_store.get_current_user()
    if actor["role"] not in ["supervisor", "ops_manager", "analyst", "org_admin"]:
        raise HTTPException(status_code=403, detail="Role not authorized to record finding review decisions.")

    if not payload.rationale or len(payload.rationale.strip()) < 5:
        raise HTTPException(status_code=400, detail="A substantive rationale is required for finding review decisions.")

    action = data_store.record_review_action(
        finding_id=finding_id,
        decision=payload.decision,
        rationale=payload.rationale,
        actor=actor,
    )
    return action
