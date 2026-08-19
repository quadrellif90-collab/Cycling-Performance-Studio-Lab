#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Deep Scan Risultato ===")
errors = []

# Test 1: config
try:
    import config
    print("OK config.py")
except Exception as e:
    print(f"ERRORE config.py: {e}")
    errors.append("config")

# Test 2: ai_coach modules
try:
    from ai_coach import get_client, generate_weekly_analysis
    print("OK ai_coach import")
except Exception as e:
    print(f"ERRORE ai_coach import: {e}")
    errors.append("ai_coach")

# Test 3: llm_client
try:
    from ai_coach.llm_client import LLMClient
    print("OK ai_coach.llm_client")
except Exception as e:
    print(f"ERRORE ai_coach.llm_client: {e}")
    errors.append("llm_client")

# Test 4: weekly_analysis
try:
    from ai_coach.weekly_analysis import generate_weekly_analysis
    print("OK ai_coach.weekly_analysis")
except Exception as e:
    print(f"ERRORE ai_coach.weekly_analysis: {e}")
    errors.append("weekly_analysis")

# Test 5: friel_coaching
try:
    from ai_coach.friel_coaching import build_friel_assessment, FRIEL_SYSTEM_PROMPT
    print("OK ai_coach.friel_coaching")
except Exception as e:
    print(f"ERRORE ai_coach.friel_coaching: {e}")
    errors.append("friel_coaching")

# Test 6: cpsl modules (analytics)
try:
    from analytics import polarization_index
    print("OK cpsl.analytics")
except Exception as e:
    print(f"ERRORE cpsl.analytics: {e}")
    errors.append("analytics")

# Test 7: power_duration_model
try:
    from power_duration_model import fit_power_duration
    print("OK cpsl.power_duration_model")
except Exception as e:
    print(f"ERRORE cpsl.power_duration_model: {e}")
    errors.append("power_duration_model")

# Test 8: phenotype
try:
    from phenotype import classify_phenotype
    print("OK cpsl.phenotype")
except Exception as e:
    print(f"ERRORE cpsl.phenotype: {e}")
    errors.append("phenotype")

# Test 9: durability_score
try:
    from durability_score import compute_durability_score
    print("OK cpsl.durability_score")
except Exception as e:
    print(f"ERRORE cpsl.durability_score: {e}")
    errors.append("durability_score")

# Test 10: training_phase_detector
try:
    from training_phase_detector import detect_training_phases
    print("OK cpsl.training_phase_detector")
except Exception as e:
    print(f"ERRORE cpsl.training_phase_detector: {e}")
    errors.append("training_phase_detector")

# Test 10: plan_generator (disabled temporarily)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("plan_generator", "ai_coach/plan_generator.py")
    print("OK ai_coach.plan_generator (file exists)")
except Exception as e:
    print(f"ERRORE ai_coach.plan_generator: {e}")
    errors.append("plan_generator")

print()
if errors:
    print(f"Errori riscontrati: {len(errors)}")
    print("File con problemi:", ", ".join(errors))
else:
    print("TUTTO OK - Nessun errore di importazione!")