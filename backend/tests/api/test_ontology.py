import pytest
import uuid
from httpx import AsyncClient
from app.main import app
from app.models.ontology import UniversalEntity, EntityType, VerificationLevel, VisibilityLevel
from app.models.problem import Problem
from app.models.base import Base
from sqlalchemy import select
from tests.conftest import TestingSessionLocal

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def workspace_id():
    return uuid.uuid4()

@pytest.fixture
def user_id():
    return uuid.uuid4()

@pytest.mark.asyncio
async def test_ontology_polymorphism(db_session, workspace_id, user_id):
    # Test creating a Problem through UniversalEntity hierarchy
    problem = Problem(
        workspace_id=workspace_id,
        owner_id=user_id,
        properties={
            "title": "Test Ontology Problem",
            "slug": "test-ontology-problem",
            "description": "This problem is stored in ontology_entities",
            "domain": "Climate",
            "status": "open"
        }
    )
    
    db_session.add(problem)
    await db_session.commit()
    
    # Query via UniversalEntity
    stmt = select(UniversalEntity).where(UniversalEntity.workspace_id == workspace_id, UniversalEntity.entity_type == EntityType.PROBLEM)
    result = await db_session.execute(stmt)
    entities = result.scalars().all()
    
    assert len(entities) == 1
    entity = entities[0]
    
    # Assert polymorphic loading
    assert isinstance(entity, Problem)
    assert entity.entity_type == EntityType.PROBLEM
    assert entity.title == "Test Ontology Problem"
    assert entity.slug == "test-ontology-problem"
    assert entity.properties["domain"] == "Climate"
    
    # Test hybrid property expressions
    stmt2 = select(Problem).where(Problem.domain == "Climate")
    res2 = await db_session.execute(stmt2)
    filtered_problems = res2.scalars().all()
    
    assert len(filtered_problems) == 1
    assert filtered_problems[0].id == problem.id
