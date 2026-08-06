import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.exceptions import CustomException, custom_exception_handler
from app.middleware import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

from app.limiter import limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecurityHeadersMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_exception_handler(CustomException, custom_exception_handler)

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "error"
        
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "environment": settings.ENVIRONMENT,
        "api_version": settings.API_V1_STR,
        "database": db_status
    }

from app.routers import auth, users, workspaces, hackathons, dashboard, invitations, teams, projects, kanban, activity, rounds, submissions, notifications, mentors, judges, evaluations, outcomes, search, analytics, export_import, portfolio

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(workspaces.router, prefix=f"{settings.API_V1_STR}", tags=["workspaces"])
app.include_router(invitations.router, prefix=f"{settings.API_V1_STR}", tags=["invitations"])
app.include_router(hackathons.router, prefix=f"{settings.API_V1_STR}", tags=["hackathons"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}", tags=["dashboard"])
app.include_router(teams.router, prefix=f"{settings.API_V1_STR}", tags=["teams"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}", tags=["projects"])
app.include_router(kanban.router, prefix=f"{settings.API_V1_STR}", tags=["kanban"])
app.include_router(activity.router, prefix=f"{settings.API_V1_STR}", tags=["activity"])
app.include_router(rounds.router, prefix=f"{settings.API_V1_STR}", tags=["rounds"])
app.include_router(submissions.router, prefix=f"{settings.API_V1_STR}", tags=["submissions"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}", tags=["notifications"])
app.include_router(mentors.router, prefix=f"{settings.API_V1_STR}", tags=["mentors"])
app.include_router(judges.router, prefix=f"{settings.API_V1_STR}", tags=["judges"])
app.include_router(evaluations.router, prefix=f"{settings.API_V1_STR}", tags=["evaluations"])
app.include_router(outcomes.router, prefix=f"{settings.API_V1_STR}", tags=["outcomes"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}", tags=["search"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}", tags=["analytics"])
app.include_router(export_import.router, prefix=f"{settings.API_V1_STR}", tags=["export_import"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}", tags=["portfolio"])
