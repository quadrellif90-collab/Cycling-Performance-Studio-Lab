import sys
sys.path.insert(0, ".")
try:
    import config
    print("config.py OK")
except Exception as e:
    print(f"config.py ERROR: {e}")

try:
    from ai_coach import get_client, generate_weekly_analysis, generate_weekly_plan, generate_goal_plan
    print("ai_coach import OK")
except Exception as e:
    print(f"ai_coach import ERROR: {e}")

try:
    from ai_coach.llm_client import LLMClient
    print("ai_coach.llm_client OK")
except Exception as e:
    print(f"ai_coach.llm_client ERROR: {e}")

try:
    from ai_coach.weekly_analysis import generate_weekly_analysis
    print("ai_coach.weekly_analysis OK")
except Exception as e:
    print(f"ai_coach.weekly_analysis ERROR: {e}")

try:
    from ai_coach.plan_generator import generate_weekly_plan, generate_goal_plan
    print("ai_coach.plan_generator OK")
except Exception as e:
    print(f"ai_coach.plan_generator ERROR: {e}")

try:
    from ai_coach.friel_coaching import build_friel_assessment, FRIEL_SYSTEM_PROMPT, WEEKLY_ANALYSIS_PROMPT, GENERATE_PLAN_PROMPT
    print("ai_coach.friel_coaching OK")
except Exception as e:
    print(f"ai_coach.friel_coaching ERROR: {e}")