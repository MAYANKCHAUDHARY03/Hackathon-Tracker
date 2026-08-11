import os

with open('app/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'app.include_router(governance.router, prefix="/api/v1")' in line:
        new_lines.append(line)
        if 'app.include_router(network.router' not in ''.join(lines):
            new_lines.append('app.include_router(network.router, prefix="/api/v1")\n')
    elif 'from app.routers import governance' in line:
        new_lines.append(line)
        if 'from app.routers import network' not in ''.join(lines):
            new_lines.append('from app.routers import network\n')
    else:
        new_lines.append(line)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
