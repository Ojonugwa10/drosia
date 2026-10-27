"""
Data Standardization & Canonical Transformation Engine for Drosia
Implements Section 3 Stage 5 and FR-04 Data Standardization
Maps heterogeneous source fields into canonical schema, preserves transformation provenance
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


class StandardizationEngine:
    def __init__(self):
        # Controlled taxonomy vocabulary mapping
        self.INCIDENT_CATEGORY_MAP = {
            "breach": "Perimeter Breach",
            "fence": "Perimeter Breach",
            "intrusion": "Perimeter Breach",
            "unauth_vehicle": "Unauthorized Vehicle",
            "vehicle": "Unauthorized Vehicle",
            "car": "Unauthorized Vehicle",
            "truck": "Unauthorized Vehicle",
            "hotspot": "Thermal Anomaly",
            "heat": "Thermal Anomaly",
            "thermal": "Thermal Anomaly",
            "tampering": "Infrastructure Tampering",
            "vandalism": "Infrastructure Tampering",
            "pipeline_leak": "Infrastructure Tampering",
            "object": "Unattended Object",
            "package": "Unattended Object",
            "loitering": "Suspicious Loitering",
            "trespassing": "Suspicious Loitering",
        }

        # Known asset normalization dictionary
        self.ASSET_CODE_MAP = {
            "m300": "UAV-M300-RTK-01",
            "matrice 300": "UAV-M300-RTK-01",
            "dji matrice 300": "UAV-M300-RTK-01",
            "mavic 3t": "UAV-M3T-THERMAL-02",
            "m3t": "UAV-M3T-THERMAL-02",
            "autel evo": "UAV-EVO2-SEC-03",
            "alpha-1": "UAV-M300-RTK-01",
            "alpha-2": "UAV-M3T-THERMAL-02",
        }

    def standardize_telemetry_record(
        self,
        raw_record: Dict[str, Any],
        actor_id: str = "system",
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Converts heterogeneous raw telemetry row into canonical TelemetryPoint dict.
        Returns (canonical_dict, list_of_transformation_logs).
        """
        transform_logs = []
        canonical = {}

        # 1. Coordinate normalization
        lat_raw = self._extract_first(raw_record, ["latitude", "lat", "lat_deg", "y"])
        lon_raw = self._extract_first(raw_record, ["longitude", "lon", "lng", "long_deg", "x"])

        if lat_raw is not None and lon_raw is not None:
            lat = float(lat_raw)
            lon = float(lon_raw)
            canonical["latitude"] = lat
            canonical["longitude"] = lon
            transform_logs.append({
                "source_field": "latitude/longitude",
                "original_value": f"{lat_raw}, {lon_raw}",
                "transformed_value": f"{lat}, {lon}",
                "rule": "Canonical Decimal Degrees (EPSG:4326)",
                "applied_at": datetime.utcnow().isoformat(),
                "actor": actor_id,
            })

        # 2. Altitude normalization to meters AGL
        alt_raw = self._extract_first(raw_record, ["altitude", "alt", "alt_m", "altitude_m", "height", "z"])
        alt_ft = self._extract_first(raw_record, ["alt_ft", "altitude_ft", "height_ft"])
        alt_ref = str(self._extract_first(raw_record, ["altitude_reference", "alt_ref", "datum"]) or "AGL").upper()

        if alt_raw is not None:
            alt_m = float(alt_raw)
        elif alt_ft is not None:
            alt_m = round(float(alt_ft) * 0.3048, 2)
            transform_logs.append({
                "source_field": "alt_ft",
                "original_value": f"{alt_ft} ft",
                "transformed_value": f"{alt_m} m",
                "rule": "Unit conversion ft -> m",
                "applied_at": datetime.utcnow().isoformat(),
                "actor": actor_id,
            })
        else:
            alt_m = 0.0

        canonical["altitude_value"] = round(alt_m, 2)
        canonical["altitude_reference"] = "AGL" if "AGL" in alt_ref else ("MSL" if "MSL" in alt_ref else "AGL")

        # 3. Speed normalization to m/s
        speed_raw = self._extract_first(raw_record, ["speed", "speed_ms", "ground_speed", "velocity"])
        speed_kmh = self._extract_first(raw_record, ["speed_kmh", "speed_kph"])
        speed_knots = self._extract_first(raw_record, ["speed_knots", "speed_kts"])

        if speed_raw is not None:
            speed_ms = float(speed_raw)
        elif speed_kmh is not None:
            speed_ms = round(float(speed_kmh) / 3.6, 2)
            transform_logs.append({
                "source_field": "speed_kmh",
                "original_value": f"{speed_kmh} km/h",
                "transformed_value": f"{speed_ms} m/s",
                "rule": "Unit conversion km/h -> m/s",
                "applied_at": datetime.utcnow().isoformat(),
                "actor": actor_id,
            })
        elif speed_knots is not None:
            speed_ms = round(float(speed_knots) * 0.514444, 2)
            transform_logs.append({
                "source_field": "speed_knots",
                "original_value": f"{speed_knots} kts",
                "transformed_value": f"{speed_ms} m/s",
                "rule": "Unit conversion knots -> m/s",
                "applied_at": datetime.utcnow().isoformat(),
                "actor": actor_id,
            })
        else:
            speed_ms = 0.0

        canonical["speed_value"] = max(0.0, round(speed_ms, 2))

        # 4. Heading
        heading_raw = self._extract_first(raw_record, ["heading", "yaw", "bearing", "course"])
        canonical["heading"] = round(float(heading_raw) % 360.0, 1) if heading_raw is not None else 0.0

        # 5. Timestamp to standard ISO UTC
        time_raw = self._extract_first(raw_record, ["timestamp", "time", "datetime", "observed_at", "utc_time"])
        if time_raw:
            try:
                # normalize to UTC string
                dt = datetime.fromisoformat(str(time_raw).replace("Z", "+00:00"))
                canonical["observed_at"] = dt.astimezone(timezone.utc).isoformat()
                transform_logs.append({
                    "source_field": "timestamp",
                    "original_value": str(time_raw),
                    "transformed_value": canonical["observed_at"],
                    "rule": "Standardized to ISO-8601 UTC with preserved original context",
                    "applied_at": datetime.utcnow().isoformat(),
                    "actor": actor_id,
                })
            except Exception:
                canonical["observed_at"] = str(time_raw)

        # 6. Battery Level
        batt_raw = self._extract_first(raw_record, ["battery", "battery_level", "battery_pct", "soc"])
        if batt_raw is not None:
            batt_val = float(str(batt_raw).replace("%", "").strip())
            canonical["battery_level"] = max(0.0, min(100.0, round(batt_val, 1)))

        return canonical, transform_logs

    def standardize_incident_category(self, raw_category: str) -> str:
        raw_lower = raw_category.lower().strip()
        for key, canonical_name in self.INCIDENT_CATEGORY_MAP.items():
            if key in raw_lower:
                return canonical_name
        return "Perimeter Breach"  # default fallback

    def normalize_asset_code(self, raw_asset: str) -> str:
        raw_lower = raw_asset.lower().strip()
        for key, canonical_code in self.ASSET_CODE_MAP.items():
            if key in raw_lower:
                return canonical_code
        return raw_asset.upper()

    def _extract_first(self, data: Dict[str, Any], candidates: List[str]) -> Optional[Any]:
        for k, v in data.items():
            cleaned_k = k.lower().strip()
            if cleaned_k in candidates and v != "" and v is not None:
                return v
        return None


standardization_engine = StandardizationEngine()
