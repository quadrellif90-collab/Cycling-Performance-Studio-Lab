"""Tests for training, analysis, and performance modules."""
import pytest


class TestCPModels:
    """Test cp_models.py — critical power modeling."""

    def test_fit_morton_3p(self):
        from cp_models import fit_morton_3p
        efforts = {120: 400, 300: 300, 600: 250, 1200: 200}
        result = fit_morton_3p(efforts)
        if result is not None:
            cp, wprime, tau, r2 = result
            assert cp > 0
            assert wprime > 0
            assert tau > 0
            assert 0 <= r2 <= 1

    def test_fit_morton_3p_empty(self):
        from cp_models import fit_morton_3p
        assert fit_morton_3p({}) is None


class TestCPImport:
    """Test cpep_import.py — CP event parser."""

    def test_import(self):
        import cpep_import
        assert hasattr(cpep_import, 'parse_cpep_pdf')

    def test_load_latest(self):
        from cpep_import import load_latest_cpep
        assert callable(load_latest_cpep)


class TestPedalAsymmetry:
    """Test pedal_asymmetry.py — left/right balance."""

    def test_parse_pedal_balanced(self):
        from pedal_asymmetry import parse_pedal_json
        data = {
            "left_balance_pct": 50.0, "right_balance_pct": 50.0,
            "left_te": 85.0, "right_te": 85.0,
            "left_ps": 75.0, "right_ps": 75.0,
        }
        r = parse_pedal_json(data)
        assert r["left_balance_pct"] == 50.0
        assert r["right_balance_pct"] == 50.0
        assert r["asymmetry_balance"] == 0.0
        assert r["flag"] is False

    def test_parse_pedal_asymmetric(self):
        from pedal_asymmetry import parse_pedal_json
        data = {
            "left_balance_pct": 60.0, "right_balance_pct": 40.0,
            "left_te": 90.0, "right_te": 70.0,
            "left_ps": 80.0, "right_ps": 60.0,
        }
        r = parse_pedal_json(data)
        assert r["left_balance_pct"] == 60.0
        assert r["flag"] is True

    def test_parse_pedal_returns_dict(self):
        from pedal_asymmetry import parse_pedal_json
        r = parse_pedal_json({"left_power": 100, "right_power": 100})
        assert isinstance(r, dict)
        assert "asymmetry_balance" in r


class TestActivityInsights:
    """Test activity_insights.py — ride classification."""

    def test_classify_endurance(self):
        from activity_insights import classify_protocol_from_if
        r = classify_protocol_from_if(0.65)
        assert "Endurance" in r or "Z2" in r

    def test_classify_threshold(self):
        from activity_insights import classify_protocol_from_if
        r = classify_protocol_from_if(0.95)
        assert "Soglia" in r or "Z4" in r

    def test_classify_vo2(self):
        from activity_insights import classify_protocol_from_if
        r = classify_protocol_from_if(1.05)
        assert "VO2" in r or "Z5" in r

    def test_classify_recovery(self):
        from activity_insights import classify_protocol_from_if
        r = classify_protocol_from_if(0.5)
        assert "Recupero" in r or "Z1" in r


class TestHRVEngine:
    """Test hrv_engine.py — HRV analysis."""

    def test_compute_baseline(self):
        from hrv_engine import compute_baseline
        daily = [
            {"date": f"2026-01-{i:02d}", "rmssd_ms": 40 + i * 2}
            for i in range(1, 10)
        ]
        b = compute_baseline(daily)
        assert b["mean_rmssd"] > 0
        assert b["std_rmssd"] >= 0

    def test_compute_baseline_empty(self):
        from hrv_engine import compute_baseline
        b = compute_baseline([])
        assert isinstance(b, dict)


class TestStrainScore:
    """Test strain_score.py."""

    def test_import(self):
        import strain_score
        assert hasattr(strain_score, 'compute_xss_components')

    def test_compute_xss_callable(self):
        from strain_score import compute_xss_components
        assert callable(compute_xss_components)

    def test_mpa_function(self):
        from strain_score import MPA
        assert callable(MPA)


class TestTauFitting:
    """Test tau_fitting.py — fatigue resistance."""

    def test_import(self):
        import tau_fitting
        assert hasattr(tau_fitting, 'fit_tau_per_athlete')

    def test_fit_tau_callable(self):
        from tau_fitting import fit_tau_per_athlete
        assert callable(fit_tau_per_athlete)


class TestContinuousPolicy:
    """Test continuous_policy.py — continuous goal engine."""

    def test_import(self):
        import continuous_policy
        assert hasattr(continuous_policy, 'deload_trigger')

    def test_foster_monotony(self):
        from continuous_policy import foster_monotony
        assert callable(foster_monotony)

    def test_hrv_band(self):
        from continuous_policy import hrv_band
        assert callable(hrv_band)

    def test_suggest_today_family(self):
        from continuous_policy import suggest_today_family
        assert callable(suggest_today_family)


class TestHRTargets:
    """Test hr_targets.py — heart rate zones."""

    def test_import(self):
        import hr_targets
        assert hasattr(hr_targets, 'zone_of_pct')

    def test_zone_of_pct(self):
        from hr_targets import zone_of_pct
        assert callable(zone_of_pct)


class TestOOSValidation:
    """Test oos_validation.py — out-of-sample validation."""

    def test_import(self):
        import oos_validation
        assert hasattr(oos_validation, 'validate_banister_oos')

    def test_validate_callable(self):
        from oos_validation import validate_banister_oos
        assert callable(validate_banister_oos)


class TestStructureFidelity:
    """Test structure_fidelity.py — workout structure analysis."""

    def test_import(self):
        import structure_fidelity
        assert hasattr(structure_fidelity, 'score_structure')

    def test_parse_zwo(self):
        from structure_fidelity import parse_zwo_text
        assert callable(parse_zwo_text)

    def test_score_blocks(self):
        from structure_fidelity import score_blocks
        assert callable(score_blocks)
