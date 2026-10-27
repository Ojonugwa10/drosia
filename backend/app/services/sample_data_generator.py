"""
Sample Data Generator for Drosia: Drone Security Intelligence & Analytics
Generates realistic Nigerian & critical infrastructure security surveillance missions,
GPS flight logs, telemetry points, GIS corridors, incidents, evidence links, and sample upload files.
"""

import csv
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple


def generate_initial_state() -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    t0 = now - timedelta(hours=3)
    t1 = now - timedelta(hours=2)

    # 1. Organization
    org_id = "org-mos-001"
    org = {
        "id": org_id,
        "name": "MOS Datahub Security Solutions",
        "status": "Active",
        "jurisdiction": "Federal Republic of Nigeria / West Africa",
        "created_at": (now - timedelta(days=90)).isoformat(),
    }

    # 2. Users (RBAC)
    users = [
        {
            "id": "usr-admin-01",
            "organization_id": org_id,
            "display_name": "Babatunde Adeleke",
            "email": "b.adeleke@mosdatahub.ng",
            "role": "org_admin",
            "status": "Active",
            "title": "Organization Administrator",
        },
        {
            "id": "usr-ops-02",
            "organization_id": org_id,
            "display_name": "Chukwuma Eze",
            "email": "c.eze@mosdatahub.ng",
            "role": "ops_manager",
            "status": "Active",
            "title": "Head of Operations",
        },
        {
            "id": "usr-pilot-03",
            "organization_id": org_id,
            "display_name": "Capt. Fatima Al-Hassan",
            "email": "f.alhassan@mosdatahub.ng",
            "role": "pilot",
            "status": "Active",
            "title": "Senior Drone Pilot (RPAS Lic #NG-842)",
        },
        {
            "id": "usr-analyst-04",
            "organization_id": org_id,
            "display_name": "Kelechi Nwosu",
            "email": "k.nwosu@mosdatahub.ng",
            "role": "analyst",
            "status": "Active",
            "title": "Senior GIS & Intelligence Analyst",
        },
        {
            "id": "usr-sup-05",
            "organization_id": org_id,
            "display_name": "Major Daniel Okafor (Rtd)",
            "email": "d.okafor@mosdatahub.ng",
            "role": "supervisor",
            "status": "Active",
            "title": "Perimeter Security Supervisor",
        },
        {
            "id": "usr-maint-06",
            "organization_id": org_id,
            "display_name": "Ibrahim Musa",
            "email": "i.musa@mosdatahub.ng",
            "role": "maintenance",
            "status": "Active",
            "title": "Fleet Maintenance Specialist",
        },
        {
            "id": "usr-appr-07",
            "organization_id": org_id,
            "display_name": "Amina Bello",
            "email": "a.bello@mosdatahub.ng",
            "role": "approver",
            "status": "Active",
            "title": "Director of Security Compliance & Reporting",
        },
        {
            "id": "usr-audit-08",
            "organization_id": org_id,
            "display_name": "Dr. Oladipo Johnson",
            "email": "o.johnson@mosdatahub.ng",
            "role": "auditor",
            "status": "Active",
            "title": "Independent Security & Compliance Auditor",
        },
    ]

    # 3. Projects
    projects = [
        {
            "id": "proj-lekki-01",
            "organization_id": org_id,
            "name": "Lekki Deepwater Port Perimeter & Access Recon",
            "project_type": "Port & Maritime Security",
            "sensitivity_level": "Official Sensitive",
            "retention_days": 365,
            "operating_area": "Lekki Free Trade Zone, Lagos State, Nigeria",
            "center": [6.4253, 3.8614],
            "created_at": (now - timedelta(days=60)).isoformat(),
        },
        {
            "id": "proj-tnp-02",
            "organization_id": org_id,
            "name": "Trans-Niger Pipeline Sector 7 Right-of-Way Recon",
            "project_type": "Pipeline Reconnaissance",
            "sensitivity_level": "Confidential",
            "retention_days": 730,
            "operating_area": "Niger Delta Basin Sector 7 Corridor, Rivers State",
            "center": [4.8156, 7.0498],
            "created_at": (now - timedelta(days=45)).isoformat(),
        },
        {
            "id": "proj-kano-03",
            "organization_id": org_id,
            "name": "Kano Kumbotso Solar Farm Critical Perimeter",
            "project_type": "Critical Infrastructure Protection",
            "sensitivity_level": "Official Sensitive",
            "retention_days": 365,
            "operating_area": "Kumbotso Industrial Corridor, Kano State",
            "center": [11.8902, 8.5124],
            "created_at": (now - timedelta(days=20)).isoformat(),
        },
    ]

    # 4. Assets (Fleet)
    assets = [
        {
            "id": "ast-m300-01",
            "organization_id": org_id,
            "asset_code": "UAV-M300-RTK-01",
            "manufacturer": "DJI Enterprise",
            "model": "Matrice 300 RTK",
            "asset_type": "Heavy Multirotor UAV",
            "serial_reference": "1581F-NG-0914",
            "status": "Active",
            "total_flight_hours": 142.8,
            "last_service_date": (now - timedelta(days=12)).strftime("%Y-%m-%d"),
        },
        {
            "id": "ast-m3t-02",
            "organization_id": org_id,
            "asset_code": "UAV-M3T-THERMAL-02",
            "manufacturer": "DJI Enterprise",
            "model": "Mavic 3 Thermal",
            "asset_type": "Compact FLIR Recon UAV",
            "serial_reference": "3MVT-NG-4482",
            "status": "Active",
            "total_flight_hours": 98.4,
            "last_service_date": (now - timedelta(days=18)).strftime("%Y-%m-%d"),
        },
        {
            "id": "ast-evo-03",
            "organization_id": org_id,
            "asset_code": "UAV-EVO2-SEC-03",
            "manufacturer": "Autel Robotics",
            "model": "EVO II Dual 640T",
            "asset_type": "Rapid Response UAV",
            "serial_reference": "EVO-NG-1120",
            "status": "Inspection Required",
            "total_flight_hours": 215.1,
            "last_service_date": (now - timedelta(days=40)).strftime("%Y-%m-%d"),
        },
    ]

    # 5. Missions
    # Lekki Port base coordinates: lat ~6.4253, lon ~3.8614
    lekki_planned_waypoints = [
        {"wp_id": 1, "latitude": 6.4210, "longitude": 3.8580, "altitude_m": 120.0, "name": "WP-1 Gate Access South"},
        {"wp_id": 2, "latitude": 6.4260, "longitude": 3.8590, "altitude_m": 120.0, "name": "WP-2 Western Boundary Fence"},
        {"wp_id": 3, "latitude": 6.4310, "longitude": 3.8620, "altitude_m": 120.0, "name": "WP-3 North Cargo Checkpoint"},
        {"wp_id": 4, "latitude": 6.4290, "longitude": 3.8680, "altitude_m": 120.0, "name": "WP-4 Eastern Perimeter Berm"},
        {"wp_id": 5, "latitude": 6.4230, "longitude": 3.8660, "altitude_m": 120.0, "name": "WP-5 Coastal Berm Patrol"},
        {"wp_id": 6, "latitude": 6.4210, "longitude": 3.8580, "altitude_m": 120.0, "name": "WP-6 Return to South Gate"},
    ]

    missions = [
        {
            "id": "msn-lekki-041",
            "project_id": "proj-lekki-01",
            "mission_code": "MSN-LK-2026-041",
            "mission_type": "Perimeter Surveillance",
            "objective": "Routine twilight security surveillance of south gate, western fence, and cargo boundary.",
            "planned_start_at": t0.isoformat(),
            "actual_start_at": (t0 + timedelta(minutes=4)).isoformat(),
            "actual_end_at": (t0 + timedelta(minutes=46)).isoformat(),
            "assigned_pilot_id": "usr-pilot-03",
            "assigned_pilot_name": "Capt. Fatima Al-Hassan",
            "asset_id": "ast-m300-01",
            "asset_code": "UAV-M300-RTK-01",
            "planned_route_waypoints": lekki_planned_waypoints,
            "status": "Completed",
            "created_by": "usr-ops-02",
            "created_at": (now - timedelta(days=2)).isoformat(),
        },
        {
            "id": "msn-tnp-088",
            "project_id": "proj-tnp-02",
            "mission_code": "MSN-TNP-2026-088",
            "mission_type": "Pipeline Reconnaissance",
            "objective": "High-resolution thermal infrared inspection along KP 42-58 right-of-way corridor.",
            "planned_start_at": (t1 - timedelta(hours=5)).isoformat(),
            "actual_start_at": (t1 - timedelta(hours=5, minutes=2)).isoformat(),
            "actual_end_at": (t1 - timedelta(hours=4, minutes=10)).isoformat(),
            "assigned_pilot_id": "usr-pilot-03",
            "assigned_pilot_name": "Capt. Fatima Al-Hassan",
            "asset_id": "ast-m3t-02",
            "asset_code": "UAV-M3T-THERMAL-02",
            "planned_route_waypoints": [
                {"wp_id": 1, "latitude": 4.8100, "longitude": 7.0420, "altitude_m": 80.0, "name": "KP 42 Valve Station"},
                {"wp_id": 2, "latitude": 4.8180, "longitude": 7.0510, "altitude_m": 80.0, "name": "KP 48 Swamp Crossing"},
                {"wp_id": 3, "latitude": 4.8250, "longitude": 7.0620, "altitude_m": 80.0, "name": "KP 58 Manifold Station"},
            ],
            "status": "Completed",
            "created_by": "usr-ops-02",
            "created_at": (now - timedelta(days=1)).isoformat(),
        },
        {
            "id": "msn-kno-015",
            "project_id": "proj-kano-03",
            "mission_code": "MSN-KNO-2026-015",
            "mission_type": "Critical Infrastructure Protection",
            "objective": "Perimeter intrusion detection sweep around high-voltage inverter stations.",
            "planned_start_at": now.isoformat(),
            "actual_start_at": now.isoformat(),
            "actual_end_at": None,
            "assigned_pilot_id": "usr-pilot-03",
            "assigned_pilot_name": "Capt. Fatima Al-Hassan",
            "asset_id": "ast-m300-01",
            "asset_code": "UAV-M300-RTK-01",
            "planned_route_waypoints": [],
            "status": "In Progress",
            "created_by": "usr-ops-02",
            "created_at": now.isoformat(),
        },
    ]

    # 6. Flight Tracks and Telemetry Points for Mission 041
    telemetry_points = []
    track_geometry = []
    start_time = t0 + timedelta(minutes=4)
    total_steps = 60

    # Path interpolation around the perimeter
    perimeter_coords = [
        (6.4210, 3.8580, 118.0),
        (6.4235, 3.8585, 120.0),
        (6.4260, 3.8590, 121.5),
        (6.4285, 3.8605, 119.5),
        (6.4310, 3.8620, 120.0),
        (6.4300, 3.8650, 122.0),
        (6.4290, 3.8680, 120.5),
        (6.4260, 3.8670, 119.0),
        (6.4230, 3.8660, 121.0),
        (6.4215, 3.8620, 120.0),
        (6.4210, 3.8580, 118.5),
    ]

    # Generate smooth telemetry interpolation
    point_idx = 0
    num_segments = len(perimeter_coords) - 1
    steps_per_segment = 6

    for s in range(num_segments):
        p_start = perimeter_coords[s]
        p_end = perimeter_coords[s + 1]
        for step in range(steps_per_segment):
            frac = step / float(steps_per_segment)
            lat = round(p_start[0] + (p_end[0] - p_start[0]) * frac, 6)
            lon = round(p_start[1] + (p_end[1] - p_start[1]) * frac, 6)
            alt = round(p_start[2] + (p_end[2] - p_start[2]) * frac, 1)
            t_point = start_time + timedelta(seconds=point_idx * 40)
            speed = round(7.5 + (point_idx % 4) * 0.8, 1)
            battery = round(98.0 - (point_idx * 0.55), 1)
            heading = round((s * 36.0 + step * 6.0) % 360.0, 1)

            t_obj = {
                "id": f"tel-{point_idx+1:04d}",
                "mission_id": "msn-lekki-041",
                "asset_id": "ast-m300-01",
                "observed_at": t_point.isoformat(),
                "latitude": lat,
                "longitude": lon,
                "altitude_value": alt,
                "altitude_reference": "AGL",
                "speed_value": speed,
                "heading": heading,
                "battery_level": battery,
                "source_record_id": f"rec-{point_idx+1:04d}",
            }
            telemetry_points.append(t_obj)
            track_geometry.append([lon, lat, alt])
            point_idx += 1

    flight_tracks = [
        {
            "id": "trk-lekki-041",
            "mission_id": "msn-lekki-041",
            "asset_id": "ast-m300-01",
            "source_file_id": "file-flt-041",
            "coordinate_reference_system": "EPSG:4326",
            "start_at": (t0 + timedelta(minutes=4)).isoformat(),
            "end_at": (t0 + timedelta(minutes=44)).isoformat(),
            "total_distance_km": 4.82,
            "max_speed_ms": 11.2,
            "avg_speed_ms": 8.1,
            "max_altitude_m": 122.0,
            "track_geometry": track_geometry,
            "data_quality_status": "Verified",
        }
    ]

    # 7. Media Assets (Linking to generated high-res images!)
    media_assets = [
        {
            "id": "med-ev01",
            "mission_id": "msn-lekki-041",
            "source_file_id": "file-img-001",
            "original_filename": "DJI_20261026_1847_SECTOR_SOUTH_GATE.JPG",
            "captured_at": (t0 + timedelta(minutes=18)).isoformat(),
            "latitude": 6.4215,
            "longitude": 3.8582,
            "altitude_m": 120.0,
            "media_type": "image/jpeg",
            "sensor_type": "Optical 4K Zoom (48MP)",
            "storage_path": "assets/images/perimeter_patrol_ev01.jpg",
            "thumbnail_path": "assets/images/perimeter_patrol_ev01.jpg",
            "integrity_status": "Verified (SHA-256 match)",
            "metadata_json": {
                "optical_zoom": "3.2x",
                "shutter_speed": "1/250s",
                "focal_length": "24mm",
                "iso": 400,
                "exif_gps_verified": True,
            },
        },
        {
            "id": "med-ev02",
            "mission_id": "msn-lekki-041",
            "source_file_id": "file-img-002",
            "original_filename": "FLIR_20261026_1854_THERMAL_CORRIDOR.JPG",
            "captured_at": (t0 + timedelta(minutes=25)).isoformat(),
            "latitude": 6.4285,
            "longitude": 3.8605,
            "altitude_m": 80.0,
            "media_type": "image/jpeg",
            "sensor_type": "FLIR Longwave IR (640x512)",
            "storage_path": "assets/images/thermal_recon_ev02.jpg",
            "thumbnail_path": "assets/images/thermal_recon_ev02.jpg",
            "integrity_status": "Verified (SHA-256 match)",
            "metadata_json": {
                "palette": "White-Hot IR",
                "temp_delta": "18.5 deg C",
                "sensor_range_m": 250,
                "exif_gps_verified": True,
            },
        },
    ]

    # 8. Incidents & Evidence Links
    incidents = [
        {
            "id": "inc-001",
            "project_id": "proj-lekki-01",
            "mission_id": "msn-lekki-041",
            "category": "Perimeter Breach",
            "description": "Stationary light commercial vehicle parked outside designated gate holding bay without active clearance manifest. Visual inspection shows two individuals near perimeter wire.",
            "observed_at": (t0 + timedelta(minutes=18)).isoformat(),
            "latitude": 6.4215,
            "longitude": 3.8582,
            "altitude_m": 120.0,
            "verification_status": "Verified Observation",
            "severity": "High",
            "created_by": "usr-pilot-03",
            "created_at": (t0 + timedelta(minutes=20)).isoformat(),
            "evidence_links": ["med-ev01"],
        },
        {
            "id": "inc-002",
            "project_id": "proj-lekki-01",
            "mission_id": "msn-lekki-041",
            "category": "Thermal Anomaly",
            "description": "Thermal hotspot detected adjacent to underground conduit run along western fence corridor. High temp delta (+18.5 C) relative to background earth.",
            "observed_at": (t0 + timedelta(minutes=25)).isoformat(),
            "latitude": 6.4285,
            "longitude": 3.8605,
            "altitude_m": 80.0,
            "verification_status": "Confirmed Threat",
            "severity": "Critical",
            "created_by": "usr-pilot-03",
            "created_at": (t0 + timedelta(minutes=27)).isoformat(),
            "evidence_links": ["med-ev02"],
        },
        {
            "id": "inc-003",
            "project_id": "proj-lekki-01",
            "mission_id": "msn-lekki-041",
            "category": "Suspicious Loitering",
            "description": "Movement observed near eastern drainage culvert outside secondary chain-link barrier.",
            "observed_at": (t0 + timedelta(minutes=34)).isoformat(),
            "latitude": 6.4230,
            "longitude": 3.8660,
            "altitude_m": 121.0,
            "verification_status": "Unverified",
            "severity": "Medium",
            "created_by": "usr-pilot-03",
            "created_at": (t0 + timedelta(minutes=36)).isoformat(),
            "evidence_links": [],
        },
    ]

    # 9. Findings (Evidence-backed operational intelligence)
    findings = [
        {
            "id": "fnd-001",
            "analysis_run_id": "run-041-01",
            "finding_type": "Perimeter Infiltration Vulnerability",
            "summary": "Verified unauthorized vehicle presence observed at South Gate outer security boundary.",
            "detailed_explanation": (
                "Optical zoom sensor captured an unmanifested pickup truck parked at coordinate 6.4215 N, 3.8582 E at 18:47 UTC. "
                "The vehicle remained stationary for 14 minutes within 15 meters of the primary concrete barrier."
            ),
            "supporting_metrics": {
                "proximity_to_fence_m": 14.8,
                "dwell_time_min": 14.0,
                "optical_confidence_score": 0.94,
            },
            "evidence_ids": ["med-ev01"],
            "geographic_context": {"latitude": 6.4215, "longitude": 3.8582, "sector": "South Gate Alpha"},
            "uncertainty_information": "High optical confidence; license plate obscured by dust angle.",
            "data_quality_limitations": "Observation corroborated by 12 consecutive telemetry epochs.",
            "verification_status": "Verified Observation",
            "review_status": "Approved by Supervisor",
            "created_at": (t0 + timedelta(minutes=45)).isoformat(),
        },
        {
            "id": "fnd-002",
            "analysis_run_id": "run-041-01",
            "finding_type": "Subsurface Pipeline / Cable Thermal Hotspot",
            "summary": "Confirmed critical thermal anomaly (+18.5 C delta) at Western Conduit Junction.",
            "detailed_explanation": (
                "FLIR thermal longwave infrared payload identified a 3.4-meter elongated surface heat signature. "
                "Temperature delta exceeds normal ambient by 18.5 deg C, indicating electrical overheating or unauthorized pipeline tapping attempt."
            ),
            "supporting_metrics": {
                "temp_delta_c": 18.5,
                "heat_footprint_length_m": 3.4,
                "flir_gain_mode": "Auto High-Contrast",
            },
            "evidence_ids": ["med-ev02"],
            "geographic_context": {"latitude": 6.4285, "longitude": 3.8605, "sector": "Western Pipeline Berm"},
            "uncertainty_information": "Thermal sensor calibrated within +/- 0.5 C.",
            "data_quality_limitations": "Track coverage verified; ground sensor verification dispatch recommended.",
            "verification_status": "Confirmed Threat",
            "review_status": "Escalated for Priority Interdiction",
            "created_at": (t0 + timedelta(minutes=48)).isoformat(),
        },
    ]

    # 10. Reports
    reports = [
        {
            "id": "rep-lekki-2026-001",
            "project_id": "proj-lekki-01",
            "report_title": "Lekki Port Twilight Surveillance & Threat Assessment Report",
            "report_type": "Security Intelligence & Mission Summary",
            "reporting_period_start": t0.isoformat(),
            "reporting_period_end": (t0 + timedelta(hours=1)).isoformat(),
            "version_number": 1,
            "status": "Review",
            "analysis_run_id": "run-041-01",
            "executive_summary": (
                "Mission MSN-LK-2026-041 completed 94.2% patrol corridor coverage across 4.82 km of Lekki perimeter fence. "
                "Two actionable findings were recorded: one verified unauthorized vehicle near South Gate (Evidence MED-EV01) "
                "and one critical subterranean thermal anomaly along the Western conduit (Evidence MED-EV02). "
                "Ground interdiction team was alerted."
            ),
            "methodology_and_limitations": (
                "Metrics calculated deterministically from UAV-M300-RTK-01 flight logs conforming to EPSG:4326. "
                "Patrol coverage denotes aircraft track presence; optical ground occlusion factors (trees/berms) documented."
            ),
            "findings_included": ["fnd-001", "fnd-002"],
            "storage_key": "reports/rep_lekki_2026_001_v1.json",
            "is_stale": False,
            "approved_by": None,
            "approved_by_name": None,
            "approved_at": None,
            "rejection_reason": None,
            "created_by": "usr-ops-02",
            "created_at": (t0 + timedelta(minutes=55)).isoformat(),
        }
    ]

    return {
        "organization": org,
        "users": users,
        "projects": projects,
        "assets": assets,
        "missions": missions,
        "telemetry_points": telemetry_points,
        "flight_tracks": flight_tracks,
        "media_assets": media_assets,
        "incidents": incidents,
        "findings": findings,
        "reports": reports,
    }


