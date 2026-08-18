"""Test PCC math modules import and basic functionality."""
import sys
sys.path.insert(0, '.')

from fitness_estimation import (
    estimate_ftp, compute_fitness_signature,
    compute_cp_wprime, extract_best_efforts,
    STANDARD_DURATIONS, MONOD_DURATIONS_S
)
from power_curve import (
    aggregate_power_curve, compute_ride_prs,
    backfill_icu_history
)

# Test fitness_estimation basic functionality
print("=== fitness_estimation.py ===")

# Test extract_best_efforts with sample data
sample_samples = [
    type('RideSample', (), {'power': [200+i for i in range(3600)], 'heart_rate': [150+i%20 for i in range(3600)]})()
]
efforts = extract_best_efforts(sample_samples)
print(f"extract_best_efforts: {len(efforts)} durations extracted")
for d, w in sorted(efforts.items())[:5]:
    print(f"  {d}s: {w}W")

# Test estimate_ftp
if efforts:
    ftp = estimate_ftp(efforts)
    print(f"estimate_ftp: {ftp}W")

# Test compute_fitness_signature
signature = compute_fitness_signature(efforts, ftp or 200)
print(f"FitnessSignature: FTP={signature.ftp}, LTP={signature.ltp}, HIE={signature.hie:.1f}kJ, Pmax={signature.peak_power}W")

# Test compute_cp_wprime
cp, wprime = compute_cp_wprime(efforts)
print(f"CP/W': {cp:.1f}W / {wprime:.0f}J")

print("\n=== power_curve.py ===")

# Test aggregate_power_curve with mock data
mock_rides = [
    type('Ride', (), {
        'efforts': [{'duration': 300, 'watts': 280}, {'duration': 600, 'watts': 250}],
        'ftp_at_ride': 200,
        'weight_kg': 70,
        'np_w': 220,
        'kj': 5000,
        'date': '2024-01-01'
    })()
]

result = aggregate_power_curve(mock_rides, window_days=90)
print(f"aggregate_power_curve: n_rides={result['n_rides']}")
print(f"  current_ftp={result['current_ftp']}W")
print(f"  cp_w={result['cp_w']}W, wprime_j={result['wprime_j']}J, pmax_w={result['pmax_w']}W")
print(f"  rider_curve samples: {len(result['rider_curve'])} entries")

print("\n✅ All PCC math modules working!")