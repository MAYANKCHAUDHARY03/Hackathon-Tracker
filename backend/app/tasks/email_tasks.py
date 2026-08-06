from typing import Dict, Any, List
from app.worker import celery_app
import time

@celery_app.task(bind=True, max_retries=3)
def send_email_async(self, recipient: str, subject: str, body: str):
    """
    Mock task for sending emails asynchronously.
    """
    try:
        # Simulate email sending delay
        time.sleep(2)
        print(f"Email sent to {recipient} - Subject: {subject}")
        return {"status": "success", "recipient": recipient}
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery_app.task(bind=True)
def sync_calendar_event_async(self, workspace_id: str, event_data: Dict[str, Any]):
    """
    Background job to sync calendar events across integrations.
    """
    import asyncio
    from app.database import async_session_maker
    from app.services.calendar_service import sync_hackathon_to_calendars
    
    async def run_sync():
        async with async_session_maker() as db:
            return await sync_hackathon_to_calendars(db, workspace_id, event_data)
            
    try:
        # Run async function in sync context of celery worker
        # Better approach is to use Celery with asyncio support or run loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_sync())
        return {"status": "success", "result": result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
