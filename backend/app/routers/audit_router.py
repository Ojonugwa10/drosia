"""
Audit Trail & Cryptographic Seal Integrity Router for Drosia
Conforms to FR-08, Section 5.1, and Section 10.4
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from ..services.data_store import data_store
from ..services.audit_service import audit_service


router = APIRouter(prefix="/api/v1/audit", tags=["Tamper-Evident Audit Trail"])


@router.get("/events")
def list_audit_events(
    actor_id: Optional[str] = None,
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = Query(default=100, le=500),
):
    """
    Retrieves the append-only audit event log.
    Accessible to Auditor, Org Admin, and Operations Manager.
    """
    actor = data_store.get_current_user()
    if actor["role"] not in ["auditor", "org_admin", "ops_manager"]:
        raise HTTPException(status_code=403, detail="Role not authorized to access audit records.")

    events = audit_service.list_events(
        actor_id=actor_id,
        action_type=action_type,
        resource_type=resource_type,
        limit=limit,
    )
    return events


@router.get("/verify-seal")
def verify_audit_seal():
    """
    Performs full cryptographic chain verification across all logged events.
    Checks SHA-256 hash chaining: if any entry was modified or deleted, verification fails immediately.
    """
    result = audit_service.verify_integrity()
    return result
