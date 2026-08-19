#!/usr/bin/env python3
with open("ai_coach/plan_generator.py", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

# Fix line 149 (index 148)
for i, line in enumerate(lines):
    if i == 148:  # line 149
        # Replace the problematic line
        lines[i] = 'Dati_analysis = str(analysis).replace("{", "").replace("}", "")\n'

with open("ai_coach/plan_generator.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Fixed line 149")