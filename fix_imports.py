#!/usr/bin/env python3
import os

os.chdir(r'C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab')

# Fix weekly_analysis.py
with open('ai_coach/weekly_analysis.py', 'r') as f:
    content = f.read()
content = content.replace('from training_phase_detector import detect_phase', 'from training_phase_detector import detect_training_phases')
with open('ai_coach/weekly_analysis.py', 'w') as f:
    f.write(content)
print('Fixed weekly_analysis.py')

# Fix plan_generator.py  
with open('ai_coach/plan_generator.py', 'r') as f:
    content = f.read()
content = content.replace('from training_phase_detector import detect_phase', 'from training_phase_detector import detect_training_phases')
with open('ai_coach/plan_generator.py', 'w') as f:
    f.write(content)
print('Fixed plan_generator.py')

# Fix friel_coaching.py
with open('ai_coach/friel_coaching.py', 'r') as f:
    content = f.read()
content = content.replace('from training_phase_detector import detect_phase', 'from training_phase_detector import detect_training_phases')
with open('ai_coach/friel_coaching.py', 'w') as f:
    f.write(content)
print('Fixed friel_coaching.py')