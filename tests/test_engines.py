"""Unit tests for CPSL core engines (no DB / no network).

Run:  ./.venv/Scripts/python.exe -m pytest tests/ -q
"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hrv_engine import compute_baseline, rolling_average, hrv_deviation
from zones import power_zones, hr_zones, power_zone_at, estimated_hr_max
from durability_score import compute_durability_score


# ───────────────────────── HRV ENGINE ─────────────────────────
def test_compute_baseline_basic():
    daily = [
        {"date": "2026-01-01", "rmssd_ms": 50.0, "ln_rmssd_ms": math.log(50.0)},
        {"date": "2026-01-02", "rmssd_ms": 60.0, "ln_rmssd_ms": math.log(60.0)},
        {"date": "2026-01-03", "rmssd_ms": 70.0, "ln_rmssd_ms": math.log(70.0)},
    ]
    base = compute_baseline(daily, window_days=7)
    assert base["count"] == 3
    assert abs(base["mean_rmssd"] - 60.0) < 1e-6
    assert "mean_ln_rmssd" in base


def test_compute_baseline_empty():
    base = compute_baseline([], window_days=7)
    assert base["count"] == 0


def test_rolling_average_7d():
    daily = [{"date": f"2026-01-0{i}", "rmssd_ms": float(10 * i)} for i in range(1, 6)]
    # 01..05 -> rmssd 10..50
    roll = rolling_average(daily, days=3)
    # first window (01) alone = 10
    assert roll[0]["rolling_3d"] == 10.0
    # last (05) window 03,04,05 = (30+40+50)/3 = 40
    assert abs(roll[-1]["rolling_3d"] - 40.0) < 1e-6


def test_hrv_deviation_sign():
    dev = hrv_deviation(55.0, 50.0)
    assert "deviation_pct" in dev
    assert dev["deviation_pct"] > 0  # higher than baseline -> positive


# ───────────────────────── ZONES ─────────────────────────
def test_power_zones_monotonic():
    zs = power_zones(200)
    watts = [z.low for z in zs] + [zs[-1].high]
    assert watts == sorted(watts), "zones must be ordered"
    # Z1 low is 0-based fraction of FTP
    assert zs[0].low == 0


def test_power_zone_at():
    zs = power_zones(200)
    # threshold ~55% FTP = 110W is Z1/Z2 boundary; pick a clear Z2 value
    z = power_zone_at(150, 200)  # 75% FTP -> Z2/Z3 area
    assert 1 <= z <= 7


def test_hr_zones_requires_lthr():
    zs = hr_zones(170)
    assert len(zs) >= 5
    # each zone's low < high
    for z in zs:
        assert z.low < z.high or z.high is None


def test_estimated_hr_max():
    # Tanaka 208 - 0.7*age
    assert estimated_hr_max(40) == 208 - 28


# ───────────────────────── DURABILITY ─────────────────────────
def test_durability_score_runs():
    rides = [
        {"power_stream": [200, 210, 220, 230, 240, 250], "duration_sec": 300},
        {"power_stream": [180, 190, 195, 200, 205, 210], "duration_sec": 300},
    ]
    res = compute_durability_score(rides)
    assert hasattr(res, "score")
    assert 0 <= res.score <= 100
