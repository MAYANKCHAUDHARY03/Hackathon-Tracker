from app.config import settings
from app.main import app

def test_app_startup():
    assert app.title == settings.PROJECT_NAME
    assert app.openapi_url == f"{settings.API_V1_STR}/openapi.json"
