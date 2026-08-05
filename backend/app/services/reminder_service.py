import uuid
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.kanban import Task, TaskAssignee
from app.models.round import HackathonRound, Deadline
from app.models.notification import Notification, NotificationCategory, NotificationSeverity
from app.models.user import WorkspaceMembership

logger = logging.getLogger(__name__)

async def _create_notification_if_not_exists(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    event_key: str,
    title: str,
    body: str,
    category: NotificationCategory,
    severity: NotificationSeverity,
    entity_type: str,
    entity_id: uuid.UUID
):
    # Check if exists
    query = select(Notification).where(Notification.event_key == event_key)
    result = await db.execute(query)
    if result.scalars().first():
        return # Already sent

    notification = Notification(
        workspace_id=workspace_id,
        recipient_user_id=user_id,
        notification_type="reminder",
        category=category,
        severity=severity,
        title=title,
        body=body,
        entity_type=entity_type,
        entity_id=entity_id,
        event_key=event_key,
        occurred_at=datetime.now(timezone.utc)
    )
    db.add(notification)

async def generate_task_reminders(db: AsyncSession, workspace_id: uuid.UUID):
    now = datetime.now(timezone.utc)
    in_24_hours = now + timedelta(hours=24)

    # Find tasks due in the next 24 hours
    query = select(Task, TaskAssignee).join(
        TaskAssignee, Task.id == TaskAssignee.task_id
    ).where(
        Task.due_date.is_not(None),
        Task.due_date <= in_24_hours,
        Task.due_date > now
    )
    
    result = await db.execute(query)
    rows = result.all()

    for task, assignee in rows:
        event_key = f"task_{task.id}_reminder_24h_{assignee.user_id}"
        await _create_notification_if_not_exists(
            db=db,
            workspace_id=workspace_id,
            user_id=assignee.user_id,
            event_key=event_key,
            title=f"Task Due Soon: {task.title}",
            body=f"Your task is due on {task.due_date.strftime('%Y-%m-%d %H:%M')}.",
            category=NotificationCategory.task,
            severity=NotificationSeverity.warning,
            entity_type="task",
            entity_id=task.id
        )
        
    await db.commit()

async def generate_round_reminders(db: AsyncSession, workspace_id: uuid.UUID):
    now = datetime.now(timezone.utc)
    in_24_hours = now + timedelta(hours=24)

    # Find rounds ending in next 24 hours
    query = select(HackathonRound).where(
        HackathonRound.end_date.is_not(None),
        HackathonRound.end_date <= in_24_hours,
        HackathonRound.end_date > now
    )
    
    result = await db.execute(query)
    rounds = result.scalars().all()

    if not rounds:
        return

    # Notify all workspace members for now (or team members depending on rules)
    member_query = select(WorkspaceMembership).where(WorkspaceMembership.workspace_id == workspace_id)
    member_result = await db.execute(member_query)
    members = member_result.scalars().all()

    for rnd in rounds:
        for member in members:
            event_key = f"round_{rnd.id}_reminder_24h_{member.user_id}"
            await _create_notification_if_not_exists(
                db=db,
                workspace_id=workspace_id,
                user_id=member.user_id,
                event_key=event_key,
                title=f"Round Ending Soon: {rnd.title}",
                body=f"The round '{rnd.title}' ends on {rnd.end_date.strftime('%Y-%m-%d %H:%M')}.",
                category=NotificationCategory.round,
                severity=NotificationSeverity.warning,
                entity_type="round",
                entity_id=rnd.id
            )
            
    await db.commit()

async def run_reminder_engine(db: AsyncSession, workspace_id: uuid.UUID):
    await generate_task_reminders(db, workspace_id)
    await generate_round_reminders(db, workspace_id)
