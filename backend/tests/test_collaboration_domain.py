import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.workspace import Workspace
from app.models.user import User
from app.models.hackathon import Hackathon
from app.models.workspace_invitation import WorkspaceInvitation
from app.models.team import Team, TeamMember
from app.models.project import Project, Technology, ProjectTechnology

@pytest.fixture
async def seed_data(prepare_database, async_client):
    from app.database import get_db
    from app.main import app
    
    # We will just yield a clean session and insert objects inside tests.
    pass

async def test_team_creation(async_client):
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as db:
        user = User(id=uuid.uuid4(), full_name="Test User", email="test@test.com", password_hash="hash")
        workspace = Workspace(id=uuid.uuid4(), name="Test WS", slug="test-ws")
        hackathon = Hackathon(
            id=uuid.uuid4(), workspace_id=workspace.id, name="Hackathon", 
            registration_deadline=datetime.now(timezone.utc),
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        db.add_all([user, workspace, hackathon])
        await db.commit()

        team = Team(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            hackathon_id=hackathon.id,
            name="Team A",
            slug="team-a",
            created_by=user.id
        )
        db.add(team)
        await db.commit()

        team_member = TeamMember(
            id=uuid.uuid4(),
            team_id=team.id,
            user_id=user.id,
            authorization_role="lead"
        )
        db.add(team_member)
        await db.commit()

        assert team.id is not None
        assert team_member.id is not None

async def test_duplicate_team_name_per_hackathon(async_client):
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as db:
        workspace = Workspace(id=uuid.uuid4(), name="Test WS 2", slug="test-ws-2")
        hackathon = Hackathon(
            id=uuid.uuid4(), workspace_id=workspace.id, name="Hackathon 2", 
            registration_deadline=datetime.now(timezone.utc),
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        db.add_all([workspace, hackathon])
        await db.commit()

        team1 = Team(id=uuid.uuid4(), workspace_id=workspace.id, hackathon_id=hackathon.id, name="Team B", slug="team-b")
        team2 = Team(id=uuid.uuid4(), workspace_id=workspace.id, hackathon_id=hackathon.id, name="Team B", slug="team-c")
        db.add(team1)
        await db.commit()

        db.add(team2)
        with pytest.raises(IntegrityError):
            await db.commit()

async def test_project_creation_and_technologies(async_client):
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as db:
        workspace = Workspace(id=uuid.uuid4(), name="Test WS", slug="test-ws-3")
        hackathon = Hackathon(
            id=uuid.uuid4(), workspace_id=workspace.id, name="Hackathon", 
            registration_deadline=datetime.now(timezone.utc),
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        team = Team(id=uuid.uuid4(), workspace_id=workspace.id, hackathon_id=hackathon.id, name="Team P", slug="team-p")
        db.add_all([workspace, hackathon, team])
        await db.commit()

        project = Project(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            hackathon_id=hackathon.id,
            team_id=team.id,
            title="Cool Project",
            slug="cool-project"
        )
        db.add(project)
        await db.commit()

        tech = Technology(id=uuid.uuid4(), name="Python", slug="python", category="language")
        db.add(tech)
        await db.commit()

        pt = ProjectTechnology(id=uuid.uuid4(), project_id=project.id, technology_id=tech.id)
        db.add(pt)
        await db.commit()

        assert project.id is not None

async def test_one_project_per_team(async_client):
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as db:
        workspace = Workspace(id=uuid.uuid4(), name="Test WS", slug="test-ws-4")
        hackathon = Hackathon(
            id=uuid.uuid4(), workspace_id=workspace.id, name="Hackathon", 
            registration_deadline=datetime.now(timezone.utc),
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        team = Team(id=uuid.uuid4(), workspace_id=workspace.id, hackathon_id=hackathon.id, name="Team PP", slug="team-pp")
        db.add_all([workspace, hackathon, team])
        await db.commit()

        project1 = Project(id=uuid.uuid4(), workspace_id=workspace.id, hackathon_id=hackathon.id, team_id=team.id, title="Proj 1", slug="proj-1")
        db.add(project1)
        await db.commit()

        project2 = Project(id=uuid.uuid4(), workspace_id=workspace.id, hackathon_id=hackathon.id, team_id=team.id, title="Proj 2", slug="proj-2")
        db.add(project2)
        with pytest.raises(IntegrityError):
            await db.commit()
