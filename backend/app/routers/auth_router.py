"""
Authentication & Role-Based Access Control (RBAC) Router for Drosia
Conforms to FR-01 and Section 2
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
from ..services.data_store import data_store


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & RBAC"])


class SwitchRoleRequest(BaseModel):
    user_id: str


@router.get("/me")
def get_current_user_context():
    """Returns the currently active user, organization, and permitted RBAC capabilities."""
    user = data_store.get_current_user()
    org = data_store.organization
    role = user.get("role", "ops_manager")

    # Granular capability matrix based on Section 2
    capabilities = {
        "can_manage_users": role == "org_admin",
        "can_create_projects": role in ["org_admin", "ops_manager"],
        "can_create_missions": role in ["org_admin", "ops_manager", "pilot"],
        "can_upload_files": role in ["pilot", "ops_manager", "analyst"],
        "can_standardize_data": role in ["analyst", "ops_manager"],
        "can_review_incidents": role in ["supervisor", "ops_manager", "analyst"],
        "can_inspect_maintenance": role in ["maintenance", "ops_manager"],
        "can_approve_reports": role in ["approver", "org_admin"],
        "can_view_audit_trail": role in ["auditor", "org_admin", "ops_manager"],
    }

    return {
        "user": user,
        "organization": org,
        "capabilities": capabilities,
    }


@router.get("/users")
def list_available_users():
    """Lists all users across the 8 distinct organizational roles for interactive role switching."""
    return data_store.users


@router.post("/switch-role")
def switch_active_role(payload: SwitchRoleRequest):
    """Switches the active session user to test and demonstrate RBAC permission enforcement."""
    switched = data_store.set_current_user(payload.user_id)
    if not switched:
        raise HTTPException(status_code=404, detail="User ID not found in organization directory.")
    return {
        "message": f"Active role switched to {switched['role']} ({switched['display_name']})",
        "user": switched,
    }
