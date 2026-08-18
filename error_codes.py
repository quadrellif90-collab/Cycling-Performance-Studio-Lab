"""
Error code taxonomy for Cycling Performance Studio Lab.
Each code follows E_<domain>_<failure> pattern.
Severity: FATAL, ERROR, WARN, INFO
"""

from __future__ import annotations
from typing import TypedDict, NotRequired


class CodeMeta(TypedDict):
    severity: str
    description: str
    user_action: NotRequired[str]


class Codes:
    PLAN_PARSE_CORRUPT = "E_PLAN_PARSE_CORRUPT"
    PLAN_LOAD_OSERROR = "E_PLAN_LOAD_OSERROR"
    PLAN_GENERATE_FAILED = "E_PLAN_GENERATE_FAILED"
    PLAN_REFORECAST_FAILED = "E_PLAN_REFORECAST_FAILED"
    PLAN_AUTO_RESTORED = "E_PLAN_AUTO_RESTORED"
    PLAN_ADOPTED_FROM_ROOT = "E_PLAN_ADOPTED_FROM_ROOT"

    ENRICH_FAILED = "E_ENRICH_FAILED"
    ENRICH_LIBRARY_FAILED = "E_ENRICH_LIBRARY_FAILED"
    ENRICH_CLASSIFICATION_FAILED = "E_ENRICH_CLASSIFICATION_FAILED"
    ENRICH_PROPAGATE_FAILED = "E_ENRICH_PROPAGATE_FAILED"
    ENRICH_CARD_STATE_FAILED = "E_ENRICH_CARD_STATE_FAILED"

    CACHE_TRAINING_FAILED = "E_CACHE_TRAINING_FAILED"
    CACHE_SLEEP_FAILED = "E_CACHE_SLEEP_FAILED"
    CACHE_WELLNESS_FAILED = "E_CACHE_WELLNESS_FAILED"
    CACHE_GENERIC_FAILED = "E_CACHE_GENERIC_FAILED"

    CALENDAR_MERGE_FAILED = "E_CALENDAR_MERGE_FAILED"
    CALENDAR_ICU_SYNC_FAILED = "E_CALENDAR_ICU_SYNC_FAILED"
    CALENDAR_RIDES_LOAD_FAILED = "E_CALENDAR_RIDES_LOAD_FAILED"
    CALENDAR_LEGACY_RIDES_FAILED = "E_CALENDAR_LEGACY_RIDES_FAILED"

    AUGMENT_3D_FITNESS_FAILED = "E_AUGMENT_3D_FITNESS_FAILED"
    READINESS_COMPUTE_FAILED = "E_READINESS_COMPUTE_FAILED"

    RIDE_PARSE_FIT = "E_RIDE_PARSE_FIT"
    RIDE_PARSE_ICU = "E_RIDE_PARSE_ICU"
    RIDE_PARSE_GENERIC = "E_RIDE_PARSE_GENERIC"

    PROFILE_LOAD = "E_PROFILE_LOAD"
    PROFILE_SAVE_FAILED = "E_PROFILE_SAVE_FAILED"
    PROFILE_SWITCH_FAILED = "E_PROFILE_SWITCH_FAILED"

    DIAG_HEALTH_CHECK_FAILED = "E_DIAG_HEALTH_CHECK_FAILED"

    FRONTEND_LOAD_HOME_FAILED = "E_FRONTEND_LOAD_HOME_FAILED"
    FRONTEND_LOAD_CAL_FAILED = "E_FRONTEND_LOAD_CAL_FAILED"
    FRONTEND_LOAD_PLAN_FAILED = "E_FRONTEND_LOAD_PLAN_FAILED"
    FRONTEND_RENDER_FAILED = "E_FRONTEND_RENDER_FAILED"
    FRONTEND_UNHANDLED = "E_FRONTEND_UNHANDLED"
    FRONTEND_PROMISE_REJECT = "E_FRONTEND_PROMISE_REJECT"
    FRONTEND_GENERIC = "E_FRONTEND_GENERIC"

    WELLNESS_FETCH_FAILED = "E_WELLNESS_FETCH_FAILED"
    ACTIVITIES_LOOKUP_FAILED = "E_ACTIVITIES_LOOKUP_FAILED"
    TODAY_SESSION_FAILED = "E_TODAY_SESSION_FAILED"
    EFTP_PROGRESS_FAILED = "E_EFTP_PROGRESS_FAILED"

    SYNC_BLOCKING_SLOW = "E_SYNC_BLOCKING_SLOW"

    BIA_PARSE_FAILED = "E_BIA_PARSE_FAILED"
    BIA_VISION_FAILED = "E_BIA_VISION_FAILED"
    HUAWEI_AUTH_FAILED = "E_HUAWEI_AUTH_FAILED"
    HUAWEI_SYNC_FAILED = "E_HUAWEI_SYNC_FAILED"

    INJURY_MANAGER_FAILED = "E_INJURY_MANAGER_FAILED"
    SLEEP_ANALYSIS_FAILED = "E_SLEEP_ANALYSIS_FAILED"
    HRV_ANALYSIS_FAILED = "E_HRV_ANALYSIS_FAILED"

    EXPORT_FAILED = "E_EXPORT_FAILED"
    IMPORT_FAILED = "E_IMPORT_FAILED"
    GPX_PARSE_FAILED = "E_GPX_PARSE_FAILED"


