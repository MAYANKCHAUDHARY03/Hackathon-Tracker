from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "services": {
            "database": db_status,
            "api": "ok"
        }
    }

@router.get("/metrics")
async def get_metrics():
    # In a real app, prometheus_client would be used here to return text format.
    # We are returning standard system health metrics for demonstration.
    import psutil
    
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    
    return {
        "system_cpu_usage_percent": cpu,
        "system_memory_usage_percent": mem.percent,
        "system_memory_available_bytes": mem.available
    }
