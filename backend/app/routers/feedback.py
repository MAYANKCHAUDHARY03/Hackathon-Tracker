from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    *,
    db: AsyncSession = Depends(get_db),
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new feedback entry.
    """
    feedback = Feedback(
        type=feedback_in.type.value,
        description=feedback_in.description,
        url=feedback_in.url,
        user_id=current_user.id if current_user else None
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback

@router.get("/feedback", response_model=List[FeedbackResponse])
async def read_feedback(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve feedback entries. (Open to authenticated users for now)
    """
    query = select(Feedback).offset(skip).limit(limit)
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    return feedbacks
