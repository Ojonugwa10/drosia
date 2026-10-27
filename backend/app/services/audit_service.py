"""
Tamper-Evident Cryptographic Audit Service for Drosia
Implements append-only SHA-256 chained event logging
Conforms to FR-08, Section 5.1, and Section 10.4
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..models.domain import AuditEvent


class AuditService:
    def __init__(self):
        self._events: List[AuditEvent] = []
        self._genesis_hash = "0" * 64

    def _calculate_hash(self, previous_hash: str, payload: Dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        hasher = hashlib.sha256()
        hasher.update((previous_hash + serialized).encode("utf-8"))
        return hasher.hexdigest()

    def record_event(
        self,
        organization_id: str,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        action_type: str,
        resource_type: str,
        resource_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> AuditEvent:
        """
        Appends an immutable audit event with a cryptographic SHA-256 link to the previous record.
        """
        previous_hash = self._events[-1].event_hash if self._events else self._genesis_hash
        event_id = f"aud-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        req_id = request_id or f"req-{uuid.uuid4().hex[:8]}"

        payload = {
            "id": event_id,
            "organization_id": organization_id,
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_role": actor_role,
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "event_timestamp": now.isoformat(),
            "request_id": req_id,
            "metadata": metadata or {},
        }

        event_hash = self._calculate_hash(previous_hash, payload)

        event = AuditEvent(
            id=event_id,
            organization_id=organization_id,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            event_timestamp=now,
            request_id=req_id,
            previous_hash=previous_hash,
            event_hash=event_hash,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verifies the cryptographic chain integrity of all audit events.
        Detects any tampering, deletion, or silent modifications.
        """
        if not self._events:
            return {"valid": True, "total_events": 0, "status": "No events logged"}

        expected_prev = self._genesis_hash
        for i, event in enumerate(self._events):
            if event.previous_hash != expected_prev:
                return {
                    "valid": False,
                    "tampered_index": i,
                    "event_id": event.id,
                    "reason": "Previous hash pointer mismatch",
                }

            payload = {
                "id": event.id,
                "organization_id": event.organization_id,
                "actor_id": event.actor_id,
                "actor_name": event.actor_name,
                "actor_role": event.actor_role,
                "action_type": event.action_type,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "event_timestamp": event.event_timestamp.isoformat(),
                "request_id": event.request_id,
                "metadata": event.metadata,
            }
            computed_hash = self._calculate_hash(expected_prev, payload)
            if computed_hash != event.event_hash:
                return {
                    "valid": False,
                    "tampered_index": i,
                    "event_id": event.id,
                    "reason": "Event content cryptographic signature mismatch",
                }
            expected_prev = event.event_hash

        return {
            "valid": True,
            "total_events": len(self._events),
            "latest_checkpoint_hash": expected_prev,
            "status": "Chained cryptographic seal intact",
        }

    def list_events(
        self,
        actor_id: Optional[str] = None,
        action_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        filtered = self._events
        if actor_id:
            filtered = [e for e in filtered if e.actor_id == actor_id]
        if action_type:
            filtered = [e for e in filtered if e.action_type == action_type]
        if resource_type:
            filtered = [e for e in filtered if e.resource_type == resource_type]
        # Return newest first
        return list(reversed(filtered[-limit:]))


# Global Singleton for in-memory audit store
audit_service = AuditService()
