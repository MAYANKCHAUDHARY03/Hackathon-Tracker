import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import get_db, get_db_ro
from app.models import Base
from app.models.user import User
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon
from app.models.team import Team, TeamMember
from app.models.project import Project, Technology, ProjectTechnology
from app.models.workspace_invitation import WorkspaceInvitation
from app.models.event import PlatformEvent
from app.models.memory import AgentMemory
from sqlalchemy.pool import StaticPool

import tempfile
import os
import uuid

@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_session_maker(test_engine):
    return async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=test_engine, class_=AsyncSession)

@pytest.fixture
async def db_session(test_session_maker):
    async with test_session_maker() as session:
        yield session

@pytest.fixture(autouse=True)
def override_dependencies(test_session_maker):
    async def _override_get_db():
        async with test_session_maker() as session:
            yield session
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_db_ro] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True, scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

from app.limiter import limiter
limiter.enabled = False

