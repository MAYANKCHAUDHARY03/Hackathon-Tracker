import os

with open('app/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'app.add_middleware(SecurityHeadersMiddleware)' in line:
        new_lines.append('from app.middleware import GlobalScaleMiddleware\n')
        new_lines.append('app.add_middleware(GlobalScaleMiddleware)\n')
        new_lines.append(line)
    elif 'app.include_router(developer.router, prefix="/api/v1")' in line:
        new_lines.append(line)
        if 'app.include_router(governance.router' not in ''.join(lines):
            new_lines.append('app.include_router(governance.router, prefix="/api/v1")\n')
    elif 'from app.routers import developer' in line:
        new_lines.append(line)
        if 'from app.routers import governance' not in ''.join(lines):
            new_lines.append('from app.routers import governance\n')
    else:
        new_lines.append(line)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
