import asyncio
from app.models import Base
from app.models.event import PlatformEvent

print(Base.metadata.tables.keys())
