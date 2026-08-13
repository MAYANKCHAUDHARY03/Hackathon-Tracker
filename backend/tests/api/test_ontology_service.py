import pytest
import uuid
from httpx import AsyncClient
from app.main import app
from app.models.ontology import EntityType

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# We might need to mock get_current_user and verify_workspace_access for this API test, or just test the service directly.
# Let's test the OntologyService directly.
from app.services.ontology_service import OntologyService
from app.schemas.ontology import UniversalEntityCreate, UniversalEntityUpdate
from tests.conftest import TestingSessionLocal

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.mark.asyncio
async def test_ontology_service_crud(db_session):
    workspace_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    service = OntologyService(db_session)
    
    # Create Startup
    create_data = UniversalEntityCreate(
        entity_type=EntityType.STARTUP,
        owner_id=owner_id,
        properties={"name": "Test Startup", "industry": "AI"}
    )
    startup = await service.create_entity(workspace_id, EntityType.STARTUP, create_data)
    
    assert startup.id is not None
    assert startup.entity_type == EntityType.STARTUP
    assert startup.properties["name"] == "Test Startup"
    
    # Get Startup
    fetched = await service.get_entity(workspace_id, EntityType.STARTUP, startup.id)
    assert fetched.id == startup.id
    
    # List Startups
    startups = await service.list_entities(workspace_id, EntityType.STARTUP)
    assert len(startups) >= 1
    
    # Update Startup
    update_data = UniversalEntityUpdate(properties={"name": "Test Startup V2", "industry": "AI"})
    updated = await service.update_entity(workspace_id, EntityType.STARTUP, startup.id, update_data)
    assert updated.properties["name"] == "Test Startup V2"
