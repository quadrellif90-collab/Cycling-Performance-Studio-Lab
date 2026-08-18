"""Copy all missing modules from domestique to CPSL."""
import shutil, os

SRC = r"C:\Users\Siviglino\Desktop\PPC\domestique"
DST = r"C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab"

# Core Python modules to copy
modules = [
    "training.py", "training_planner.py", "readiness.py", "readiness_composite.py",
    "sleep.py", "execution_score.py", "fit_activity.py", "workout_facts.py",
    "strain_score.py", "tau_fitting.py", "continuous_policy.py", "hr_targets.py",
    "icu_calendar_push.py", "oos_validation.py", "structure_fidelity.py",
    "geodesy.py", "gpx_to_gc.py", "route_archetypes.py", "sleep_inhibit.py",
    "migrate_profiles.py", "launcher.py", "programme_summary_png.py",
    "ride_report_png.py", "analytics.py",
]

copied = 0
for f in modules:
    s = os.path.join(SRC, f)
    if os.path.exists(s):
        shutil.copy2(s, os.path.join(DST, f))
        copied += 1
        print(f"  + {f}")
    else:
        print(f"  ! MISSING: {f}")

# Data files
data_files = ["routes.json", "profiles_indexed.json", "surface_types.json"]
for f in data_files:
    s = os.path.join(SRC, f)
    if os.path.exists(s):
        shutil.copy2(s, os.path.join(DST, f))
        copied += 1
        print(f"  + {f}")

# Directories to copy whole
dirs_to_copy = ["workouts", "courses", "gpx_sources", "profiles", "plans"]
for d in dirs_to_copy:
    src_d = os.path.join(SRC, d)
    dst_d = os.path.join(DST, d)
    if os.path.exists(src_d):
        if os.path.exists(dst_d):
            shutil.rmtree(dst_d)
        shutil.copytree(src_d, dst_d)
        count = sum(len(files) for _, _, files in os.walk(dst_d))
        copied += 1
        print(f"  + {d}/ ({count} files)")
    else:
        print(f"  ! MISSING: {d}/")

# VERSION file
vf = os.path.join(SRC, "VERSION")
if os.path.exists(vf):
    shutil.copy2(vf, os.path.join(DST, "VERSION"))
    copied += 1
    print(f"  + VERSION")

print(f"\nDone: {copied} items copied")