REGISTRY: dict[str, CodeMeta] = {
    Codes.PLAN_PARSE_CORRUPT: {"severity": "ERROR", "description": "Plan file is corrupt or invalid JSON", "user_action": "Restore from backup or recreate plan"},
    Codes.PLAN_LOAD_OSERROR: {"severity": "ERROR", "description": "Failed to read plan file from disk", "user_action": "Check file permissions and disk space"},
    Codes.PLAN_GENERATE_FAILED: {"severity": "ERROR", "description": "Training plan generation failed", "user_action": "Verify profile settings and try again"},
    Codes.PLAN_REFORECAST_FAILED: {"severity": "WARN", "description": "Plan reforecast after ride completion failed", "user_action": "Plan will use previous forecast; reforecast on next ride"},
    Codes.PLAN_AUTO_RESTORED: {"severity": "INFO", "description": "Corrupt plan automatically restored from backup", "user_action": "Review restored plan for correctness"},
    Codes.PLAN_ADOPTED_FROM_ROOT: {"severity": "INFO", "description": "Plan adopted from root profile", "user_action": "Verify plan matches current profile goals"},

    Codes.ENRICH_FAILED: {"severity": "ERROR", "description": "Workout enrichment failed", "user_action": "Check workout library and classification data"},
    Codes.ENRICH_LIBRARY_FAILED: {"severity": "ERROR", "description": "Failed to load workout library for enrichment", "user_action": "Verify workout directory exists and is readable"},
    Codes.ENRICH_CLASSIFICATION_FAILED: {"severity": "WARN", "description": "Workout classification lookup failed", "user_action": "Workout will use filename-based classification fallback"},
    Codes.ENRICH_PROPAGATE_FAILED: {"severity": "WARN", "description": "Failed to propagate enrichment to calendar", "user_action": "Calendar entries may lack detailed workout info"},
    Codes.ENRICH_CARD_STATE_FAILED: {"severity": "WARN", "description": "Failed to compute workout card state", "user_action": "Card may show incomplete information"},

    Codes.CACHE_TRAINING_FAILED: {"severity": "WARN", "description": "Training cache update failed", "user_action": "Data may be stale; will retry on next sync"},
    Codes.CACHE_SLEEP_FAILED: {"severity": "WARN", "description": "Sleep cache update failed", "user_action": "Sleep data may be incomplete"},
    Codes.CACHE_WELLNESS_FAILED: {"severity": "WARN", "description": "Wellness cache update failed", "user_action": "Wellness metrics may be stale"},
    Codes.CACHE_GENERIC_FAILED: {"severity": "WARN", "description": "Generic cache operation failed", "user_action": "Retry automatically scheduled"},

    Codes.CALENDAR_MERGE_FAILED: {"severity": "ERROR", "description": "Failed to merge calendar entries", "user_action": "Check for conflicting entries"},
    Codes.CALENDAR_ICU_SYNC_FAILED: {"severity": "ERROR", "description": "Intervals.icu calendar sync failed", "user_action": "Verify ICU credentials and network connectivity"},
    Codes.CALENDAR_RIDES_LOAD_FAILED: {"severity": "ERROR", "description": "Failed to load rides from calendar", "user_action": "Check ICU API status and credentials"},
    Codes.CALENDAR_LEGACY_RIDES_FAILED: {"severity": "WARN", "description": "Legacy ride format parsing failed", "user_action": "Some historical rides may not appear"},

    Codes.AUGMENT_3D_FITNESS_FAILED: {"severity": "WARN", "description": "3D fitness model augmentation failed", "user_action": "Fitness metrics may use simplified model"},
    Codes.READINESS_COMPUTE_FAILED: {"severity": "WARN", "description": "Readiness score computation failed", "user_action": "Check HRV, sleep, and training load data availability"},

    Codes.RIDE_PARSE_FIT: {"severity": "ERROR", "description": "FIT file parsing failed", "user_action": "Verify file is valid FIT format; try re-exporting from device"},
    Codes.RIDE_PARSE_ICU: {"severity": "ERROR", "description": "ICU ride data parsing failed", "user_action": "Check ICU API response format"},
    Codes.RIDE_PARSE_GENERIC: {"severity": "ERROR", "description": "Generic ride parsing failed", "user_action": "File format not recognized or corrupt"},

    Codes.PROFILE_LOAD: {"severity": "ERROR", "description": "Failed to load athlete profile", "user_action": "Check profile directory permissions and athlete.json validity"},
    Codes.PROFILE_SAVE_FAILED: {"severity": "ERROR", "description": "Failed to save athlete profile", "user_action": "Check disk space and write permissions"},
    Codes.PROFILE_SWITCH_FAILED: {"severity": "ERROR", "description": "Profile switch failed", "user_action": "Try again; check for database locks"},

    Codes.DIAG_HEALTH_CHECK_FAILED: {"severity": "WARN", "description": "System health check failed", "user_action": "Review diagnostics endpoint for details"},

    Codes.FRONTEND_LOAD_HOME_FAILED: {"severity": "ERROR", "description": "Frontend home page load failed", "user_action": "Refresh page; check browser console"},
    Codes.FRONTEND_LOAD_CAL_FAILED: {"severity": "ERROR", "description": "Frontend calendar load failed", "user_action": "Refresh page; check network tab"},
    Codes.FRONTEND_LOAD_PLAN_FAILED: {"severity": "ERROR", "description": "Frontend plan load failed", "user_action": "Refresh page; verify profile has active plan"},
    Codes.FRONTEND_RENDER_FAILED: {"severity": "ERROR", "description": "Frontend render error", "user_action": "Refresh page; report if persistent"},
    Codes.FRONTEND_UNHANDLED: {"severity": "ERROR", "description": "Unhandled frontend error", "user_action": "Refresh page; check browser console for details"},
    Codes.FRONTEND_PROMISE_REJECT: {"severity": "ERROR", "description": "Unhandled promise rejection in frontend", "user_action": "Refresh page; report if persistent"},
    Codes.FRONTEND_GENERIC: {"severity": "ERROR", "description": "Generic frontend error", "user_action": "Refresh page"},

    Codes.WELLNESS_FETCH_FAILED: {"severity": "WARN", "description": "Wellness data fetch from ICU failed", "user_action": "Check ICU credentials and API status"},
    Codes.ACTIVITIES_LOOKUP_FAILED: {"severity": "WARN", "description": "Activity lookup failed", "user_action": "Retry automatically scheduled"},
    Codes.TODAY_SESSION_FAILED: {"severity": "WARN", "description": "Today's session computation failed", "user_action": "Check plan and calendar data"},
    Codes.EFTP_PROGRESS_FAILED: {"severity": "WARN", "description": "eFTP progress computation failed", "user_action": "eFTP chart may be incomplete"},

    Codes.SYNC_BLOCKING_SLOW: {"severity": "WARN", "description": "Sync operation blocking longer than expected", "user_action": "Wait for completion; check network if persistent"},

    Codes.BIA_PARSE_FAILED: {"severity": "ERROR", "description": "BIA PDF parsing failed", "user_action": "Verify PDF is a valid BIA report format"},
    Codes.BIA_VISION_FAILED: {"severity": "ERROR", "description": "BIA Vision API request failed", "user_action": "Check API key and network connectivity"},
    Codes.HUAWEI_AUTH_FAILED: {"severity": "ERROR", "description": "Huawei Health authentication failed", "user_action": "Re-authenticate in settings"},
    Codes.HUAWEI_SYNC_FAILED: {"severity": "ERROR", "description": "Huawei Health data sync failed", "user_action": "Check Terra API status and credentials"},

    Codes.INJURY_MANAGER_FAILED: {"severity": "ERROR", "description": "Injury manager operation failed", "user_action": "Check injury data integrity"},
    Codes.SLEEP_ANALYSIS_FAILED: {"severity": "WARN", "description": "Sleep analysis computation failed", "user_action": "Sleep metrics may be incomplete"},
    Codes.HRV_ANALYSIS_FAILED: {"severity": "WARN", "description": "HRV analysis computation failed", "user_action": "HRV metrics may be incomplete"},

    Codes.EXPORT_FAILED: {"severity": "ERROR", "description": "Data export failed", "user_action": "Check disk space and permissions"},
    Codes.IMPORT_FAILED: {"severity": "ERROR", "description": "Data import failed", "user_action": "Verify file format and try again"},
    Codes.GPX_PARSE_FAILED: {"severity": "ERROR", "description": "GPX file parsing failed", "user_action": "Verify GPX is valid and not corrupt"},
}


def is_valid_code(code: str) -> bool:
    return code in REGISTRY


def all_codes() -> list[str]:
    return sorted(REGISTRY.keys())


def metadata(code: str) -> CodeMeta | None:
    return REGISTRY.get(code)


def _log_error(code: str, exc: Exception | None = None, **context) -> None:
    """Single funnel for structured error logging with E_<domain>_<failure> codes."""
    from datetime import datetime, timezone
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "code": code,
        "message": str(exc) if exc else "",
        "context": context,
    }
    
    # Log via standard logging
    import logging
    meta = REGISTRY.get(code)
    if meta:
        level = getattr(logging, meta["severity"], logging.ERROR)
        logger = logging.getLogger(__name__)
        logger.log(level, f"[{code}] {meta['description']} | {entry}")