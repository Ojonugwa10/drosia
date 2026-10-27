"""
Projects, Missions & Fleet Assets Router for Drosia
Conforms to FR-01, Section 3 Stages 1 & 2, and Section 5
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from ..services.data_store import data_store


router = APIRouter(prefix="/api/v1", tags=["Projects & Missions"])


class CreateProjectRequest(BaseModel):
    name: str
    project_type: str = "Perimeter Surveillance"
    sensitivity_level: str = "Official Sensitive"
    retention_days: int = 365
    operating_area: str = "Nigeria"


class CreateMissionRequest(BaseModel):
    project_id: str
    mission_code: str
    mission_type: str = "Perimeter Surveillance"
    objective: str
    planned_start_at: Optional[str] = None
    assigned_pilot_id: Optional[str] = "usr-pilot-03"
    assigned_pilot_name: Optional[str] = "Capt. Fatima Al-Hassan"
    asset_id: Optional[str] = None
    planned_route_waypoints: Optional[List[Dict[str, Any]]] = []


@router.get("/projects")
def list_projects():
    return data_store.list_projects()


@router.get("/projects/{project_id}")
def get_project_details(project_id: str):
    p = data_store.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found.")
    return p


@router.post("/projects")
def create_project(payload: CreateProjectRequest):
    actor = data_store.get_current_user()
    if actor["role"] not in ["org_admin", "ops_manager"]:
        raise HTTPException(status_code=403, detail="Only Organization Admins and Operations Managers may create projects.")
    created = data_store.create_project(payload.dict(), actor)
    return created


@router.get("/missions")
def list_missions(project_id: Optional[str] = None):
    return data_store.list_missions(project_id)


@router.get("/missions/{mission_id}")
def get_mission_details(mission_id: str):
    m = data_store.get_mission(mission_id)
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found.")
    return m


@router.post("/missions")
def create_mission(payload: CreateMissionRequest):
    actor = data_store.get_current_user()
    if actor["role"] not in ["org_admin", "ops_manager", "pilot"]:
        raise HTTPException(status_code=403, detail="User lacks permission to register missions.")
    created = data_store.create_mission(payload.dict(), actor)
    return created


@router.get("/assets")
def list_assets():
    return data_store.list_assets()
