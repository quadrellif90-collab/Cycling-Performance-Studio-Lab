"""Tests for core Domestique modules merged into CPSL."""
import pytest
from pathlib import Path


class TestZones:
    """Test zones.py (shared across CPSL/PCC/Domestique)."""

    def test_power_zones_count(self):
        from zones import power_zones
        pz = power_zones(250)
        assert len(pz) == 7

    def test_power_zones_names(self):
        from zones import power_zones
        pz = power_zones(250)
        names = [z.name for z in pz]
        assert "Recovery" in names[0]
        assert "Neuromuscular" in names[-1]

    def test_power_zones_monotonically_increasing(self):
        from zones import power_zones
        pz = power_zones(300)
        for i in range(1, len(pz)):
            assert pz[i].low >= pz[i - 1].low

    def test_hr_zones(self):
        from zones import hr_zones
        hz = hr_zones(165, 190)
        assert len(hz) == 5
        assert hz[0].low == 0
        assert hz[-1].high == 190

    def test_estimated_hr_max_young(self):
        from zones import estimated_hr_max
        assert estimated_hr_max(20) > 190

    def test_estimated_hr_max_old(self):
        from zones import estimated_hr_max
        assert estimated_hr_max(70) < 160

    def test_zone_distribution_basic(self):
        from zones import zone_distribution, Zone
        zones = [Zone(0, 100, "Z1"), Zone(100, 200, "Z2")]
        samples = [(150, 60), (120, 120)]
        dist = zone_distribution(samples, zones)
        assert len(dist) == 2
        assert sum(dist) == 180

    def test_zone_distribution_empty(self):
        from zones import zone_distribution, Zone
        zones = [Zone(0, 100, "Z1")]
        dist = zone_distribution([], zones)
        assert dist == [0]


class TestFitnessEstimation:
    """Test fitness_estimation.py."""

    def test_estimate_ftp_typical(self):
        from fitness_estimation import estimate_ftp
        efforts = {20: 300, 60: 250, 300: 200, 1200: 150}
        ftp = estimate_ftp(efforts)
        assert ftp is not None
        assert 100 < ftp < 400

    def test_estimate_ftp_empty(self):
        from fitness_estimation import estimate_ftp
        assert estimate_ftp({}) is None

    def test_estimate_ftp_single_effort(self):
        from fitness_estimation import estimate_ftp
        ftp = estimate_ftp({300: 250})
        if ftp is not None:
            assert 100 < ftp < 500


class TestPowerCurve:
    """Test power_curve.py."""

    def test_import(self):
        import power_curve
        assert hasattr(power_curve, 'aggregate_power_curve')

    def test_aggregate_power_curve_callable(self):
        from power_curve import aggregate_power_curve
        assert callable(aggregate_power_curve)


class TestTrainingPlanner:
    """Test training_planner.py."""

    def test_import(self):
        import training_planner
        assert hasattr(training_planner, 'daily_recalculate_adjustment')

    def test_daily_recalculate(self):
        from training_planner import daily_recalculate_adjustment
        assert callable(daily_recalculate_adjustment)

    def test_recommend_block_model(self):
        from training_planner import recommend_block_model
        assert callable(recommend_block_model)


class TestUserProfile:
    """Test user_home.py path management."""

    def test_cpsl_home(self):
        from user_home import cpsl_home
        assert cpsl_home is not None

    def test_domestique_home_alias(self):
        from user_home import domestique_home, cpsl_home
        assert domestique_home == cpsl_home


class TestProfileManager:
    """Test profile_manager.py."""

    def test_import(self):
        import profile_manager
        assert hasattr(profile_manager, 'ProfileManager')

    def test_get_returns_profile(self):
        from profile_manager import get
        profile = get()
        assert profile is not None


class TestErrorCodes:
    """Test error_codes.py."""

    def test_import(self):
        import error_codes
        assert hasattr(error_codes, 'Codes')

    def test_has_plan_parse_corrupt(self):
        from error_codes import Codes
        assert hasattr(Codes, 'PLAN_PARSE_CORRUPT')


class TestReadiness:
    """Test readiness.py."""

    def test_import(self):
        import readiness
        assert hasattr(readiness, 'compute_readiness')


class TestSleep:
    """Test sleep.py."""

    def test_import(self):
        import sleep
        assert hasattr(sleep, 'compute_sleep_score')

    def test_compute_sleep_score(self):
        from sleep import compute_sleep_score
        assert callable(compute_sleep_score)


class TestExecutionScore:
    """Test execution_score.py."""

    def test_import(self):
        import execution_score
        assert hasattr(execution_score, 'score_ride')

    def test_score_ride_callable(self):
        from execution_score import score_ride
        assert callable(score_ride)
