import asyncio
import psutil
from datetime import datetime
from sqlalchemy import select, func
from app.database import async_session_maker
from app.models.user import User
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon

async def generate_health_summary():
    print(f"--- Weekly Health Check Summary: {datetime.now().strftime('%Y-%m-%d')} ---")
    
    # 1. System Performance
    print("\n[1] Performance Trend (Current Snapshot)")
    print(f"  - CPU Usage: {psutil.cpu_percent()}%")
    print(f"  - Memory Usage: {psutil.virtual_memory().percent}%")
    
    # 2. Application Errors
    print("\n[2] Error Rate")
    print("  - Application Logs: Structured JSON logging is active via app.main")
    print("  - Centralized Error Tracking (e.g., Sentry): MISSING")
    
    # 3. Usage Patterns
    try:
        async with async_session_maker() as session:
            user_count = (await session.execute(select(func.count(User.id)))).scalar()
            workspace_count = (await session.execute(select(func.count(Workspace.id)))).scalar()
            hackathon_count = (await session.execute(select(func.count(Hackathon.id)))).scalar()
            
        print("\n[3] Usage Patterns (Database Entities)")
        print(f"  - Total Users: {user_count}")
        print(f"  - Total Workspaces: {workspace_count}")
        print(f"  - Total Hackathons: {hackathon_count}")
    except Exception as e:
        print(f"\n[3] Usage Patterns Error: Could not connect to database - {e}")
        
    print("\n[4] Telemetry & Widget Tracking")
    print("  - Frontend Page/Widget Usage: MISSING (No PostHog/Mixpanel installed)")

if __name__ == "__main__":
    asyncio.run(generate_health_summary())
