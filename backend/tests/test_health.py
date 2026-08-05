# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from httpx import AsyncClient
from app.config import settings

@pytest.mark.asyncio
async def test_health_check_no_db(async_client: AsyncClient):
    # To test health endpoint without DB dependency, we should mock the DB session
    # but since it's an end-to-end endpoint test, we can just call it and expect 
    # it to return 200 even if the DB connection fails (it should return status="degraded")
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["environment"] == settings.ENVIRONMENT
    assert data["api_version"] == settings.API_V1_STR