def write_sample_csv_and_geojson_files(output_dir: str):
    """
    Writes physical sample files into frontend/assets/samples/
    Allows users to download and batch-upload real files through the platform UI!
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Telemetry CSV sample
    tel_path = os.path.join(output_dir, "telemetry_mission_lekki_perimeter.csv")
    with open(tel_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "latitude", "longitude", "altitude_m", "speed_kmh", "heading", "battery_pct"])
        now = datetime.now(timezone.utc)
        coords = [
            (6.4210, 3.8580, 118.0, 28.5, 45.0, 98),
            (6.4235, 3.8585, 120.0, 30.2, 52.0, 96),
            (6.4260, 3.8590, 121.5, 29.8, 48.0, 94),
            (6.4285, 3.8605, 119.5, 31.0, 50.0, 92),
            (6.4310, 3.8620, 120.0, 27.5, 90.0, 90),
            (6.4300, 3.8650, 122.0, 28.0, 135.0, 88),
            (6.4290, 3.8680, 120.5, 30.5, 180.0, 85),
            (6.4260, 3.8670, 119.0, 29.0, 210.0, 82),
            (6.4230, 3.8660, 121.0, 28.2, 225.0, 79),
            (6.4215, 3.8620, 120.0, 32.0, 260.0, 76),
            (6.4210, 3.8580, 118.5, 18.0, 270.0, 74),
        ]
        for i, (lat, lon, alt, spd, hdg, batt) in enumerate(coords):
            ts = (now + timedelta(seconds=i * 60)).strftime("%Y-%m-%dT%H:%M:%SZ")
            writer.writerow([ts, lat, lon, alt, spd, hdg, batt])

    # 2. Incidents CSV sample
    inc_path = os.path.join(output_dir, "incidents_lekki_perimeter.csv")
    with open(inc_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["observed_at", "category", "description", "latitude", "longitude", "severity", "verification_status"])
        writer.writerow([
            now.strftime("%Y-%m-%dT18:47:00Z"),
            "Perimeter Breach",
            "Suspicious stationary vehicle adjacent to South Gate barrier",
            6.4215,
            3.8582,
            "High",
            "Verified Observation",
        ])
        writer.writerow([
            now.strftime("%Y-%m-%dT18:54:00Z"),
            "Thermal Anomaly",
            "Subterranean pipeline conduit thermal hotspot (+18.5 C)",
            6.4285,
            3.8605,
            "Critical",
            "Confirmed Threat",
        ])
        writer.writerow([
            now.strftime("%Y-%m-%dT19:02:00Z"),
            "Suspicious Loitering",
            "Pedestrian activity along exterior drainage berm",
            6.4230,
            3.8660,
            "Medium",
            "Unverified",
        ])

    # 3. GeoJSON Planned Corridor sample
    geojson_path = os.path.join(output_dir, "planned_route_lekki_corridor.geojson")
    geojson_data = {
        "type": "FeatureCollection",
        "name": "Planned_Patrol_Corridor_Lekki_Sector_Alpha",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "corridor_id": "CORR-LK-01",
                    "corridor_name": "Lekki Deepwater Free Zone Primary Fence Line",
                    "buffer_width_m": 35.0,
                    "security_tier": "Tier-1 Critical",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [3.8580, 6.4210],
                        [3.8585, 6.4235],
                        [3.8590, 6.4260],
                        [3.8605, 6.4285],
                        [3.8620, 6.4310],
                        [3.8650, 6.4300],
                        [3.8680, 6.4290],
                        [3.8670, 6.4260],
                        [3.8660, 6.4230],
                        [3.8620, 6.4215],
                        [3.8580, 6.4210],
                    ],
                },
            }
        ],
    }
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)

    # 4. QA Quarantine test file (Demonstrates FR-03 and Section 6 error detection!)
    qa_path = os.path.join(output_dir, "corrupted_sample_for_qa_testing.csv")
    with open(qa_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "latitude", "longitude", "altitude_ft", "speed_mph"])
        writer.writerow(["2026-10-26T18:00:00Z", 6.4210, 3.8580, 393.7, 18.0])
        writer.writerow(["2026-10-26T18:01:00Z", 195.4210, 3.8585, 400.0, 19.5])  # Lat > 90!
        writer.writerow(["2026-10-26T17:59:00Z", 6.4260, 3.8590, 410.0, 22.0])  # Time regression backwards!
        writer.writerow(["2026-10-26T18:03:00Z", 6.5500, 4.1200, 390.0, 550.0])  # Implausible 550 mph speed jump!
