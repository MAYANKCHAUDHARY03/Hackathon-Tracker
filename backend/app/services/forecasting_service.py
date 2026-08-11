from uuid import UUID
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.hackathon import Hackathon
from app.models.forecast import Forecast
from app.schemas.forecast import ForecastResponse
from app.services.ai import AIProviderFactory
from app.config import settings

class ForecastingService:
    @staticmethod
    async def generate_project_forecast(
        workspace_id: UUID, 
        project_id: UUID, 
        db: AsyncSession
    ) -> ForecastResponse:
        
        # 1. Fetch Project
        query = select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id
        )
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise ValueError("Project not found")

        # 2. Initialize AI Provider
        if settings.GEMINI_API_KEY:
            provider = AIProviderFactory.get_provider("gemini", settings.GEMINI_API_KEY)
        else:
            provider = AIProviderFactory.get_provider("mock", "dummy_key")

        # 3. Generate Forecast
        target_data = {
            "title": project.title,
            "description": project.description,
            "status": project.status
        }
        
        ai_result = await provider.generate_forecast("project", target_data, [])
        
        # 4. Save to DB
        forecast = Forecast(
            workspace_id=workspace_id,
            target_type="project",
            target_id=project.id,
            forecast_type="success_probability",
            prediction=ai_result.get("prediction", {}),
            confidence=ai_result.get("confidence", 0.0),
            is_prediction=True, # Explicitly labeled as prediction
            factors=ai_result.get("factors", [])
        )
        db.add(forecast)
        await db.commit()
        await db.refresh(forecast)
        
        return ForecastResponse.model_validate(forecast)
