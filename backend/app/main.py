import logging
import json
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

from app.config import settings
from app.database import get_db
from app.core.graph_events import register_graph_events

# Register graph events
register_graph_events()

from app.exceptions import CustomException, custom_exception_handler
from app.middleware import SecurityHeadersMiddleware
from app.core.event_bus import event_bus
from app.plugins.plugin_manager import plugin_manager
from app.services.integration_dispatcher import register_integration_dispatcher
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components
    logger.info("Initializing plugins and event bus...")
    plugin_manager.discover_plugins("app.plugins.installed")
    plugin_manager.initialize_plugins(event_bus)
    register_integration_dispatcher()
    yield
    # Cleanup on shutdown
    pass

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

from app.limiter import limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.middleware import GlobalScaleMiddleware
app.add_middleware(GlobalScaleMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

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

from app.routers import auth, users, workspaces, hackathons, dashboard, invitations, teams, projects, kanban, activity, rounds, submissions, notifications, mentors, judges, evaluations, outcomes, search, analytics, export_import, portfolio, automation, integration, ai, hub_integrations, audit, webhook, graph, opportunities, marketplace
from app.routers import verification

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(workspaces.router, prefix=f"{settings.API_V1_STR}", tags=["workspaces"])
app.include_router(verification.router, prefix=f"{settings.API_V1_STR}", tags=["Verification"])
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
app.include_router(hub_integrations.router, prefix=f"{settings.API_V1_STR}", tags=["hub_integrations"])
app.include_router(mentors.router, prefix=f"{settings.API_V1_STR}", tags=["mentors"])
app.include_router(judges.router, prefix=f"{settings.API_V1_STR}", tags=["judges"])
app.include_router(evaluations.router, prefix=f"{settings.API_V1_STR}", tags=["evaluations"])
app.include_router(outcomes.router, prefix=f"{settings.API_V1_STR}", tags=["outcomes"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}", tags=["search"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}", tags=["analytics"])
app.include_router(export_import.router, prefix=f"{settings.API_V1_STR}", tags=["export_import"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}", tags=["portfolio"])
app.include_router(automation.router, prefix=f"{settings.API_V1_STR}", tags=["automation"])
app.include_router(integration.router, prefix=f"{settings.API_V1_STR}", tags=["integration"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}", tags=["ai_intelligence"])
app.include_router(opportunities.router, prefix=f"{settings.API_V1_STR}", tags=["opportunities"])
from app.routers import matching
app.include_router(matching.router, prefix=f"{settings.API_V1_STR}", tags=["matching"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}", tags=["audit"])
app.include_router(webhook.router, prefix=f"{settings.API_V1_STR}", tags=["webhook"])

from app.routers import api_keys
app.include_router(api_keys.router, prefix=f"{settings.API_V1_STR}", tags=["api_keys"])
app.include_router(graph.router, prefix=f"{settings.API_V1_STR}", tags=["graph"])

from app.routers import feedback, application
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}", tags=["feedback"])
app.include_router(application.router, prefix=f"{settings.API_V1_STR}", tags=["application"])

from app.routers import calendar as calendar_router
app.include_router(calendar_router.router, prefix=f"{settings.API_V1_STR}", tags=["calendar"])

from app.routers import incubation
app.include_router(incubation.router, prefix=f"{settings.API_V1_STR}", tags=["incubation"])

from app.routers import intelligence
app.include_router(intelligence.router, prefix=f"{settings.API_V1_STR}/intelligence", tags=["intelligence"])

app.include_router(marketplace.router, prefix=f"{settings.API_V1_STR}", tags=["marketplace"])

from app.routers import challenge_exchange
app.include_router(challenge_exchange.router, prefix=f"{settings.API_V1_STR}", tags=["challenge_exchange"])

from app.routers import federation
app.include_router(federation.router, prefix=f"{settings.API_V1_STR}", tags=["federation"])
from app.routers import research
app.include_router(research.router, prefix=f"{settings.API_V1_STR}", tags=["research"])

from app.routers import sso
app.include_router(sso.router, prefix=f"{settings.API_V1_STR}/sso", tags=["sso"])

from app.routers import scim
app.include_router(scim.router, prefix=f"{settings.API_V1_STR}/scim/v2", tags=["scim"])

from app.routers import hackathon_sync
app.include_router(hackathon_sync.router, prefix=f"{settings.API_V1_STR}/hackathon-sync", tags=["hackathon-sync"])

from app.routers import events
app.include_router(events.router, prefix=f"{settings.API_V1_STR}/workspaces/{{workspace_id}}/events", tags=["events"])

from app.routers import health
app.include_router(health.router, prefix="/api/ops", tags=["ops"])

from app.routers import api_keys
from app.routers import verification
from app.routers import matchmaking
from app.routers import cross_portfolio
from app.routers import copilot
from app.routers import forecasting
from app.routers import impact
from app.routers import observatory
from app.routers import federation
from app.routers import developer
from app.routers import governance
from app.routers import network
from app.routers.public_api_v1 import hackathons as public_hackathons
from app.routers.public_api_v1 import data_exchange
app.include_router(api_keys.router, prefix=f"{settings.API_V1_STR}", tags=["api_keys"])
app.include_router(data_exchange.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")
app.include_router(matchmaking.router, prefix="/api/v1")
app.include_router(cross_portfolio.router, prefix="/api/v1")
app.include_router(copilot.router, prefix="/api/v1")
app.include_router(forecasting.router, prefix="/api/v1")
app.include_router(impact.router, prefix="/api/v1")
app.include_router(observatory.router, prefix="/api/v1")
from fastapi import FastAPI, Depends
import logging
import json
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

from app.config import settings
from app.database import get_db
from app.core.graph_events import register_graph_events

# Register graph events
register_graph_events()

from app.exceptions import CustomException, custom_exception_handler
from app.middleware import SecurityHeadersMiddleware
from app.core.event_bus import event_bus
from app.plugins.plugin_manager import plugin_manager
from app.services.integration_dispatcher import register_integration_dispatcher
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components
    logger.info("Initializing plugins and event bus...")
    plugin_manager.discover_plugins("app.plugins.installed")
    plugin_manager.initialize_plugins(event_bus)
    register_integration_dispatcher()
    yield
    # Cleanup on shutdown
    pass

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

from app.limiter import limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.middleware import GlobalScaleMiddleware
app.add_middleware(GlobalScaleMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

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

from app.routers import auth, users, workspaces, hackathons, dashboard, invitations, teams, projects, kanban, activity, rounds, submissions, notifications, mentors, judges, evaluations, outcomes, search, analytics, export_import, portfolio, automation, integration, ai, hub_integrations, audit, webhook, graph, opportunities, marketplace
from app.routers import verification

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(workspaces.router, prefix=f"{settings.API_V1_STR}", tags=["workspaces"])
app.include_router(verification.router, prefix=f"{settings.API_V1_STR}", tags=["Verification"])
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
app.include_router(hub_integrations.router, prefix=f"{settings.API_V1_STR}", tags=["hub_integrations"])
app.include_router(mentors.router, prefix=f"{settings.API_V1_STR}", tags=["mentors"])
app.include_router(judges.router, prefix=f"{settings.API_V1_STR}", tags=["judges"])
app.include_router(evaluations.router, prefix=f"{settings.API_V1_STR}", tags=["evaluations"])
app.include_router(outcomes.router, prefix=f"{settings.API_V1_STR}", tags=["outcomes"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}", tags=["search"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}", tags=["analytics"])
app.include_router(export_import.router, prefix=f"{settings.API_V1_STR}", tags=["export_import"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}", tags=["portfolio"])
app.include_router(automation.router, prefix=f"{settings.API_V1_STR}", tags=["automation"])
app.include_router(integration.router, prefix=f"{settings.API_V1_STR}", tags=["integration"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}", tags=["ai_intelligence"])
app.include_router(opportunities.router, prefix=f"{settings.API_V1_STR}", tags=["opportunities"])
from app.routers import matching
app.include_router(matching.router, prefix=f"{settings.API_V1_STR}", tags=["matching"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}", tags=["audit"])
app.include_router(webhook.router, prefix=f"{settings.API_V1_STR}", tags=["webhook"])

from app.routers import api_keys
app.include_router(api_keys.router, prefix=f"{settings.API_V1_STR}", tags=["api_keys"])
app.include_router(graph.router, prefix=f"{settings.API_V1_STR}", tags=["graph"])

from app.routers import feedback, application
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}", tags=["feedback"])
app.include_router(application.router, prefix=f"{settings.API_V1_STR}", tags=["application"])

from app.routers import calendar as calendar_router
app.include_router(calendar_router.router, prefix=f"{settings.API_V1_STR}", tags=["calendar"])

from app.routers import incubation
app.include_router(incubation.router, prefix=f"{settings.API_V1_STR}", tags=["incubation"])

from app.routers import intelligence
app.include_router(intelligence.router, prefix=f"{settings.API_V1_STR}/intelligence", tags=["intelligence"])

app.include_router(marketplace.router, prefix=f"{settings.API_V1_STR}", tags=["marketplace"])

from app.routers import challenge_exchange
app.include_router(challenge_exchange.router, prefix=f"{settings.API_V1_STR}", tags=["challenge_exchange"])

from app.routers import federation
app.include_router(federation.router, prefix=f"{settings.API_V1_STR}", tags=["federation"])
from app.routers import research
app.include_router(research.router, prefix=f"{settings.API_V1_STR}", tags=["research"])

from app.routers import sso
app.include_router(sso.router, prefix=f"{settings.API_V1_STR}/sso", tags=["sso"])

from app.routers import scim
app.include_router(scim.router, prefix=f"{settings.API_V1_STR}/scim/v2", tags=["scim"])

from app.routers import hackathon_sync
app.include_router(hackathon_sync.router, prefix=f"{settings.API_V1_STR}/hackathon-sync", tags=["hackathon-sync"])

from app.routers import events
app.include_router(events.router, prefix=f"{settings.API_V1_STR}/workspaces/{{workspace_id}}/events", tags=["events"])

from app.routers import health
app.include_router(health.router, prefix="/api/ops", tags=["ops"])

from app.routers import api_keys
from app.routers import verification
from app.routers import matchmaking
from app.routers import cross_portfolio
from app.routers import copilot
from app.routers import forecasting
from app.routers import impact
from app.routers import observatory
from app.routers import federation
from app.routers import developer
from app.routers import governance
from app.routers import network
from app.routers import portable_identity
from app.routers import trust_verification
from app.routers import financing
from app.routers import autonomous_network
from app.routers.public_api_v1 import hackathons as public_hackathons
from app.routers.public_api_v1 import data_exchange
app.include_router(api_keys.router, prefix=f"{settings.API_V1_STR}", tags=["api_keys"])
app.include_router(data_exchange.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")
app.include_router(matchmaking.router, prefix="/api/v1")
app.include_router(cross_portfolio.router, prefix="/api/v1")
app.include_router(copilot.router, prefix="/api/v1")
app.include_router(forecasting.router, prefix="/api/v1")
app.include_router(impact.router, prefix="/api/v1")
app.include_router(observatory.router, prefix="/api/v1")
from app.routers import organization_federation, innovation_protocol
app.include_router(federation.router, prefix="/api/v1")
app.include_router(organization_federation.router, prefix=f"{settings.API_V1_STR}")
app.include_router(innovation_protocol.router)
app.include_router(developer.router, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")
app.include_router(network.router, prefix="/api/v1")
app.include_router(portable_identity.router, prefix="/api/v1")
app.include_router(trust_verification.router, prefix="/api/v1")
app.include_router(financing.router, prefix="/api/v1")
app.include_router(autonomous_network.router, prefix="/api/v1")

from app.routers import ontology, agents, approvals, memory
app.include_router(ontology.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")

# Include the Public API router
app.include_router(public_hackathons.router, prefix="/api", tags=["public_api"])
