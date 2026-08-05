import uuid
from typing import Sequence
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.notification import Notification, NotificationPreference, NotificationCategory, NotificationSeverity

async def get_notifications(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    category: str | None = None,
    severity: str | None = None,
    is_read: bool | None = None,
    skip: int = 0,
    limit: int = 20
):
    query = select(Notification).where(
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id,
        Notification.dismissed_at.is_(None)
    )

    if category:
        query = query.where(Notification.category == category)
    if severity:
        query = query.where(Notification.severity == severity)
    if is_read is not None:
        if is_read:
            query = query.where(Notification.read_at.is_not(None))
        else:
            query = query.where(Notification.read_at.is_(None))

    query = query.order_by(Notification.occurred_at.desc())

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Unread Count
    unread_query = select(func.count()).select_from(query.where(Notification.read_at.is_(None)).subquery())
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar() or 0

    # Items
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total, unread_count

async def get_unread_count(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID
) -> int:
    query = select(func.count()).select_from(Notification).where(
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id,
        Notification.read_at.is_(None),
        Notification.dismissed_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar() or 0

async def get_notification_summary(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID
):
    # Base query for unread
    query = select(Notification.category, func.count(Notification.id)).where(
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id,
        Notification.read_at.is_(None),
        Notification.dismissed_at.is_(None)
    ).group_by(Notification.category)
    
    result = await db.execute(query)
    rows = result.all()
    
    unread_by_category = {row[0].value: row[1] for row in rows}
    total_unread = sum(unread_by_category.values())
    
    # Total count
    total_query = select(func.count(Notification.id)).where(
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id,
        Notification.dismissed_at.is_(None)
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return {
        "total_unread": total_unread,
        "unread_by_category": unread_by_category,
        "total": total
    }

async def mark_read(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    notification_id: uuid.UUID
) -> Notification | None:
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id
    )
    result = await db.execute(query)
    notification = result.scalars().first()
    
    if notification and not notification.read_at:
        notification.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(notification)
        
    return notification

async def mark_all_read(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID
):
    stmt = update(Notification).where(
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id,
        Notification.read_at.is_(None)
    ).values(read_at=datetime.now(timezone.utc))
    
    await db.execute(stmt)
    await db.commit()

async def dismiss(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    notification_id: uuid.UUID
) -> Notification | None:
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.workspace_id == workspace_id,
        Notification.recipient_user_id == user_id
    )
    result = await db.execute(query)
    notification = result.scalars().first()
    
    if notification and not notification.dismissed_at:
        notification.dismissed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(notification)
        
    return notification
