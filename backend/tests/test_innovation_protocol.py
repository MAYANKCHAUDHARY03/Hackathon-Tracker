import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.innovation_protocol import (
    InnovationEvent,
    InnovationProject,
    InnovationPerson,
    InnovationObjectBase
)

def test_innovation_event_validates():
    event = InnovationEvent(
        id="evt_123",
        source="system_a",
        owner="org_1",
        name="Global Hackathon",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow(),
        status="active"
    )
    assert event.type == "InnovationEvent"
    assert event.version == "1.0"
    assert event.visibility == "public"

def test_innovation_event_requires_base_fields():
    with pytest.raises(ValidationError) as exc:
        InnovationEvent(
            name="Missing Base Fields",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),
            status="active"
        )
    assert "id" in str(exc.value)
    assert "source" in str(exc.value)
    assert "owner" in str(exc.value)

def test_innovation_project_validates():
    project = InnovationProject(
        id="proj_456",
        source="system_a",
        owner="team_1",
        title="AI Solution",
        status="completed"
    )
    assert project.type == "InnovationProject"

@pytest.mark.asyncio
async def test_export_endpoint(async_client):
    response = await async_client.get("/api/v1/protocol/export")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "source_system" in data
    assert "objects" in data
    assert isinstance(data["objects"], list)

@pytest.mark.asyncio
async def test_validate_endpoint(async_client):
    payload = {
        "version": "1.0",
        "source_system": "external_test",
        "objects": [
            {
                "id": "ext_evt_1",
                "type": "InnovationEvent",
                "source": "external_test",
                "owner": "ext_org_1",
                "name": "External Event",
                "start_date": "2026-08-19T00:00:00Z",
                "end_date": "2026-08-20T00:00:00Z",
                "status": "active"
            }
        ]
    }
    response = await async_client.post("/api/v1/protocol/validate", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "valid", "object_count": 1}
