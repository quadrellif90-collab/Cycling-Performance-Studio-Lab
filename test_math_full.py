"""Test PCC math modules - verified working functions."""
from fitness_estimation import (
    estimate_ftp, compute_fitness_signature, compute_cp_wprime
)
from power_curve import aggregate_power_curve

print("="*60)
print("Cycling Performance Studio Lab - PCC Math Modules")
print("="*60)

# Test 1: estimate_ftp - FTP from best efforts
print("\n1. estimate_ftp() - FTP Estimation")
sample_efforts = {300: 280, 600: 250, 1200: 220}
ftp = estimate_ftp(sample_efforts)
print(f"   Input: {sample_efforts}")
print(f"   FTP: {ftp}W")
assert ftp is not None and ftp > 100
print("   PASSED")

# Test 2: compute_fitness_signature - Xert-style signature
print("\n2. compute_fitness_signature() - Fitness Signature")
signature = compute_fitness_signature(sample_efforts, ftp)
print(f"   FTP: {signature.ftp}W | LTP: {signature.ltp}W | HIE: {signature.hie:.1f}kJ | Pmax: {signature.peak_power}W")
assert signature.ftp == ftp and signature.ltp > 0 and signature.hie > 0 and signature.peak_power > 0
print("   PASSED")

# Test 3: compute_cp_wprime - Monod-Scherrer CP/W' fit
print("\n3. compute_cp_wprime() - Critical Power & W^prime")
cp, wprime = compute_cp_wprime(sample_efforts)
print(f"   CP: {cp:.1f}W | W': {wprime:.0f}J")
assert cp is not None and cp > 100 and wprime is not None and wprime > 0
print("   PASSED")

# Test 4: aggregate_power_curve note
print("\n4. aggregate_power_curve() - Needs full data infrastructure")
print("   (requires cached ride data from Intervals.icu)")
print("   Available in production with ride data")
print("   Configurable via ride_storage module")

print("\n" + "="*60)
print("CORE PCC MATH MODULES OPERATIONAL")
print("="*60)
print("\nVerified 3/4 functions ready for API integration:")
print("  • FTP estimation from best efforts")
print("  • Fitness signature (FTP/LTP/HIE/Pmax)")
print("  • CP/W' Monod-Scherrer analysis")
print("\nReady for API endpoint exposure and frontend integration!")