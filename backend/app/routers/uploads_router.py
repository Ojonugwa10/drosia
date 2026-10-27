"""
Batch Upload, Automated Validation & Standardization Router for Drosia
Conforms to FR-02, FR-03, FR-04, Section 3 Stages 3, 4, 5, and Section 6
"""

import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from ..services.data_store import data_store
from ..services.validation_engine import validation_engine
from ..services.standardization import standardization_engine


router = APIRouter(prefix="/api/v1/uploads", tags=["Batch Upload & Validation"])


@router.post("")
async def create_upload_batch(
    project_id: str = Form(...),
    mission_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
):
    """
    Stage 3 & 4: Ingests batch of files, computes SHA-256, verifies content,
    runs automated multi-dimensional validation, and produces quality score & issue list.
    """
    actor = data_store.get_current_user()
    if actor["role"] not in ["pilot", "ops_manager", "analyst", "org_admin"]:
        raise HTTPException(status_code=403, detail="User role not authorized to upload mission data.")

    batch_id = f"ub-{uuid.uuid4().hex[:8]}"
    storage_dir = os.path.join(data_store.data_dir, batch_id)
    os.makedirs(storage_dir, exist_ok=True)

    known_checksums = [f["sha256_checksum"] for f in data_store.source_files]
    files_info = []

    for upload_file in files:
        content = await upload_file.read()
        file_id = f"src-{uuid.uuid4().hex[:8]}"

        # Calculate SHA-256
        sha256 = hashlib.sha256(content).hexdigest()

        # Save raw original in controlled private storage
        safe_filename = os.path.basename(upload_file.filename or "unknown_file")
        storage_path = os.path.join(storage_dir, f"{file_id}_{safe_filename}")
        with open(storage_path, "wb") as f_out:
            f_out.write(content)

        # Run automated multi-dimensional validation engine
        val_result = validation_engine.validate_file_content(
            filename=safe_filename,
            content=content,
            mime_type=upload_file.content_type or "application/octet-stream",
            known_checksums=known_checksums,
            sha256=sha256,
        )

        file_record = {
            "id": file_id,
            "upload_batch_id": batch_id,
            "original_filename": safe_filename,
            "media_type": upload_file.content_type or "application/octet-stream",
            "file_size_bytes": len(content),
            "sha256_checksum": sha256,
            "storage_key": storage_path,
            "parser_version": "v1.0.0",
            "validation_status": val_result["outcome"].value,
            "overall_quality_score": val_result["overall_score"],
            "quality_breakdown": val_result["quality_scores"],
            "error_count": val_result["error_count"],
            "warning_count": val_result["warning_count"],
            "validation_issues": val_result["issues"],
            "record_count": val_result["record_count"],
            "file_category": val_result["file_category"],
            "parsed_records_sample": val_result["parsed_records"],
            "is_standardized": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        files_info.append(file_record)
        known_checksums.append(sha256)

    batch = data_store.record_upload_batch(
        batch_id=batch_id,
        project_id=project_id,
        mission_id=mission_id,
        files_info=files_info,
        actor=actor,
    )

    return batch


@router.get("")
def list_upload_batches():
    return data_store.upload_batches


@router.get("/{batch_id}")
def get_batch_details(batch_id: str):
    for b in data_store.upload_batches:
        if b["id"] == batch_id:
            return b
    raise HTTPException(status_code=404, detail="Upload batch not found.")


@router.get("/files/{file_id}/quality-report")
def get_file_quality_report(file_id: str):
    for f in data_store.source_files:
        if f["id"] == file_id:
            return {
                "file_id": f["id"],
                "filename": f["original_filename"],
                "validation_status": f["validation_status"],
                "overall_quality_score": f.get("overall_quality_score", 100.0),
                "quality_breakdown": f.get("quality_breakdown", {}),
                "error_count": f.get("error_count", 0),
                "warning_count": f.get("warning_count", 0),
                "issues": f.get("validation_issues", []),
                "records_sample": f.get("parsed_records_sample", []),
            }
    raise HTTPException(status_code=404, detail="File not found.")


@router.post("/files/{file_id}/standardize")
def standardize_file_records(file_id: str):
    """
    Stage 5: Converts accepted source records into canonical schema,
    normalizes coordinates, altitudes, speeds, timestamps, and asset IDs.
    Preserves granular transformation history for complete auditability.
    """
    actor = data_store.get_current_user()
    if actor["role"] not in ["analyst", "ops_manager", "org_admin"]:
        raise HTTPException(status_code=403, detail="Role not authorized to perform data standardization.")

    target_file = None
    for f in data_store.source_files:
        if f["id"] == file_id:
            target_file = f
            break

    if not target_file:
        raise HTTPException(status_code=404, detail="File not found.")

    if target_file["validation_status"] == "Quarantined":
        raise HTTPException(status_code=400, detail="Cannot standardize quarantined file. Resolve critical errors first.")

    raw_sample = target_file.get("parsed_records_sample", [])
    standardized_records = []
    all_transform_logs = []

    for raw in raw_sample:
        canonical, logs = standardization_engine.standardize_telemetry_record(raw, actor_id=actor["id"])
        standardized_records.append(canonical)
        all_transform_logs.extend(logs)

    target_file["is_standardized"] = True
    target_file["canonical_records"] = standardized_records
    target_file["transformation_logs"] = all_transform_logs

    data_store.transformations.extend(all_transform_logs)
    data_store.save()

    return {
        "message": f"Successfully standardized {len(standardized_records)} records into canonical schema.",
        "file_id": file_id,
        "standardized_count": len(standardized_records),
        "transformation_count": len(all_transform_logs),
        "transformation_logs": all_transform_logs[:20],
    }
