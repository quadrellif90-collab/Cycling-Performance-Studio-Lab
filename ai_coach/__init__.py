"""AI Coach module for CPSL.

Provides multi-provider LLM integration with 14 supported providers:
  openai, anthropic, google, mistral, deepseek, groq, openrouter,
  ollama, lmstudio, perplexity, replicate, cohere, xai, azure.

All calls use httpx (already in requirements-common.txt), no new dependencies.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .llm_client import LLMClient, get_client
from .weekly_analysis import generate_weekly_analysis
from .plan_generator import generate_weekly_plan, generate_goal_plan
from .friel_coaching import build_friel_assessment, FRIEL_SYSTEM_PROMPT, WEEKLY_ANALYSIS_PROMPT, GENERATE_PLAN_PROMPT

__all__ = [
    "LLMClient",
    "get_client",
    "generate_weekly_analysis",
    "generate_weekly_plan",
    "generate_goal_plan",
    "build_friel_assessment",
    "FRIEL_SYSTEM_PROMPT",
    "WEEKLY_ANALYSIS_PROMPT",
    "GENERATE_PLAN_PROMPT",
]