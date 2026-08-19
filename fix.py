import os
os.chdir(r'C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab')
with open('ai_coach/plan_generator.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if i == 148:
        lines[i] = 'Dati_analysis = str(analysis).replace("{", "").replace("}", "")\n'
with open('ai_coach/plan_generator.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed')