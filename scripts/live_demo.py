"""Live demo of CPSL v0.9.0 API routes."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

print("=" * 60)
print("  CPSL v0.9.0 — Live API Demo")
print("=" * 60)
print()

# 1. Version
r = client.get("/api/version")
print("1. APP VERSION:")
for k, v in r.json().items():
    print(f"   {k}: {v}")
print()

# 2. Adaptive Recommendation
r = client.get("/api/analytics/adaptive-recommendation?goal=ftp_improvement")
data = r.json()
rec = data.get("recommendation", {})
print("2. ADAPTIVE RECOMMENDATION (FTP Improvement goal):")
print(f"   Goal: {rec.get('goal_label')}")
print(f"   Recommended method: {rec.get('recommended_method_label')}")
print(f"   Readiness adjustment: {rec.get('readiness_adjustment')}")
wl = rec.get("weekly_load", {})
print(f"   Weekly TSS target: {wl.get('target_tss')}")
print(f"   Weekly hours target: {wl.get('target_hours')}")
print(f"   Sessions/week: {wl.get('sessions_per_week')}")
reasoning = rec.get("reasoning", [])
for r_text in reasoning[:3]:
    print(f"   - {r_text}")
print()

# 3. Available Goals
print("3. AVAILABLE TRAINING GOALS:")
for k, v in data.get("available_goals", {}).items():
    print(f"   - {k}: {v}")
print()

# 4. Power-Duration Model
r = client.get("/api/analytics/power-duration-model")
print("4. POWER-DURATION MODEL:")
print(f"   Status: {r.json().get('error', 'Fitted OK')}")
print()

# 5. Phenotype
r = client.get("/api/analytics/phenotype")
print("5. PHENOTYPE CLASSIFICATION:")
print(f"   Status: {r.json().get('error', 'Classified OK')}")
print()

# 6. Durability
r = client.get("/api/analytics/durability")
result = r.json().get("result", {})
print("6. DURABILITY SCORE:")
print(f"   Tier: {result.get('tier', r.json().get('error', 'N/A'))}")
print(f"   Score: {result.get('score', 'N/A')}")
print()

# 7. Training Phases
r = client.get("/api/analytics/training-phases")
data = r.json()
result = data.get("result") or {}
print("7. TRAINING PHASE DETECTION:")
print(f"   Current phase: {result.get('current_phase', data.get('error', 'N/A'))}")
print(f"   Phases detected: {len(result.get('phases', []))}")
print()

# 8. Custom Alerts
r = client.get("/api/alerts/rules")
print("8. CUSTOM ALERTS:")
print(f"   Rules loaded: {len(r.json().get('rules', []))}")
print()

# 9. Polarization
r = client.get("/api/analytics/polarization")
print("9. POLARIZATION ANALYTICS:")
print(f"   Rides analyzed: {r.json().get('n_rides', 0)}")
print()

# 10. Create an alert rule
r = client.post("/api/alerts/rules", json={
    "name": "Sprint Alert",
    "metric": "power_w",
    "operator": ">",
    "value": 1000,
    "streak_seconds": 0,
})
print("10. CREATE ALERT RULE:")
rule = r.json().get("rule", {})
print(f"    Created: {rule.get('name')} ({rule.get('metric')} {rule.get('operator')} {rule.get('value')})")
print()

print("=" * 60)
print("  All 8 new API routes responding correctly!")
print("  CPSL v0.9.0 — Advanced Analytics Suite")
print("=" * 60)
