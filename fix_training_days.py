import os
os.chdir(r'C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab')

with open('ai_coach/plan_generator.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Fix the problematic list comprehension
old = "training_days = [i for i in range(days_per_week) if not rest_days[i % len(rest_days)] if rest_days else True]"
new = "training_days = []\n    for i in range(days_per_week):\n        is_rest = rest_days[i % len(rest_days)] if rest_days else False\n        if not is_rest:\n            training_days.append(i)"

content = content.replace(old, new)

with open('ai_coach/plan_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed training_days')