import httpx
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.calendar_integration import CalendarIntegration

async def push_event_to_google(integration: CalendarIntegration, event_data: Dict[str, Any]) -> str:
    # Requires valid access token. For production, token refresh logic goes here.
    from app.security_vault import decrypt_string
    
    calendar_id = integration.remote_calendar_id or "primary"
    token = decrypt_string(integration.access_token) if integration.access_token else ""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    
    payload = {
        "summary": event_data.get("title"),
        "description": event_data.get("description", ""),
        "start": {
            "dateTime": event_data.get("start_time").isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": event_data.get("end_time").isoformat(),
            "timeZone": "UTC"
        }
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Calendar token expired")
        elif not response.is_success:
            raise HTTPException(status_code=502, detail=f"Google Calendar Error: {response.text}")
            
        data = response.json()
        return data.get("id")

async def push_event_to_outlook(integration: CalendarIntegration, event_data: Dict[str, Any]) -> str:
    from app.security_vault import decrypt_string
    token = decrypt_string(integration.access_token) if integration.access_token else ""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = "https://graph.microsoft.com/v1.0/me/events"
    
    payload = {
        "subject": event_data.get("title"),
        "body": {
            "contentType": "HTML",
            "content": event_data.get("description", "")
        },
        "start": {
            "dateTime": event_data.get("start_time").isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": event_data.get("end_time").isoformat(),
            "timeZone": "UTC"
        }
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Calendar token expired")
        elif not response.is_success:
            raise HTTPException(status_code=502, detail=f"Outlook Calendar Error: {response.text}")
            
        data = response.json()
        return data.get("id")

async def sync_hackathon_to_calendars(db: AsyncSession, workspace_id: str, event_data: Dict[str, Any]):
    from sqlalchemy import select
    stmt = select(CalendarIntegration).where(
        CalendarIntegration.workspace_id == workspace_id,
        CalendarIntegration.is_active == True
    )
    integrations = (await db.execute(stmt)).scalars().all()
    
    results = []
    for integration in integrations:
        try:
            if integration.provider == 'google':
                ext_id = await push_event_to_google(integration, event_data)
                results.append({"provider": "google", "status": "success", "id": ext_id})
            elif integration.provider == 'outlook':
                ext_id = await push_event_to_outlook(integration, event_data)
                results.append({"provider": "outlook", "status": "success", "id": ext_id})
        except Exception as e:
            results.append({"provider": integration.provider, "status": "error", "message": str(e)})
            
    return results
