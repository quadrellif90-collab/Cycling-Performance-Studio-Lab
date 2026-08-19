#!/usr/bin/env python3
"""Add HRV monitor route to app.py"""

with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

old_block = """# Workout Player page
@app.get("/player/{workout_filename}", response_class=HTMLResponse)
def workout_player_page(request: Request, workout_filename: str = ""):
    """Serve the workout player UI for a given .zwo file."""
    from workout_player import resolve_workout_path, ZWOParser
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    ftp = pm.active_profile.get("ftp", 250.0) if pm.active_profile else 250.0

    workout_data = None
    if workout_filename:
        path = resolve_workout_path(workout_filename)

        workout_data = {
            "name": timeline.name,
            "description": timeline.description,
            "author": timeline.author,
            "duration_total": round(timeline.duration_total, 1),
            "ftp": timeline.ftp,
            "intervals": timeline.get_intervals_summary(),
        }

    return templates.TemplateResponse(
        request=request, name="workout_player.html",
        context={
            "workout": workout_data,
            "workout_filename": workout_filename,
            "active_profile_id": pm.active_id or "",
        })


if __name__ == "__new_block":"""

# Actually, let me just find the line number and insert after it
import re

# Find the "# Workout Player page" line
lines = content.split('\n')
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if '# Workout Player page' in line and i > 23090 and i < 23100:
        # Add the HRV monitor route after this block
        # Find the "if __name__ == "__main__":" line
        pass

# Simple approach: replace the "if __name__" block
target = '''if __name__ == "__main__":'''

replacement = '''if __name__ == "__main__":'''

# Actually, let's just insert the HRV route before the "if __name__" line
# Find the index of the if __name__ line
for i, line in enumerate(new_lines):
    if line.strip() == 'if __name__ == "__main__":':
        # Insert before this line
        hrv_route = '''# HRV Monitor page
@app.get("/hrv", response_class=HTMLResponse)
def hrv_monitor_page(request: Request):
    """Serve the HRV monitoring UI."""
    from profile_manager import ProfileManager
    pm = ProfileManager.get()
    return templates.TemplateResponse(
        request=request, name="hrv_monitor.html",
        context={"active_profile_id": pm.active_id or ""})


'''
        new_lines.insert(i, hrv_route)
        print(f"Inserted HRV route at line {i+1}")
        break

with open('app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print("Done")