import os

with open('app/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'app.include_router(cross_portfolio.router, prefix="/api/v1")' in line:
        new_lines.append(line)
        new_lines.append('app.include_router(copilot.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(forecasting.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(impact.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(observatory.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(federation.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(developer.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(governance.router, prefix="/api/v1")\n')
        new_lines.append('app.include_router(network.router, prefix="/api/v1")\n')
    elif 'from app.routers import cross_portfolio' in line:
        new_lines.append(line)
        new_lines.append('from app.routers import copilot\n')
        new_lines.append('from app.routers import forecasting\n')
        new_lines.append('from app.routers import impact\n')
        new_lines.append('from app.routers import observatory\n')
        new_lines.append('from app.routers import federation\n')
        new_lines.append('from app.routers import developer\n')
        new_lines.append('from app.routers import governance\n')
        new_lines.append('from app.routers import network\n')
    else:
        new_lines.append(line)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
