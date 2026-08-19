#!/usr/bin/env python3
import os
os.chdir(r'C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab')

with open('ai_coach/plan_generator.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Fix the system_prompt line (around line 226)
for i, line in enumerate(lines):
    if 'system_prompt = f' in line and '"""' in line:
        # Replace the f-string with regular string
        # Keep the content but remove the f prefix
        new_line = line.replace('system_prompt = f', 'system_prompt =')
        lines[i] = new_line
        # Also fix the content - remove the curly braces that were f-string placeholders
        # But keep them as literal text since we're not using f-string anymore
        break

with open('ai_coach/plan_generator.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Applied simple fix')