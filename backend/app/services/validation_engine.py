"""
Automated Data Quality & Validation Engine for Drosia
Implements Section 6 Multi-Dimensional Quality Scoring and Detailed Error Inspection
Conforms to FR-03, Section 3 Stage 4, and Section 6
"""

import csv
import io
import json
import math
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from ..models.domain import ValidationOutcome, QualityDimension


class ValidationEngine:
    def __init__(self):
        # Configurable thresholds
        self.MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
        self.MAX_DRONE_SPEED_MS = 45.0  # ~162 km/h max plausible speed for tactical multirotor
        self.MAX_TELEMETRY_GAP_SEC = 10.0  # gap threshold to flag
        self.REQUIRED_FLIGHT_LOG_FIELDS = ["timestamp", "latitude", "longitude", "altitude_m"]
        self.REQUIRED_INCIDENT_FIELDS = ["observed_at", "category", "description", "latitude", "longitude"]

    def validate_file_content(
        self,
        filename: str,
        content: bytes,
        mime_type: str,
        known_checksums: List[str],
        sha256: str,
    ) -> Dict[str, Any]:
        """
        Runs comprehensive multi-dimensional file and content validation.
        Returns outcome, dimensional quality scores, and granular issue list.
        """
        issues: List[Dict[str, Any]] = []
        quality_scores: Dict[str, float] = {
            QualityDimension.COMPLETENESS.value: 100.0,
            QualityDimension.VALIDITY.value: 100.0,
            QualityDimension.CONSISTENCY.value: 100.0,
            QualityDimension.UNIQUENESS.value: 100.0,
            QualityDimension.TIMELINESS.value: 100.0,
            QualityDimension.GEOSPATIAL_RELIABILITY.value: 100.0,
            QualityDimension.PROVENANCE.value: 100.0,
        }

        # 1. File-level checks
        if len(content) > self.MAX_FILE_SIZE_BYTES:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.VALIDITY.value,
                "message": f"File size ({len(content)} bytes) exceeds maximum configured limit (50MB).",
                "resolution": "Compress or split file before batch upload.",
            })
            quality_scores[QualityDimension.VALIDITY.value] -= 50

        if sha256 in known_checksums:
            issues.append({
                "severity": "WARNING",
                "dimension": QualityDimension.UNIQUENESS.value,
                "message": "Duplicate file checksum detected. This file content was previously uploaded.",
                "resolution": "Verify if this mission was already processed to avoid double-counting.",
            })
            quality_scores[QualityDimension.UNIQUENESS.value] -= 30

        # Determine file type by extension and content
        lower_name = filename.lower()
        parsed_records = []
        file_category = "unknown"

        if lower_name.endswith(".csv") or "csv" in mime_type:
            file_category = "csv"
            parsed_records, csv_issues = self._validate_csv(content)
            issues.extend(csv_issues)
        elif lower_name.endswith(".json") or lower_name.endswith(".geojson"):
            file_category = "json_gis"
            parsed_records, json_issues = self._validate_json_or_geojson(content)
            issues.extend(json_issues)
        elif lower_name.endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
            file_category = "imagery"
            img_issues = self._validate_image_metadata(filename, content)
            issues.extend(img_issues)
        else:
            issues.append({
                "severity": "WARNING",
                "dimension": QualityDimension.VALIDITY.value,
                "message": f"Unrecognized file extension for '{filename}'. Allowed: CSV, JSON, GeoJSON, JPEG, PNG, TIFF.",
                "resolution": "Check file format against supported parser schemas.",
            })
            quality_scores[QualityDimension.VALIDITY.value] -= 20

        # Calculate dimensional score impacts from issues
        for issue in issues:
            sev = issue.get("severity", "INFO")
            dim = issue.get("dimension", QualityDimension.VALIDITY.value)
            penalty = 25.0 if sev == "CRITICAL" else (10.0 if sev == "WARNING" else 2.0)
            if dim in quality_scores:
                quality_scores[dim] = max(0.0, quality_scores[dim] - penalty)

        overall_score = round(sum(quality_scores.values()) / len(quality_scores), 1)

        critical_count = sum(1 for i in issues if i["severity"] == "CRITICAL")
        warning_count = sum(1 for i in issues if i["severity"] == "WARNING")

        if critical_count > 0:
            outcome = ValidationOutcome.QUARANTINED
        elif warning_count > 0 or overall_score < 85.0:
            outcome = ValidationOutcome.ACCEPTED_WITH_WARNINGS
        else:
            outcome = ValidationOutcome.ACCEPTED

        return {
            "outcome": outcome,
            "overall_score": overall_score,
            "quality_scores": quality_scores,
            "issues": issues,
            "error_count": critical_count,
            "warning_count": warning_count,
            "file_category": file_category,
            "record_count": len(parsed_records),
            "parsed_records": parsed_records[:500],  # sample for inspection
        }

    def _validate_csv(self, content: bytes) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        issues = []
        records = []
        try:
            text = content.decode("utf-8-sig", errors="replace")
        except Exception as e:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.VALIDITY.value,
                "message": f"Unable to decode CSV text: {str(e)}",
                "resolution": "Ensure file is UTF-8 encoded text.",
            })
            return records, issues

        lines = text.strip().splitlines()
        if not lines:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.COMPLETENESS.value,
                "message": "CSV file is empty.",
                "resolution": "Upload a file containing tabular data with headers.",
            })
            return records, issues

        reader = csv.DictReader(lines)
        if not reader.fieldnames:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.COMPLETENESS.value,
                "message": "CSV file does not contain a valid header row.",
                "resolution": "Ensure first row contains column headers.",
            })
            return records, issues

        headers = [h.strip().lower() for h in reader.fieldnames if h]

        # Detect flight log schema vs incident schema vs generic
        is_telemetry = any(h in headers for h in ["lat", "latitude", "lng", "lon", "longitude", "alt", "altitude", "altitude_m"])
        has_time = any(h in headers for h in ["timestamp", "time", "datetime", "observed_at", "utc_time"])

        if is_telemetry and not has_time:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.COMPLETENESS.value,
                "message": "Telemetry file is missing a required timestamp column.",
                "resolution": "Add UTC or local timestamp column to telemetry records.",
            })

        prev_time = None
        prev_lat = None
        prev_lon = None
        seen_timestamps = set()

        for row_idx, row in enumerate(reader, start=2):  # line 2 is first data row
            cleaned_row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
            records.append(cleaned_row)

            # Check lat/lon if present
            lat_val = cleaned_row.get("latitude") or cleaned_row.get("lat")
            lon_val = cleaned_row.get("longitude") or cleaned_row.get("lon") or cleaned_row.get("lng")
            if lat_val and lon_val:
                try:
                    lat_f = float(lat_val)
                    lon_f = float(lon_val)
                    if not (-90.0 <= lat_f <= 90.0):
                        issues.append({
                            "severity": "CRITICAL",
                            "dimension": QualityDimension.GEOSPATIAL_RELIABILITY.value,
                            "row": row_idx,
                            "message": f"Row {row_idx}: Latitude {lat_f} is out of valid range [-90, 90].",
                            "resolution": "Correct coordinate value in source dataset.",
                        })
                    if not (-180.0 <= lon_f <= 180.0):
                        issues.append({
                            "severity": "CRITICAL",
                            "dimension": QualityDimension.GEOSPATIAL_RELIABILITY.value,
                            "row": row_idx,
                            "message": f"Row {row_idx}: Longitude {lon_f} is out of valid range [-180, 180].",
                            "resolution": "Correct coordinate value in source dataset.",
                        })

                    # Implausible movement jump check
                    if prev_lat is not None and prev_lon is not None and prev_time is not None:
                        # rough distance
                        d_lat = (lat_f - prev_lat) * 111000.0
                        d_lon = (lon_f - prev_lon) * 111000.0 * math.cos(math.radians(lat_f))
                        dist_m = math.sqrt(d_lat * d_lat + d_lon * d_lon)
                        time_val = cleaned_row.get("timestamp") or cleaned_row.get("time") or cleaned_row.get("datetime")
                        if time_val:
                            try:
                                curr_t = self._parse_iso_or_common(time_val)
                                dt_sec = (curr_t - prev_time).total_seconds()
                                if dt_sec > 0:
                                    speed = dist_m / dt_sec
                                    if speed > self.MAX_DRONE_SPEED_MS:
                                        issues.append({
                                            "severity": "WARNING",
                                            "dimension": QualityDimension.CONSISTENCY.value,
                                            "row": row_idx,
                                            "message": f"Row {row_idx}: Implausible ground speed calculated ({round(speed, 1)} m/s / {round(speed*3.6, 1)} km/h). Possible GPS glitch or coordinate swap.",
                                            "resolution": "Review telemetry point for GPS multipath or jump error.",
                                        })
                                    if dt_sec > self.MAX_TELEMETRY_GAP_SEC:
                                        issues.append({
                                            "severity": "WARNING",
                                            "dimension": QualityDimension.TIMELINESS.value,
                                            "row": row_idx,
                                            "message": f"Row {row_idx}: Telemetry logging gap of {round(dt_sec, 1)}s detected.",
                                            "resolution": "Document telemetry dropout or check flight log logger frequency.",
                                        })
                            except Exception:
                                pass

                    prev_lat = lat_f
                    prev_lon = lon_f
                except ValueError:
                    issues.append({
                        "severity": "WARNING",
                        "dimension": QualityDimension.VALIDITY.value,
                        "row": row_idx,
                        "message": f"Row {row_idx}: Non-numeric coordinates ('{lat_val}', '{lon_val}').",
                        "resolution": "Ensure coordinates are decimal degrees.",
                    })

            # Check timestamp ordering and duplicates
            time_str = cleaned_row.get("timestamp") or cleaned_row.get("time") or cleaned_row.get("observed_at")
            if time_str:
                if time_str in seen_timestamps:
                    issues.append({
                        "severity": "WARNING",
                        "dimension": QualityDimension.UNIQUENESS.value,
                        "row": row_idx,
                        "message": f"Row {row_idx}: Duplicate timestamp entry '{time_str}'.",
                        "resolution": "Deduplicate identical timestamp readings.",
                    })
                seen_timestamps.add(time_str)

                try:
                    curr_dt = self._parse_iso_or_common(time_str)
                    if prev_time and curr_dt < prev_time:
                        issues.append({
                            "severity": "CRITICAL",
                            "dimension": QualityDimension.CONSISTENCY.value,
                            "row": row_idx,
                            "message": f"Row {row_idx}: Chronological sequence regression (timestamp decreased).",
                            "resolution": "Sort records chronologically by timestamp.",
                        })
                    prev_time = curr_dt
                except Exception:
                    issues.append({
                        "severity": "WARNING",
                        "dimension": QualityDimension.VALIDITY.value,
                        "row": row_idx,
                        "message": f"Row {row_idx}: Could not parse timestamp string '{time_str}'.",
                        "resolution": "Format timestamps as ISO-8601 (YYYY-MM-DDTHH:MM:SSZ).",
                    })

            # Check battery values
            batt_str = cleaned_row.get("battery") or cleaned_row.get("battery_level") or cleaned_row.get("battery_pct")
            if batt_str:
                try:
                    batt_f = float(batt_str.replace("%", "").strip())
                    if not (0.0 <= batt_f <= 100.0):
                        issues.append({
                            "severity": "WARNING",
                            "dimension": QualityDimension.VALIDITY.value,
                            "row": row_idx,
                            "message": f"Row {row_idx}: Battery value {batt_f} outside 0-100% scale.",
                            "resolution": "Scale battery metric to standard 0-100% percentage.",
                        })
                except ValueError:
                    pass

        return records, issues

    def _validate_json_or_geojson(self, content: bytes) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        issues = []
        records = []
        try:
            data = json.loads(content.decode("utf-8", errors="replace"))
        except Exception as e:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.VALIDITY.value,
                "message": f"Invalid JSON syntax: {str(e)}",
                "resolution": "Validate JSON structure.",
            })
            return records, issues

        if isinstance(data, dict) and data.get("type") == "FeatureCollection":
            # GeoJSON feature collection
            features = data.get("features", [])
            for idx, feat in enumerate(features):
                geom = feat.get("geometry", {})
                props = feat.get("properties", {})
                if not geom or "coordinates" not in geom:
                    issues.append({
                        "severity": "WARNING",
                        "dimension": QualityDimension.GEOSPATIAL_RELIABILITY.value,
                        "message": f"Feature #{idx}: Missing geometry or coordinates.",
                        "resolution": "Include valid GeoJSON Point, LineString, or Polygon geometry.",
                    })
                records.append({
                    "feature_id": feat.get("id", f"feat-{idx}"),
                    "geometry_type": geom.get("type", "Unknown"),
                    "coordinates": geom.get("coordinates", []),
                    "properties": props,
                })
        elif isinstance(data, list):
            # List of telemetry or log objects
            records = data
        elif isinstance(data, dict):
            records = [data]

        return records, issues

    def _validate_image_metadata(self, filename: str, content: bytes) -> List[Dict[str, Any]]:
        issues = []
        if len(content) < 1024:
            issues.append({
                "severity": "CRITICAL",
                "dimension": QualityDimension.VALIDITY.value,
                "message": f"Image file '{filename}' is corrupted or truncated (< 1KB).",
                "resolution": "Re-upload the uncorrupted source image.",
            })
            return issues

        # Check for EXIF GPS markers in byte stream (0x8825 is GPS tag)
        has_exif = b"Exif" in content[:4096] or b"JFIF" in content[:4096]
        if not has_exif:
            issues.append({
                "severity": "WARNING",
                "dimension": QualityDimension.GEOSPATIAL_RELIABILITY.value,
                "message": f"Image '{filename}' lacks standard EXIF metadata or GPS geotag.",
                "resolution": "Link image manually to a flight log timestamp or coordinate.",
            })

        return issues

    def _parse_iso_or_common(self, s: str) -> datetime:
        s = s.strip()
        for fmt in (
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y/%m/%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        # Fallback to fromisoformat
        return datetime.fromisoformat(s.replace("Z", "+00:00"))


validation_engine = ValidationEngine()
