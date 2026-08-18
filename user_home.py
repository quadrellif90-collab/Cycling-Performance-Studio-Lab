"""Single resolver for the CPSL user-data home (~/.cpsl).

3.4.3 (chip task_23a70236): the dev preview server used to run against the
REAL ~/.cpsl — every live plan-tab browse during development mutated
the owner's actual training data (plan rewrites via the open sequence,
sync markers, readiness flags; it polluted two diagnoses on 2026-07-16).

`CPSL_HOME`, when set, points ALL user-data resolution at that
directory instead. The packaged app never sets it → env absent = exactly
the old behavior (Path.home()/".cpsl"). scripts/dev_preview.sh sets
it to a scratch copy seeded from the real profile.

Import-order contract: this module has NO project imports (stdlib only) so
every module constant (db._USER_DATA, tp.PLAN_DIR, …) can resolve through
it at import time.
"""
from __future__ import annotations

import os
from pathlib import Path


def cpsl_home() -> Path:
    """The user-data root: $CPSL_HOME if set, else ~/.cpsl."""
    env = os.environ.get("CPSL_HOME", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".cpsl"


# Backward-compat alias — domestique modules import ``domestique_home``
domestique_home = cpsl_home
