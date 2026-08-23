"""Tests for v1.5.0 Montis port modules:
- espe.py            (Energy System Progression Engine)
- durability_score.durability_trend  (ISDM-style weekly trend)
- advanced_metrics.anaerobic_repeatability  (W'bal depletion stats)
- ai_coach.decision_engine.compute_ade      (ADE governance)
"""
import datetime as _dt

import pytest

TODAY = _dt.date(2026, 8, 23)


def _iso(days_ago: int) -> str:
    return (TODAY - _dt.timedelta(days=days_ago)).isoformat()


# ══════════════════════════════════════════════════════════════════════════════
# ESPE
# ══════════════════════════════════════════════════════════════════════════════

class TestEspe:

    def _ride(self, days_ago, efforts):
        return {"date": _iso(days_ago), "efforts": [
            {"secs": s, "watts": w} for s, w in efforts]}

    def test_progression_detected(self):
        from espe import compute_espe
        prev = [(60, 800), (300, 500), (1200, 350), (3600, 280)]
        cur = [(60, 850), (300, 520), (1200, 365), (3600, 285)]
        rides = [self._ride(100, prev), self._ride(10, cur)]
        out = compute_espe(rides, window_days=84, today=TODAY)
        assert out["ok"] is True
        by_sys = {s["system"]: s for s in out["systems"]}
        # P1m +6.25% -> strong_gain anaerobic
        assert by_sys["anaerobic"]["classification"] == "strong_gain"
        assert by_sys["threshold"]["delta_pct"] == pytest.approx(
            100 * (365 - 350) / 350, abs=0.1)
        assert out["rides_current_window"] >= 1
        assert out["rides_previous_window"] >= 1

    def test_derived_metrics(self):
        from espe import compute_espe
        cur = [(60, 900), (300, 500), (1200, 400), (3600, 300)]
        rides = [self._ride(100, cur), self._ride(10, cur)]
        out = compute_espe(rides, window_days=84, today=TODAY, cp_w=280)
        assert out["glycolytic_bias"] == pytest.approx(900 / 400, abs=0.01)
        assert out["durability_gradient"] == pytest.approx(300 / 400, abs=0.01)
        assert out["vo2_reserve_ratio"] == pytest.approx(500 / 280, abs=0.01)
        assert out["plateau"] is True
        assert out["adaptation_state"] == "plateau"

    def test_insufficient_data(self):
        from espe import compute_espe
        out = compute_espe([], window_days=84, today=TODAY)
        assert out["ok"] is False
        assert out["adaptation_state"] == "insufficient_data"

    def test_curve_profile_mapping(self):
        from espe import compute_espe
        # Steep decay -> anaerobic specialist-ish shape
        cur = [(60, 1000), (300, 450), (1200, 320), (3600, 250)]
        rides = [self._ride(10, cur)]
        out = compute_espe(rides, window_days=84, today=TODAY)
        # Only one window populated: ok False but curve profile computed
        assert out["curve_profile"] in (
            None, "time_trialist", "endurance_monster", "all_rounder",
            "climber", "sprinter_puncheur", "anaerobic_specialist")

    def test_power_stream_source(self):
        from espe import _best_mean_powers, compute_espe
        stream = [300] * 3700
        be = _best_mean_powers(stream)
        assert be[60] == 300 and be[3600] == 300
        rides = [{"date": _iso(5), "power_stream": stream},
                 {"date": _iso(90), "power_stream": stream}]
        out = compute_espe(rides, window_days=84, today=TODAY)
        # identical windows -> all deltas ~0 -> plateau
        assert out["ok"] is True
        assert out["plateau"] is True


# ══════════════════════════════════════════════════════════════════════════════
# Durability trend (ISDM)
# ══════════════════════════════════════════════════════════════════════════════

class TestDurabilityTrend:

    def _ride(self, days_ago, decoupling, duration_s=7200):
        return {"date": _iso(days_ago), "decoupling_pct": decoupling,
                "duration_s": duration_s}

    def test_drift_clear(self):
        from durability_score import durability_trend
        rides = [self._ride(i, 12.0 + i) for i in range(4)]
        out = durability_trend(rides, days=7, today=TODAY)
        assert out["state"] == "drifting"
        assert out["mean_signed_decoupling"] > 10

    def test_drift_requires_repetition(self):
        from durability_score import durability_trend
        rides = [self._ride(1, 12.0), self._ride(3, 2.0)]
        out = durability_trend(rides, days=7, today=TODAY)
        assert out["state"] != "drifting"

    def test_improving(self):
        from durability_score import durability_trend
        rides = [self._ride(1, -7.0), self._ride(3, -6.5)]
        out = durability_trend(rides, days=7, today=TODAY)
        assert out["state"] == "improving"

    def test_stable_and_insufficient(self):
        from durability_score import durability_trend
        out = durability_trend([self._ride(1, 1.0), self._ride(2, 2.0)],
                               days=7, today=TODAY)
        assert out["state"] == "stable"
        out_empty = durability_trend([], days=7, today=TODAY)
        assert out_empty["state"] == "insufficient_data"

    def test_short_rides_excluded(self):
        from durability_score import durability_trend
        rides = [self._ride(1, 15.0, duration_s=1800)]
        out = durability_trend(rides, days=7, today=TODAY)
        assert out["state"] == "insufficient_data"


