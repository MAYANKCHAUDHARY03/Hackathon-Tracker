from datetime import timezone
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace
from app.models.user import User, WorkspaceMembership
from app.models.hackathon import Hackathon
from app.models.team import Team
from app.config import settings
from jose import jwt
import datetime

def create_access_token(user_id: uuid.UUID):
    to_encode = {"sub": str(user_id)}
    expire = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

@pytest.mark.asyncio
async def test_cross_tenant_team_creation(
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    # Setup User
    user_a = User(email="usera@example.com", password_hash="pw", full_name="User A", is_active=True)
    db_session.add(user_a)
    await db_session.flush()

    headers_a = {"Authorization": f"Bearer {create_access_token(user_a.id)}"}

    # Setup: Create Workspace A (belongs to user_a)
    ws_a = Workspace(name="Workspace A", slug="workspace-a")
    db_session.add(ws_a)
    await db_session.flush()
    mem_a = WorkspaceMembership(workspace_id=ws_a.id, user_id=user_a.id, role="admin")
    db_session.add(mem_a)
    
    # Setup: Create Workspace B (does NOT belong to user_a)
    ws_b = Workspace(name="Workspace B", slug="workspace-b")
    db_session.add(ws_b)
    await db_session.flush()
    
    # Create Hackathon in Workspace B
    hack_b = Hackathon(workspace_id=ws_b.id, name="Hackathon B", mode="online", status="active", registration_deadline=datetime.datetime.now(timezone.utc), start_date=datetime.datetime.now(timezone.utc), end_date=datetime.datetime.now(timezone.utc))
    db_session.add(hack_b)
    await db_session.commit()
    
    # Attempt: user_a (in ws A) creates a team in ws A, but points to hack_b
    response = await async_client.post(
        f"/api/v1/workspaces/{ws_a.id}/teams",
        headers=headers_a,
        json={
            "name": "Cross Tenant Team",
            "hackathon_id": str(hack_b.id),
            "description": "Malicious"
        }
    )
    
    # This SHOULD be 404, 403, or 422 but due to IDOR, it might be 200
    assert response.status_code in [403, 404, 400, 422], f"VULNERABILITY CONFIRMED: Allowed cross-tenant team creation! Status: {response.status_code}"

@pytest.mark.asyncio
async def test_cross_tenant_project_creation(
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    # Setup User
    user_a = User(email="usera2@example.com", password_hash="pw", full_name="User A2", is_active=True)
    db_session.add(user_a)
    await db_session.flush()

    headers_a = {"Authorization": f"Bearer {create_access_token(user_a.id)}"}

    # Setup: Create Workspace A
    ws_a = Workspace(name="Workspace A2", slug="workspace-a2")
    db_session.add(ws_a)
    await db_session.flush()
    mem_a = WorkspaceMembership(workspace_id=ws_a.id, user_id=user_a.id, role="admin")
    db_session.add(mem_a)
    
    # Setup: Create Workspace B (No access)
    ws_b = Workspace(name="Workspace B2", slug="workspace-b2")
    db_session.add(ws_b)
    await db_session.flush()
    
    # Hackathon and Team in Workspace B
    hack_b = Hackathon(workspace_id=ws_b.id, name="Hackathon B2", mode="online", status="active", registration_deadline=datetime.datetime.now(timezone.utc), start_date=datetime.datetime.now(timezone.utc), end_date=datetime.datetime.now(timezone.utc))
    db_session.add(hack_b)
    await db_session.flush()
    team_b = Team(workspace_id=ws_b.id, hackathon_id=hack_b.id, name="Team B2", slug="team-b2", status="active")
    db_session.add(team_b)
    await db_session.commit()
    
    # Attempt: user_a creates a project in ws A, but points to team_b (in ws B)
    response = await async_client.post(
        f"/api/v1/workspaces/{ws_a.id}/teams/{team_b.id}/projects",
        headers=headers_a,
        json={
            "name": "Cross Tenant Project",
            "description": "Malicious",
            "hackathon_id": str(hack_b.id)
        }
    )
    
    assert response.status_code in [403, 404, 400, 422], f"VULNERABILITY CONFIRMED: Allowed cross-tenant project creation! Status: {response.status_code}"
