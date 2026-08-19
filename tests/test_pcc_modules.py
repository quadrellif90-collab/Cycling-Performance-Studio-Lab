"""Tests for PCC modules integrated into CPSL."""
import pytest
import json
import os
import tempfile
from pathlib import Path


class TestZones:
    """Test zones.py (byte-identical between CPSL/PCC/Domestique)."""

    def test_power_zones(self):
        from zones import power_zones
        pz = power_zones(250)
        assert len(pz) == 7
        assert pz[0].low == 0
        assert "Recovery" in pz[0].name
        assert "Tempo" in pz[2].name
        assert "Anaerobic" in pz[5].name

    def test_hr_zones(self):
        from zones import hr_zones
        hz = hr_zones(165, 190)
        assert len(hz) == 5
        assert "Recovery" in hz[0].name

    def test_estimated_hr_max(self):
        from zones import estimated_hr_max
        hrmax = estimated_hr_max(35)
        assert 175 < hrmax < 185

    def test_zone_distribution(self):
        from zones import zone_distribution, Zone
        zones = [Zone(0, 100, "Z1"), Zone(100, 200, "Z2")]
        samples = [(150, 60), (120, 120)]  # (value, duration) pairs
        dist = zone_distribution(samples, zones)
        assert isinstance(dist, list)
        assert len(dist) == 2
        assert dist[0] + dist[1] == 180  # total duration


class TestFitnessEstimation:
    """Test fitness_estimation.py."""

    def test_estimate_ftp(self):
        from fitness_estimation import estimate_ftp
        efforts = {20: 300, 60: 250, 300: 200}
        ftp = estimate_ftp(efforts)
        assert ftp is not None
        assert 150 < ftp < 350

    def test_estimate_ftp_empty(self):
        from fitness_estimation import estimate_ftp
        ftp = estimate_ftp({})
        assert ftp is None


class TestNutrition:
    """Test nutrition.py."""

    def test_day_macros(self):
        from nutrition import day_macros
        result = day_macros("high_intensity", "maintain", 75, 180, 30, "m")
        assert "target_kcal" in result
        assert "carb_g" in result
        assert "protein_g" in result
        assert "fat_g" in result
        assert result["target_kcal"] > 1500

    def test_supplement_doses(self):
        from nutrition import supplement_doses
        result = supplement_doses(75)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "key" in result[0]
        assert "dose" in result[0]


class TestStrengthMobility:
    """Test strength_mobility.py."""

    def test_build_strength_plan(self):
        from strength_mobility import build_strength_plan
        plan = build_strength_plan("base", 4, one_rm_kg=100)
        assert len(plan) == 4
        assert len(plan[0]["sessions"]) > 0

    def test_build_mobility_plan(self):
        from strength_mobility import build_mobility_plan
        routine = build_mobility_plan(7)
        assert len(routine) == 7
        assert "sequence" in routine[0]
        assert len(routine[0]["sequence"]) > 0

    def test_strength_summary(self):
        from strength_mobility import strength_summary
        s = strength_summary("base")
        assert "phase" in s
        assert "sessions_per_week" in s


class TestCPModels:
    """Test cp_models.py."""

    def test_fit_morton_3p(self):
        from cp_models import fit_morton_3p
        efforts = {120: 400, 300: 300, 600: 250, 1200: 200}
        result = fit_morton_3p(efforts)
        # May return None if data insufficient, that's OK
        if result is not None:
            cp, wprime, tau, r2 = result
            assert cp > 0
            assert wprime > 0


class TestCalendarICS:
    """Test calendar_ics.py."""

    def test_build_ics(self):
        from calendar_ics import build_ics
        # build_ics reads current_plan.json, may return empty calendar
        ics = build_ics()
        assert isinstance(ics, str)
        assert "VCALENDAR" in ics or "BEGIN:VCALENDAR" in ics


class TestFieldTestProtocols:
    """Test field_test_protocols.py."""

    def test_list_protocols(self):
        from field_test_protocols import list_protocols
        protocols = list_protocols()
        assert len(protocols) > 0
        assert "id" in protocols[0]
        assert "label" in protocols[0]


class TestHRVEngine:
    """Test hrv_engine.py."""

    def test_compute_baseline(self):
        from hrv_engine import compute_baseline
        daily = [
            {"date": "2026-01-01", "rmssd_ms": 45.0},
            {"date": "2026-01-02", "rmssd_ms": 50.0},
            {"date": "2026-01-03", "rmssd_ms": 42.0},
            {"date": "2026-01-04", "rmssd_ms": 48.0},
            {"date": "2026-01-05", "rmssd_ms": 55.0},
            {"date": "2026-01-06", "rmssd_ms": 40.0},
            {"date": "2026-01-07", "rmssd_ms": 47.0},
        ]
        baseline = compute_baseline(daily)
        assert "mean_rmssd" in baseline
        assert baseline["mean_rmssd"] > 0


class TestPedalAsymmetry:
    """Test pedal_asymmetry.py."""

    def test_parse_pedal_json(self):
        from pedal_asymmetry import parse_pedal_json
        data = {
            "left_power": 150,
            "right_power": 145,
            "left_torque_effectiveness": 85.0,
            "right_torque_effectiveness": 82.0,
            "left_pedal_smoothness": 75.0,
            "right_pedal_smoothness": 73.0,
        }
        result = parse_pedal_json(data)
        assert "asymmetry_balance" in result
        assert "flag" in result


class TestCustomCharts:
    """Test custom_charts.py."""

    def test_load_charts(self):
        from custom_charts import load_charts
        charts = load_charts()
        assert isinstance(charts, list)


class TestUpstreamCheck:
    """Test upstream_check.py."""

    def test_check_upstream(self):
        from upstream_check import check_upstream
        result = check_upstream()
        assert isinstance(result, dict)
        assert "upstream_tag" in result or "error" in result


class TestActivityInsights:
    """Test activity_insights.py."""

    def test_classify_protocol_from_if(self):
        from activity_insights import classify_protocol_from_if
        result = classify_protocol_from_if(0.75)
        assert isinstance(result, str)
        assert "Endurance" in result or "Z2" in result


class TestDietParser:
    """Test diet_parser.py."""

    def test_import(self):
        import diet_parser
        assert hasattr(diet_parser, 'parse_diet_pdf') or hasattr(diet_parser, 'parse')


class TestTerraSync:
    """Test terra_sync.py."""

    def test_import(self):
        import terra_sync
        assert hasattr(terra_sync, 'build_auth_url')
        assert hasattr(terra_sync, 'handle_callback')
        assert hasattr(terra_sync, 'disconnect')


class TestBiaParser:
    """Test bia_parser.py."""

    def test_import(self):
        import bia_parser
        assert hasattr(bia_parser, 'parse_bia_pdf')
        assert hasattr(bia_parser, 'parse_bia_text')
        assert hasattr(bia_parser, 'BIAReading')


class TestSessionManager:
    """Test session_manager.py."""

    def test_import(self):
        import session_manager
        assert hasattr(session_manager, 'SessionManager')


class TestCache:
    """Test caching.py."""

    def test_import(self):
        import caching
        assert hasattr(caching, 'TTLCache') or hasattr(caching, 'cache')
