"""
Global configuration constants for Cycling Performance Studio Lab.
Per-profile values are resolved dynamically via ProfileManager proxy (see __getattr__).
"""

from __future__ import annotations

ICU_BASE = "https://intervals.icu/api/v1"
ICU_OAUTH_AUTHORIZE = "https://intervals.icu/oauth/authorize"
ICU_OAUTH_TOKEN = "https://intervals.icu/oauth/token"
ICU_OAUTH_CLIENT_ID = "511"
ICU_OAUTH_REDIRECT_PATH = "/oauth/callback"
ICU_OAUTH_SCOPES = "ACTIVITY:READ,WELLNESS:READ,LIBRARY:READ,CALENDAR:WRITE"

TERRA_BASE = "https://api.tryterra.co/v2"

DOMESTIQUE_PORT = 22400

WEEKLY_LIT_PCT = 0.80
WEEKLY_HIT_PCT = 0.20
MAX_HIT_PER_WEEK = 2

ACWR_GREEN_LOW = 0.85
ACWR_GREEN_HIGH = 1.15
ACWR_ORANGE_HIGH = 1.25

RAMP_RATE_GREEN = 5.0
RAMP_RATE_ORANGE = 10.0

TSB_RED_LINE = -30.0

SLEEP_GREEN = 7.5
SLEEP_ORANGE = 6.5

EA_OPTIMAL = 45.0
EA_SAFE = 35.0
EA_DANGER = 30.0

PROFILE_SCHEMA_VERSION = 4
_PROFILE_ID_RE = r'^[a-z0-9][a-z0-9_-]{0,31}$'

PRESET_COLORS = [
    "blue", "green", "orange", "purple",
    "red", "yellow", "cyan", "pink"
]

STANDARD_DURATIONS = [1, 5, 15, 30, 60, 120, 300, 480, 600, 1200, 1800, 3600]
MONOD_DURATIONS_S = (180, 300, 600, 1200)
MONOD_MIN_POINTS = 3
MONOD_R2_MIN = 0.90

FTP_SCALING_FACTORS = {
    300: 0.80,
    480: 0.86,
    1200: 0.95,
    1800: 0.97,
    3600: 1.00,
}
MIN_FTP_EFFORT_DURATION = 300

_PG_2011_W_PER_KG = {
    1: 23.7, 5: 14.9, 15: 9.7, 30: 7.5,
    60: 6.3, 120: 5.4, 300: 4.8, 480: 4.4,
    600: 4.2, 1200: 3.8, 1800: 3.5, 3600: 3.1,
}

SYNC_GATE_TIMEOUT_S = 10.0

WORK_FLOOR_FRAC = 0.75
TOL_FRAC = 0.05
TOL_MIN_W = 10.0
TRANSIENT_GRACE_S = 3
ALIGN_MAX_OFFSET_S = 120
MISSING_BELOW_FLOOR_FRAC = 0.5
MISSING_TARGET_FRAC = 0.90


class _ConfigProxy:
    def __getattr__(self, name: str):
        # Check if it's a module-level config constant
        import config as _cfg
        if hasattr(_cfg, name):
            return getattr(_cfg, name)
        
        from profile_manager import ProfileManager, get as pm_get
        pm = pm_get()
        mapping = {
            "ATHLETE_FTP_W": lambda: pm.ftp,
            "ATHLETE_WEIGHT_KG": lambda: pm.weight_kg,
            "ATHLETE_LBM_KG": lambda: pm.lbm_kg,
            "ATHLETE_LTHR": lambda: pm.lthr,
            "ATHLETE_MAX_HR": lambda: pm.max_hr,
            "ATHLETE_CP_W": lambda: pm.cp,
            "ATHLETE_WPRIME_J": lambda: pm.wprime_j,
            "ATHLETE_PMAX_W": lambda: pm.pmax_w,
            "ATHLETE_AGE": lambda: getattr(pm, "age", None),
            "ATHLETE_SEX": lambda: getattr(pm, "sex", None),
            "TARGET_MODE": lambda: pm.target_mode,
            "CAP_SHORT_INTERVALS": lambda: pm.cap_short_intervals,
            "ICU_ATHLETE_ID": lambda: pm.icu_athlete_id,
            "ICU_API_KEY": lambda: pm.icu_api_key,
            "ICU_ACCESS_TOKEN": lambda: pm.icu_access_token,
            "ICU_NAME": lambda: pm.icu_name,
            "BIA_VISION_API_KEY": lambda: pm.bia_vision_api_key,
            "BIA_VISION_BASE_URL": lambda: pm.bia_vision_base_url,
            "BIA_VISION_MODEL": lambda: pm.bia_vision_model,
        }
        if name in mapping:
            return mapping[name]()
        raise AttributeError(f"Config has no attribute {name!r}")


config = _ConfigProxy()