# ══════════════════════════════════════════════════════════════════════════════
# Anaerobic repeatability (W'bal)
# ══════════════════════════════════════════════════════════════════════════════

class TestAnaerobicRepeatability:

    def _ride(self, days_ago, wp=None, dep=None, kj=None):
        return {"date": _iso(days_ago), "icu_w_prime": wp,
                "icu_max_wbal_depletion": dep, "kj_above_ftp": kj}

    def test_icu_source(self):
        from advanced_metrics import anaerobic_repeatability
        rides = [
            self._ride(1, wp=20000, dep=13000),   # 65% high
            self._ride(2, wp=20000, dep=11000),   # 55% moderate
            self._ride(3, wp=20000, dep=6000),    # 30%
        ]
        out = anaerobic_repeatability(rides, days=7, today=TODAY)
        assert out["ok"] is True
        assert out["source"] == "icu"
        assert out["max_depletion_pct"] == pytest.approx(65.0, abs=0.1)
        assert out["high_depletion_sessions"] == 1
        assert out["moderate_depletion_sessions"] == 2
        assert out["w_prime_divergence"] == pytest.approx(
            out["mean_depletion_pct"] / 100 - 0.30, abs=0.001)

    def test_estimated_fallback(self):
        from advanced_metrics import anaerobic_repeatability
        rides = [self._ride(1, kj=13.0)]  # 13000 J / 20000 J W'
        out = anaerobic_repeatability(rides, days=7, today=TODAY,
                                      w_prime_joules=20000)
        assert out["source"] == "estimated"
        assert out["max_depletion_pct"] == pytest.approx(65.0, abs=0.1)

    def test_no_data(self):
        from advanced_metrics import anaerobic_repeatability
        out = anaerobic_repeatability([{"date": _iso(1)}], days=7, today=TODAY)
        assert out["ok"] is False
        assert out["sessions"] == []

    def test_window_filtering(self):
        from advanced_metrics import anaerobic_repeatability
        rides = [self._ride(20, wp=20000, dep=19000)]
        out = anaerobic_repeatability(rides, days=7, today=TODAY)
        assert out["ok"] is False


# ══════════════════════════════════════════════════════════════════════════════
# ADE governance
# ══════════════════════════════════════════════════════════════════════════════

class TestDecisionEngine:

    def test_recovery_priority_directive(self):
        from ai_coach.decision_engine import compute_ade
        d = compute_ade({"tsb": -35, "hrv_ratio": 0.85})
        assert d["score"] < 80
        assert any(x["item"] == "operational_state" and x["delta"] == -30
                   for x in d["drivers"])
        assert d["directive"] in ("reduce", "recovery_day", "off")

    def test_green_light_full_load(self):
        from ai_coach.decision_engine import compute_ade
        d = compute_ade({"tsb": 28, "hrv_ratio": 1.05, "sleep_score": 92,
                         "risk_flag": "normal", "fatigue_forecast": "green",
                         "load_trend": "increasing"})
        assert d["directive"] == "train_through"
        assert d["score"] <= 100

    def test_missing_signals_low_confidence(self):
        from ai_coach.decision_engine import compute_ade
        d = compute_ade({})
        assert d["signals_available"] == 0
        assert d["confidence"] == 0
        assert d["directive"] in ("train_through", "maintain")

    def test_taper_conflict_penalised(self):
        from ai_coach.decision_engine import compute_ade
        d = compute_ade({"days_to_event": 14, "event_tsb": 25, "tsb": 26,
                         "load_trend": "increasing"})
        assert any(x["item"] == "taper" and x["delta"] < 0
                   for x in d["drivers"])

    def test_clamped_score(self):
        from ai_coach.decision_engine import compute_ade
        worst = {"operational_state": "recovery_priority", "risk_flag": "high",
                 "fatigue_forecast": "red", "load_trend": "increasing",
                 "hrv_ratio": 0.7, "sleep_score": 40, "monotony": 2.5,
                 "ramp_rate": 10}
        d = compute_ade(worst)
        assert d["score"] == 0
        assert d["directive"] == "off"
